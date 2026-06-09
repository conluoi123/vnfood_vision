"""
train.py — VNFood Vision Training Loop

Chạy tại LOCAL (từ thư mục gốc dự án):
  python src/vision/train.py
  python src/vision/train.py --backbone resnet50

Chạy tại COLAB:
  !python src/vision/train.py --data_dir "/content/drive/MyDrive/VietFood-Project/data/processed"
"""
import argparse
import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path

import torch
import torch.optim as optim
import yaml
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, WeightedRandomSampler, random_split
from tqdm import tqdm

# Thêm project root vào path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.vision.dataset import VietnameseFoodDataset, get_transforms
from src.vision.model import FocalLoss, VNFoodModel, compute_class_weights, mixup_criterion, mixup_data


# ─────────────────────────────────────────────
# HELPER: AverageMeter
# ─────────────────────────────────────────────
class AverageMeter:
    def __init__(self): self.reset()
    def reset(self): self.val = self.avg = self.sum = self.count = 0
    def update(self, val, n=1):
        self.val = val; self.sum += val * n
        self.count += n; self.avg = self.sum / self.count


# ─────────────────────────────────────────────
# HELPER: Top-K Accuracy
# ─────────────────────────────────────────────
def topk_accuracy(output, target, topk=(1, 5)):
    with torch.no_grad():
        maxk = max(topk)
        batch_size = target.size(0)
        _, pred = output.topk(maxk, 1, True, True)
        pred = pred.t()
        correct = pred.eq(target.view(1, -1).expand_as(pred))
        res = []
        for k in topk:
            correct_k = correct[:k].reshape(-1).float().sum(0, keepdim=True)
            res.append(correct_k.mul_(100.0 / batch_size).item())
        return res


# ─────────────────────────────────────────────
# TRAIN ONE EPOCH
# ─────────────────────────────────────────────
def train_one_epoch(model, loader, criterion, optimizer, device, config, epoch):
    model.train()
    loss_meter = AverageMeter()
    acc_meter  = AverageMeter()

    mixup_alpha  = config['data']['augmentation'].get('mixup_alpha', 0.0)
    use_mixup    = mixup_alpha > 0

    pbar = tqdm(loader, desc=f"Epoch {epoch:03d} [Train]", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        if use_mixup:
            images, y_a, y_b, lam = mixup_data(images, labels, mixup_alpha)
            logits = model(images)
            loss = mixup_criterion(criterion, logits, y_a, y_b, lam)
        else:
            logits = model(images)
            loss = criterion(logits, labels)

        optimizer.zero_grad()
        loss.backward()

        # Gradient clipping
        grad_clip = config['training'].get('grad_clip', 1.0)
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)

        optimizer.step()

        acc1, _ = topk_accuracy(logits, labels, topk=(1, 5))
        loss_meter.update(loss.item(), images.size(0))
        acc_meter.update(acc1, images.size(0))
        pbar.set_postfix(loss=f"{loss_meter.avg:.4f}", acc=f"{acc_meter.avg:.2f}%")

    return loss_meter.avg, acc_meter.avg


# ─────────────────────────────────────────────
# VALIDATE
# ─────────────────────────────────────────────
@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    loss_meter = AverageMeter()
    top1_meter = AverageMeter()
    top5_meter = AverageMeter()

    for images, labels in tqdm(loader, desc="[Val]", leave=False):
        images, labels = images.to(device), labels.to(device)
        logits = model(images)
        loss = criterion(logits, labels)

        acc1, acc5 = topk_accuracy(logits, labels, topk=(1, 5))
        loss_meter.update(loss.item(), images.size(0))
        top1_meter.update(acc1, images.size(0))
        top5_meter.update(acc5, images.size(0))

    return loss_meter.avg, top1_meter.avg, top5_meter.avg


# ─────────────────────────────────────────────
# MAIN TRAINING LOOP
# ─────────────────────────────────────────────
def resolve_data_dir(config: dict, override_data_dir: str = None) -> str:
    """
    Tự động tìm đường dẫn `processed/` theo thứ tự ưu tiên:
    1. Tham số --data_dir từ CLI
    2. Biến môi trường VNFOOD_DATA_DIR
    3. processed_dir trong config.yaml (nếu không rỗng)
    4. Tự động tìm từ project root
    """
    import os

    # Ưu tiên 1: CLI argument
    if override_data_dir:
        return override_data_dir

    # Ưu tiên 2: Biến môi trường (tiện cho Colab)
    env_dir = os.environ.get("VNFOOD_DATA_DIR", "")
    if env_dir:
        return env_dir

    # Ưu tiên 3: Giá trị trong config.yaml
    cfg_dir = config['data'].get('processed_dir', '')
    if cfg_dir:
        return cfg_dir

    # Ưu tiên 4: Tự tìm từ vị trí file train.py
    project_root = Path(__file__).resolve().parents[2]
    auto_path = project_root / "data" / "processed"
    return str(auto_path)


def main(config_path: str, override_backbone: str = None, override_data_dir: str = None):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Override backbone từ CLI nếu có
    if override_backbone:
        config['model']['backbone'] = override_backbone

    # Giải quyết đường dẫn data
    config['data']['processed_dir'] = resolve_data_dir(config, override_data_dir)
    print(f"  Data dir : {config['data']['processed_dir']}")

    torch.manual_seed(config['data']['seed'])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'='*60}")
    print(f"  VNFood Vision — Training")
    print(f"  Device : {device}")
    print(f"  Backbone: {config['model']['backbone']}")
    print(f"{'='*60}\n")

    # ── Dataset & DataLoader ──────────────────
    train_transform = get_transforms(config, mode='train')
    val_transform   = get_transforms(config, mode='val')

    full_dataset = VietnameseFoodDataset(
        root_dir=config['data']['processed_dir'],
        transform=train_transform
    )

    if len(full_dataset) == 0:
        print("⚠️  Dataset trống! Kiểm tra lại đường dẫn 'processed_dir' trong config.yaml")
        print("   Đang tạo dataset giả để test pipeline...")
        # Dummy fallback
        from torch.utils.data import TensorDataset
        num_classes = 10
        dummy = TensorDataset(
            torch.randn(100, 3, config['data']['image_size'], config['data']['image_size']),
            torch.randint(0, num_classes, (100,))
        )
        n_val = 20
        train_ds, val_ds = random_split(dummy, [80, n_val])
        class_names = [f"class_{i}" for i in range(num_classes)]
    else:
        num_classes = len(full_dataset.classes)
        class_names = full_dataset.classes
        n_val  = int(len(full_dataset) * config['data']['val_split'])
        n_test = int(len(full_dataset) * config['data']['test_split'])
        n_train = len(full_dataset) - n_val - n_test
        train_ds, val_ds, _ = random_split(
            full_dataset, [n_train, n_val, n_test],
            generator=torch.Generator().manual_seed(config['data']['seed'])
        )
        print(f"  Dataset: {len(full_dataset):,} ảnh | {num_classes} class")
        print(f"  Train: {n_train:,} | Val: {n_val:,} | Test: {n_test:,}\n")

    # ── Class Weights & WeightedRandomSampler ─
    # (Phải tạo TRƯỚC DataLoader)
    class_weights = None
    sampler = None
    if hasattr(full_dataset, 'samples') and len(full_dataset) > 0:
        weights_path = config['loss'].get('class_weights_path', 'configs/class_weights.json')
        class_weights = compute_class_weights(full_dataset, save_path=weights_path)
        class_weights = class_weights.to(device)

        # WeightedRandomSampler: đảm bảo mỗi batch có phân phối class cân bằng hơn
        # Mỗi ảnh được gán trọng số = class_weight của class nó thuộc về
        train_labels = [full_dataset.samples[i][1] for i in train_ds.indices]
        sample_weights = [class_weights[label].item() for label in train_labels]
        sampler = WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(sample_weights),
            replacement=True  # Cho phép lấy lặp ảnh của class thiểu số
        )
        print(f"  ✅ WeightedRandomSampler: Bật — cân bằng {num_classes} class trong mỗi batch")

    train_loader = DataLoader(
        train_ds,
        batch_size=config['data']['batch_size'],
        shuffle=(sampler is None),  # Tắt shuffle khi có sampler
        sampler=sampler,
        num_workers=config['data']['num_workers'],
        pin_memory=True
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=config['data']['batch_size'],
        shuffle=False,
        num_workers=config['data']['num_workers'],
        pin_memory=True
    )

    # ── Model ─────────────────────────────────
    model = VNFoodModel(
        backbone_name=config['model']['backbone'],
        num_classes=num_classes,
        pretrained=config['model']['pretrained'],
        dropout=config['model']['dropout']
    ).to(device)

    freeze_epochs = config['model'].get('freeze_backbone_epochs', 0)
    if freeze_epochs > 0:
        model.freeze_backbone()

    # ── Loss ──────────────────────────────────
    criterion = FocalLoss(
        alpha=config['loss']['focal_alpha'],
        gamma=config['loss']['focal_gamma'],
        class_weights=class_weights,
        label_smoothing=config['loss']['label_smoothing'],
        num_classes=num_classes
    )

    # ── Optimizer & Scheduler ─────────────────
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=config['training']['learning_rate'],
        weight_decay=config['training']['weight_decay']
    )
    scheduler = CosineAnnealingLR(
        optimizer,
        T_max=config['training']['epochs'],
        eta_min=config['training']['min_lr']
    )

    # ── W&B Logging ───────────────────────────
    use_wandb = config['logging'].get('use_wandb', False)
    if use_wandb:
        try:
            import wandb
            wandb.init(project=config['logging']['project_name'],
                       name=config['logging']['experiment_name'],
                       config=config)
        except ImportError:
            print("⚠️  wandb chưa cài. Bỏ qua logging W&B.")
            use_wandb = False

    # ── Checkpointing ─────────────────────────
    ckpt_dir = Path(config['training']['checkpoint_dir']) / config['model']['backbone']
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # Lưu class names để dùng lúc inference
    with open(ckpt_dir / "class_names.json", "w", encoding="utf-8") as f:
        json.dump(class_names, f, ensure_ascii=False, indent=2)

    best_val_acc = 0.0
    patience_counter = 0
    patience = config['training']['early_stopping_patience']
    start_epoch = 1

    # ── Auto-Resume: Tiếp tục từ checkpoint cuối cùng nếu có ─
    resume_path = ckpt_dir / "last_checkpoint.pth"
    if resume_path.exists():
        print(f"\n🔄 Phát hiện checkpoint cũ! Đang resume từ: {resume_path}")
        resume_ckpt = torch.load(resume_path, map_location=device)
        model.load_state_dict(resume_ckpt['state_dict'])
        optimizer.load_state_dict(resume_ckpt['optimizer_state'])
        scheduler.load_state_dict(resume_ckpt['scheduler_state'])
        start_epoch    = resume_ckpt['epoch'] + 1
        best_val_acc   = resume_ckpt['best_val_acc']
        patience_counter = resume_ckpt['patience_counter']
        print(f"   ✅ Resume từ Epoch {resume_ckpt['epoch']} | Best acc: {best_val_acc:.2f}%")
        print(f"   Tiếp tục từ Epoch {start_epoch}...\n")
    else:
        print(f"  Không có checkpoint cũ. Bắt đầu từ đầu.\n")

    # Đường dẫn sync lên Drive (chỉ hoạt động trên Colab)
    drive_ckpt_dir = None
    colab_drive = Path("/content/drive/MyDrive")
    if colab_drive.exists():
        # Tìm thư mục dự án trên Drive tự động
        for candidate in [
            colab_drive / "vnfood_vision" / "checkpoints",
            colab_drive / "VietFood-Project" / "vnfood_vision" / "checkpoints",
        ]:
            if candidate.parent.exists():
                drive_ckpt_dir = candidate / config['model']['backbone']
                drive_ckpt_dir.mkdir(parents=True, exist_ok=True)
                print(f"  💾 Drive sync: Bật — sẽ tự động lưu về {drive_ckpt_dir} sau mỗi epoch")
                break

    # ── Training Loop ─────────────────────────
    for epoch in range(start_epoch, config['training']['epochs'] + 1):

        # Unfreeze backbone sau N epoch
        if epoch == freeze_epochs + 1 and freeze_epochs > 0:
            model.unfreeze_backbone()
            print(f"\n[Epoch {epoch}] Unfreeze backbone! Tiếp tục fine-tune toàn bộ.")
            
            # ── CHỐNG SỐC RÃ ĐÔNG (ANTI-SHOCK) ──
            # Giảm Learning Rate cơ sở đi 10 lần để không đập vỡ weights của EfficientNet
            for i in range(len(scheduler.base_lrs)):
                scheduler.base_lrs[i] *= 0.1
            print(f"  📉 Đã giảm Learning Rate 10 lần để chống sốc (Catastrophic Forgetting)!\n")

        t0 = time.time()
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device, config, epoch)
        val_loss, val_acc1, val_acc5 = validate(
            model, val_loader, criterion, device)
        scheduler.step()

        elapsed = time.time() - t0
        lr_now = optimizer.param_groups[0]['lr']

        print(f"Epoch {epoch:03d}/{config['training']['epochs']} "
              f"| LR: {lr_now:.2e} "
              f"| Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% "
              f"| Val Loss: {val_loss:.4f} "
              f"| Val Top-1: {val_acc1:.2f}% Top-5: {val_acc5:.2f}% "
              f"| {elapsed:.0f}s")

        if use_wandb:
            import wandb
            wandb.log({"epoch": epoch, "train_loss": train_loss,
                       "train_acc": train_acc, "val_loss": val_loss,
                       "val_acc1": val_acc1, "val_acc5": val_acc5, "lr": lr_now})

        # ── Lưu last_checkpoint.pth (Mọi epoch — để resume khi mất kết nối) ─
        last_ckpt = {
            "epoch": epoch,
            "backbone": config['model']['backbone'],
            "num_classes": num_classes,
            "class_names": class_names,
            "best_val_acc": best_val_acc,
            "patience_counter": patience_counter,
            "val_acc1": val_acc1,
            "state_dict": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "scheduler_state": scheduler.state_dict(),
        }
        torch.save(last_ckpt, ckpt_dir / "last_checkpoint.pth")

        # ── Lưu best_model.pth nếu có cải thiện ────────
        if val_acc1 > best_val_acc:
            best_val_acc = val_acc1
            patience_counter = 0
            best_ckpt = {
                "epoch": epoch,
                "backbone": config['model']['backbone'],
                "num_classes": num_classes,
                "class_names": class_names,
                "val_acc1": val_acc1,
                "state_dict": model.state_dict()
            }
            torch.save(best_ckpt, ckpt_dir / "best_model.pth")
            print(f"  ✅ Best model saved! Val Top-1: {val_acc1:.2f}%")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n⏹️  Early stopping sau {patience} epoch không cải thiện.")
                break

        # ── Tự động sync checkpoint lên Google Drive ────────
        if drive_ckpt_dir is not None:
            import shutil
            for fname in ["last_checkpoint.pth", "best_model.pth", "class_names.json"]:
                src_f = ckpt_dir / fname
                if src_f.exists():
                    shutil.copy(src_f, drive_ckpt_dir / fname)
            print(f"  💾 Đã sync → Drive ({epoch}/{config['training']['epochs']})")

    print(f"\n🎉 Training xong! Best Val Top-1 Accuracy: {best_val_acc:.2f}%")
    print(f"   Model đã lưu tại: {ckpt_dir / 'best_model.pth'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VNFood Vision Training")
    parser.add_argument("--config",   default="configs/config.yaml",
                        help="Đường dẫn file config")
    parser.add_argument("--backbone", default=None,
                        help="Override backbone: efficientnet_b3 | resnet50 | mobilenet_v3_large")
    parser.add_argument("--data_dir", default=None,
                        help="Override đường dẫn data/processed/. "
                             "VD Colab: /content/drive/MyDrive/VietFood-Project/data/processed")
    args = parser.parse_args()
    main(args.config, args.backbone, args.data_dir)
