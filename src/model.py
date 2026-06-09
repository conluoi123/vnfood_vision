"""
model.py — VNFood Vision
Hỗ trợ: EfficientNet-B3 | ResNet50 | MobileNetV3-Large
Tích hợp: Focal Loss, Label Smoothing, Class Weights
"""
import json
import math
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


# ─────────────────────────────────────────────
# 1. FOCAL LOSS
# ─────────────────────────────────────────────
class FocalLoss(nn.Module):
    """
    Focal Loss: giảm ảnh hưởng của ảnh dễ nhận diện,
    tập trung vào các class khó / thiểu số.
    Tham khảo: https://arxiv.org/abs/1708.02002
    """
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0,
                 class_weights: torch.Tensor = None,
                 label_smoothing: float = 0.1,
                 num_classes: int = None):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.class_weights = class_weights
        self.label_smoothing = label_smoothing
        self.num_classes = num_classes

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        # Label smoothing
        if self.label_smoothing > 0 and self.num_classes:
            smooth_val = self.label_smoothing / self.num_classes
            one_hot = torch.zeros_like(logits).scatter_(1, targets.unsqueeze(1), 1)
            one_hot = one_hot * (1 - self.label_smoothing) + smooth_val
            log_prob = F.log_softmax(logits, dim=1)
            ce_loss = -(one_hot * log_prob).sum(dim=1)
        else:
            ce_loss = F.cross_entropy(logits, targets,
                                      weight=self.class_weights,
                                      reduction='none')

        # Focal weight
        prob = torch.exp(-ce_loss)
        focal_weight = self.alpha * (1 - prob) ** self.gamma
        loss = focal_weight * ce_loss
        return loss.mean()


# ─────────────────────────────────────────────
# 2. MODEL FACTORY
# ─────────────────────────────────────────────
class VNFoodModel(nn.Module):
    """
    Wrapper model linh hoạt — thay backbone qua config.
    """
    def __init__(self, backbone_name: str, num_classes: int,
                 pretrained: bool = True, dropout: float = 0.3):
        super().__init__()
        self.backbone_name = backbone_name
        self.num_classes = num_classes

        if backbone_name == "efficientnet_b3":
            weights = models.EfficientNet_B3_Weights.DEFAULT if pretrained else None
            base = models.efficientnet_b3(weights=weights)
            in_features = base.classifier[1].in_features
            base.classifier = nn.Sequential(
                nn.Dropout(p=dropout),
                nn.Linear(in_features, num_classes)
            )
            self.model = base

        elif backbone_name == "resnet50":
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            base = models.resnet50(weights=weights)
            in_features = base.fc.in_features
            base.fc = nn.Sequential(
                nn.Dropout(p=dropout),
                nn.Linear(in_features, num_classes)
            )
            self.model = base

        elif backbone_name == "mobilenet_v3_large":
            weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
            base = models.mobilenet_v3_large(weights=weights)
            in_features = base.classifier[3].in_features
            base.classifier[3] = nn.Linear(in_features, num_classes)
            self.model = base

        else:
            raise ValueError(f"Backbone '{backbone_name}' chưa được hỗ trợ. "
                             "Chọn: efficientnet_b3 | resnet50 | mobilenet_v3_large")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

    def freeze_backbone(self):
        """Đóng băng toàn bộ backbone, chỉ train lớp classifier."""
        for name, param in self.model.named_parameters():
            if "classifier" not in name and "fc" not in name:
                param.requires_grad = False
        print(f"[Model] Backbone frozen. Chỉ train classifier.")

    def unfreeze_backbone(self):
        """Mở toàn bộ backbone để fine-tune."""
        for param in self.model.parameters():
            param.requires_grad = True
        print(f"[Model] Backbone unfrozen. Fine-tuning toàn bộ mạng.")


# ─────────────────────────────────────────────
# 3. UTILITY: tính class weights từ dataset
# ─────────────────────────────────────────────
def compute_class_weights(dataset, save_path: str = None) -> torch.Tensor:
    """
    Đếm số ảnh của mỗi class → tính inverse-frequency weight.
    Giúp Focal Loss tập trung vào các class ít ảnh (class mất cân bằng).
    """
    from collections import Counter
    label_counts = Counter(label for _, label in dataset.samples)
    num_classes = len(dataset.classes)
    total = sum(label_counts.values())

    weights = torch.zeros(num_classes)
    for cls_idx in range(num_classes):
        count = label_counts.get(cls_idx, 1)
        weights[cls_idx] = total / (num_classes * count)

    # Normalize về khoảng [0.1, 10]
    weights = weights / weights.mean()
    weights = weights.clamp(0.1, 10.0)

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        idx_to_class = {v: k for k, v in
                        {cls: i for i, cls in enumerate(dataset.classes)}.items()}
        weights_dict = {idx_to_class[i]: float(weights[i]) for i in range(num_classes)}
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(weights_dict, f, ensure_ascii=False, indent=2)
        print(f"[Model] Class weights saved → {save_path}")

    return weights


# ─────────────────────────────────────────────
# 4. MIXUP / CUTMIX AUGMENTATION
# ─────────────────────────────────────────────
def mixup_data(x: torch.Tensor, y: torch.Tensor, alpha: float = 0.2):
    """Mixup: trộn 2 ảnh và nhãn lại với tỉ lệ ngẫu nhiên."""
    if alpha <= 0:
        return x, y, y, 1.0
    lam = torch.distributions.Beta(alpha, alpha).sample().item()
    batch_size = x.size(0)
    index = torch.randperm(batch_size, device=x.device)
    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam


def mixup_criterion(criterion, pred, y_a, y_b, lam):
    """Loss cho Mixup."""
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)
