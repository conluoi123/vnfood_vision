"""
inference.py — VNFood Vision
Nhận vào 1 ảnh → trả về top-K dự đoán + confidence score
Hỗ trợ: Test Time Augmentation (TTA)

Chạy:
  python src/inference.py --image path/to/anh.jpg
  python src/inference.py --image path/to/anh.jpg --tta
"""
import argparse
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
import yaml
from PIL import Image
from torchvision import transforms

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.model import VNFoodModel


# ─────────────────────────────────────────────
# TTA TRANSFORMS (5 biến thể)
# ─────────────────────────────────────────────
def get_tta_transforms(image_size: int):
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    return [
        transforms.Compose([transforms.Resize(image_size + 32),
                            transforms.CenterCrop(image_size),
                            transforms.ToTensor(), normalize]),
        transforms.Compose([transforms.Resize(image_size + 32),
                            transforms.RandomHorizontalFlip(p=1.0),
                            transforms.CenterCrop(image_size),
                            transforms.ToTensor(), normalize]),
        transforms.Compose([transforms.Resize(image_size + 64),
                            transforms.CenterCrop(image_size),
                            transforms.ToTensor(), normalize]),
        transforms.Compose([transforms.Resize(image_size + 32),
                            transforms.RandomRotation(degrees=10),
                            transforms.CenterCrop(image_size),
                            transforms.ToTensor(), normalize]),
        transforms.Compose([transforms.Resize(image_size + 32),
                            transforms.ColorJitter(brightness=0.2, contrast=0.2),
                            transforms.CenterCrop(image_size),
                            transforms.ToTensor(), normalize]),
    ]


# ─────────────────────────────────────────────
# PREDICT FUNCTION
# ─────────────────────────────────────────────
@torch.no_grad()
def predict(image_path: str, config_path: str, use_tta: bool = False, device: str = None, model_path_override: str = None):
    """
    Trả về:
        list of dict: [{"class": "pho_bo", "confidence": 0.92}, ...]
    """
    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    inf_cfg = config.get('inference', {})
    top_k   = inf_cfg.get('top_k', 5)
    thresh  = inf_cfg.get('confidence_threshold', 0.3)
    ckpt_path = model_path_override or inf_cfg.get('model_path', 'checkpoints/best_model.pth')

    # Device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device)

    # Load checkpoint
    ckpt = torch.load(ckpt_path, map_location=device)
    class_names = ckpt.get('class_names', [])
    num_classes  = ckpt.get('num_classes', len(class_names))

    model = VNFoodModel(
        backbone_name=ckpt.get('backbone', config['model']['backbone']),
        num_classes=num_classes,
        pretrained=False,
        dropout=0.0     # Tắt dropout lúc inference
    ).to(device)
    model.load_state_dict(ckpt['state_dict'])
    model.eval()

    # Load ảnh
    image = Image.open(image_path).convert("RGB")
    image_size = config['data']['image_size']

    if use_tta:
        # TTA: average logits từ 5 transform khác nhau
        tta_transforms = get_tta_transforms(image_size)
        logits_list = []
        for t in tta_transforms:
            inp = t(image).unsqueeze(0).to(device)
            logits_list.append(model(inp))
        avg_logits = torch.stack(logits_list).mean(0)
        probs = F.softmax(avg_logits, dim=1)[0]
    else:
        normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        transform = transforms.Compose([
            transforms.Resize(image_size + 32),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(), normalize
        ])
        inp = transform(image).unsqueeze(0).to(device)
        probs = F.softmax(model(inp), dim=1)[0]

    # Top-K results
    top_probs, top_indices = probs.topk(min(top_k, num_classes))
    results = []
    for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
        class_name = class_names[idx] if idx < len(class_names) else f"class_{idx}"
        results.append({"class": class_name, "confidence": round(prob, 4)})

    # Nếu confidence thấp → không xác định
    if results and results[0]['confidence'] < thresh:
        print(f"⚠️  Confidence thấp ({results[0]['confidence']:.2%}) — "
              "Có thể là ảnh ngoài phân phối training data.")

    return results


# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="VNFood Vision — Inference")
    parser.add_argument("--image",  required=True, help="Đường dẫn tới ảnh cần nhận diện")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--model_path", default=None, help="Đường dẫn tới checkpoint (ví dụ: checkpoints/best_model.pth)")
    parser.add_argument("--tta",    action="store_true", help="Bật Test Time Augmentation")
    parser.add_argument("--device", default=None, help="cuda | cpu (auto nếu để trống)")
    args = parser.parse_args()

    print(f"\n📸 Đang nhận diện: {args.image}")
    if args.model_path:
        print(f"   Model: {args.model_path}")
    print(f"   TTA: {'✅ Bật' if args.tta else '❌ Tắt'}\n")

    results = predict(args.image, args.config, args.tta, args.device, args.model_path)

    print("🍜 KẾT QUẢ DỰ ĐOÁN:")
    print("─" * 40)
    for i, r in enumerate(results, 1):
        bar = "█" * int(r['confidence'] * 30)
        print(f"  #{i} {r['class']:<25} {r['confidence']:6.2%}  {bar}")
    print("─" * 40)


if __name__ == "__main__":
    main()
