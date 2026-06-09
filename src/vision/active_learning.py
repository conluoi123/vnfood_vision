"""
active_learning.py — VNFood Vision
Dùng mô hình đã train để tự động tìm ra những ảnh "khả nghi"
(ảnh mà mô hình thấy nhãn thư mục KHÔNG khớp với nội dung ảnh)
→ Xuất danh sách ra CSV + JSON để import vào Label Studio

Luồng hoạt động:
  1. Load model đã train (best_model.pth)
  2. Chạy inference trên toàn bộ thư mục processed/
  3. Tính "điểm khả nghi" cho mỗi ảnh
  4. AI TỰ QUYẾT ĐỊNH số lượng ảnh cần review (không cần đặt cứng con số)

Chạy LOCAL:
  python src/vision/active_learning.py

Chạy COLAB:
  !python src/vision/active_learning.py \\
    --data_dir "/content/drive/MyDrive/VietFood-Project/data/processed" \\
    --model_path "checkpoints/best_model.pth"

  # Nếu muốn override thủ công:
  !python src/vision/active_learning.py --top_n 500
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
import yaml
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.vision.model import VNFoodModel


# ─────────────────────────────────────────────
# ĐỊNH NGHĨA "ĐIỂM KHẢ NGHI"
# ─────────────────────────────────────────────
# Ảnh bị đánh dấu khả nghi khi rơi vào 1 trong 2 trường hợp:
#
# TRƯỜNG HỢP 1 — SAI LỚP (Wrong class):
#   Model dự đoán nhãn KHÁC hoàn toàn so với thư mục chứa ảnh.
#   VD: Ảnh nằm trong thư mục "pho_bo" nhưng model bảo đây là "bun_rieu" (confidence 87%)
#   → Điểm khả nghi = confidence của nhãn SAI (càng cao càng nguy hiểm)
#
# TRƯỜNG HỢP 2 — MÔ HÌNH KHÔNG CHẮC (Low confidence):
#   Model predict đúng lớp NHƯNG confidence rất thấp.
#   VD: Ảnh là "pho_bo", model cũng bảo "pho_bo" nhưng chỉ chắc 31%
#   → Thường là ảnh mờ, góc chụp xấu, nhiều thứ trong ảnh
#   → Điểm khả nghi = (1 - confidence_đúng_lớp)
# ─────────────────────────────────────────────


def get_val_transform(image_size: int):
    return transforms.Compose([
        transforms.Resize(image_size + 32),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])


@torch.no_grad()
def scan_dataset(data_dir: str, model: VNFoodModel, class_names: list,
                 image_size: int, device: torch.device,
                 low_conf_threshold: float = 0.5) -> list:
    """
    Quét toàn bộ thư mục data_dir, tính điểm khả nghi cho mỗi ảnh.
    Trả về list of dict đã sắp xếp theo điểm khả nghi giảm dần.
    """
    model.eval()
    transform = get_val_transform(image_size)

    # Tạo mapping: tên class → index
    class_to_idx = {cls: i for i, cls in enumerate(class_names)}

    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục: {data_dir}")

    # Thu thập tất cả file ảnh
    all_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        all_images.extend(data_path.rglob(ext))

    print(f"  Tìm thấy {len(all_images):,} ảnh trong {data_dir}")
    print(f"  Đang chạy inference... (có thể mất vài phút)\n")

    suspicious = []

    for img_path in tqdm(all_images, desc="Scanning", unit="ảnh"):
        # Tên thư mục chứa ảnh = nhãn thực tế (ground truth từ cấu trúc thư mục)
        true_class_name = img_path.parent.name
        true_idx = class_to_idx.get(true_class_name, -1)

        # Bỏ qua ảnh nằm ở thư mục không có trong danh sách class
        if true_idx == -1:
            continue

        try:
            image = Image.open(img_path).convert("RGB")
            inp = transform(image).unsqueeze(0).to(device)
            probs = F.softmax(model(inp), dim=1)[0]
        except Exception:
            # Ảnh bị hỏng, không đọc được → khả nghi tối đa
            suspicious.append({
                "image_path": str(img_path),
                "true_class": true_class_name,
                "predicted_class": "UNREADABLE",
                "true_class_conf": 0.0,
                "predicted_conf": 1.0,
                "suspicion_score": 1.0,
                "suspicion_reason": "Ảnh lỗi — không đọc được file"
            })
            continue

        pred_idx = probs.argmax().item()
        pred_class = class_names[pred_idx]
        pred_conf = probs[pred_idx].item()
        true_conf = probs[true_idx].item()

        # ── Trường hợp 1: Sai lớp ──────────────────────
        if pred_idx != true_idx:
            suspicion_score = pred_conf          # Càng chắc sai → càng nguy hiểm
            reason = (f"Mô hình nhầm '{true_class_name}' → '{pred_class}' "
                      f"(confidence {pred_conf:.1%})")
            suspicious.append({
                "image_path": str(img_path),
                "true_class": true_class_name,
                "predicted_class": pred_class,
                "true_class_conf": round(true_conf, 4),
                "predicted_conf": round(pred_conf, 4),
                "suspicion_score": round(suspicion_score, 4),
                "suspicion_reason": reason
            })

        # ── Trường hợp 2: Đúng lớp nhưng confidence thấp ──
        elif true_conf < low_conf_threshold:
            suspicion_score = 1.0 - true_conf   # Confidence thấp → nghi ngờ cao
            reason = (f"Đúng lớp '{true_class_name}' nhưng mô hình không chắc "
                      f"(confidence chỉ {true_conf:.1%})")
            suspicious.append({
                "image_path": str(img_path),
                "true_class": true_class_name,
                "predicted_class": pred_class,
                "true_class_conf": round(true_conf, 4),
                "predicted_conf": round(pred_conf, 4),
                "suspicion_score": round(suspicion_score, 4),
                "suspicion_reason": reason
            })

    # Sắp xếp theo điểm khả nghi giảm dần
    suspicious.sort(key=lambda x: x['suspicion_score'], reverse=True)
    return suspicious


def auto_decide_top_n(suspicious: list) -> tuple[int, str]:
    """
    AI tự quyết định số lượng ảnh cần review dựa trên phân phối điểm khả nghi.

    Chiến lược 3 lớp:
      Lớp 1 — LUÔN LUÔN review: Toàn bộ ảnh SAI LỚP và ảnh LỖI FILE
               (Đây là những ảnh chắc chắn có vấn đề, không thể bỏ qua)

      Lớp 2 — REVIEW THÔNG MINH: Ảnh confidence thấp có điểm >= ngưỡng tự động
               Ngưỡng = mean(scores) + 0.5 * std(scores) của nhóm này
               (Chỉ lấy những ảnh "thực sự đáng ngờ", bỏ qua ảnh hơi mờ bình thường)

      Lớp 3 — GIỚI HẠN AN TOÀN: Không quá 15% tổng dataset để team review được
               trong 1 buổi làm việc hợp lý

    Trả về: (top_n, lý_do_quyết_định)
    """
    if not suspicious:
        return 0, "Không có ảnh khả nghi nào."

    # Phân loại
    wrong_class = [x for x in suspicious
                   if x['predicted_class'] != x['true_class']]
    low_conf    = [x for x in suspicious
                   if x['predicted_class'] == x['true_class']
                   and x['predicted_class'] != "UNREADABLE"]

    # Lớp 1: Bắt buộc review tất cả ảnh sai lớp + lỗi file
    mandatory_n = len(wrong_class)
    reasons = [f"{mandatory_n:,} ảnh sai lớp/lỗi file (bắt buộc review)"]

    # Lớp 2: Tự động tìm ngưỡng cho nhóm confidence thấp
    optional_n = 0
    if low_conf:
        scores = [x['suspicion_score'] for x in low_conf]
        mean_s = sum(scores) / len(scores)
        variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
        std_s = variance ** 0.5

        # Chỉ lấy ảnh có điểm cao hơn mức trung bình
        # (mean + 0.5*std = ngưỡng "đáng ngờ hơn bình thường")
        auto_threshold = mean_s + 0.5 * std_s
        auto_threshold = min(auto_threshold, 0.85)  # Không quá khắt khe
        auto_threshold = max(auto_threshold, 0.55)  # Không quá lỏng lẻo

        optional_n = sum(1 for s in scores if s >= auto_threshold)
        reasons.append(
            f"{optional_n:,} ảnh confidence thấp "
            f"(ngưỡng tự động: {auto_threshold:.2f}, "
            f"mean={mean_s:.2f}, std={std_s:.2f})"
        )

    raw_total = mandatory_n + optional_n

    # Lớp 3: Giới hạn an toàn = 15% tổng số ảnh khả nghi
    # (Nếu dataset 27k thì giới hạn là ~4k ảnh để review trong 1 buổi)
    safety_cap = max(int(len(suspicious) * 0.15), mandatory_n, 50)
    final_n = min(raw_total, safety_cap)

    if final_n < raw_total:
        reasons.append(
            f"Giới hạn an toàn {safety_cap:,} ảnh (≤15% tổng khả nghi) được áp dụng"
        )

    reason_str = " + ".join(reasons)
    return final_n, reason_str


def export_csv(suspicious: list, output_path: str):
    """Xuất danh sách ảnh khả nghi ra CSV để dễ đọc."""
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "suspicion_score", "suspicion_reason",
            "true_class", "predicted_class",
            "true_class_conf", "predicted_conf", "image_path"
        ])
        writer.writeheader()
        writer.writerows(suspicious)
    print(f"  📄 CSV  → {output_path}")


def export_label_studio_json(suspicious: list, output_path: str,
                              data_dir: str, top_n: int):
    """
    Xuất file JSON theo định dạng Label Studio để import trực tiếp.
    Chỉ lấy top_n ảnh khả nghi nhất (top_n được quyết định tự động hoặc thủ công).
    """
    tasks = []
    for item in suspicious[:top_n]:
        try:
            data_value = f"/data/local-files/?d={item['image_path']}"
        except Exception:
            data_value = f"/data/local-files/?d={item['image_path']}"

        tasks.append({
            "data": {"image": data_value},
            "meta": {
                "true_class": item['true_class'],
                "predicted_class": item['predicted_class'],
                "suspicion_score": item['suspicion_score'],
                "suspicion_reason": item['suspicion_reason']
            }
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    print(f"  📄 JSON → {output_path}  (để import vào Label Studio)")


def print_summary(suspicious: list, top_n: int, auto_reason: str = ""):
    """In bảng tóm tắt kết quả."""
    wrong_class = [x for x in suspicious if x['predicted_class'] != x['true_class']
                   and x['predicted_class'] != "UNREADABLE"]
    low_conf    = [x for x in suspicious if x['predicted_class'] == x['true_class']]
    unreadable  = [x for x in suspicious if x['predicted_class'] == "UNREADABLE"]

    print(f"\n{'='*60}")
    print(f"  KẾT QUẢ ACTIVE LEARNING SCAN")
    print(f"{'='*60}")
    print(f"  🔴 Sai lớp (ảnh nhầm thư mục)  : {len(wrong_class):>6,} ảnh")
    print(f"  🟡 Confidence thấp (ảnh mờ/xấu): {len(low_conf):>6,} ảnh")
    print(f"  ⚫ Lỗi file (không đọc được)    : {len(unreadable):>6,} ảnh")
    print(f"  {'─'*41}")
    print(f"  Tổng ảnh khả nghi               : {len(suspicious):>6,} ảnh")
    print(f"")
    if auto_reason:
        print(f"  🤖 AI tự quyết định export: {top_n:,} ảnh")
        print(f"     Lý do: {auto_reason}")
    else:
        print(f"  📌 Export thủ công: {top_n:,} ảnh (do người dùng chỉ định --top_n)")
    print(f"{'='*60}")

    if suspicious:
        print(f"\n  🏆 TOP 5 ẢNH KHẢ NGHI NHẤT:")
        print(f"  {'Score':<8} {'Lý do'}")
        print(f"  {'─'*50}")
        for item in suspicious[:5]:
            print(f"  {item['suspicion_score']:.3f}   {item['suspicion_reason']}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="VNFood Vision — Active Learning Scanner")
    parser.add_argument("--config",     default="configs/config.yaml")
    parser.add_argument("--data_dir",   default=None,
                        help="Đường dẫn thư mục processed/ (override config)")
    parser.add_argument("--model_path", default=None,
                        help="Đường dẫn checkpoint .pth (override config)")
    parser.add_argument("--top_n",      type=int, default=None,
                        help="[Tùy chọn] Chỉ định cứng số ảnh export. "
                             "Nếu KHÔNG truyền → AI tự quyết định (khuyên dùng)")
    parser.add_argument("--low_conf",   type=float, default=0.5,
                        help="Ngưỡng confidence thấp ban đầu (mặc định: 0.5)")
    parser.add_argument("--output_dir", default="outputs/active_learning",
                        help="Thư mục lưu kết quả")
    args = parser.parse_args()

    # Load config
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Giải quyết đường dẫn
    import os
    data_dir = (args.data_dir
                or os.environ.get("VNFOOD_DATA_DIR", "")
                or config['data'].get('processed_dir', '')
                or str(Path(__file__).resolve().parent.parent / "data" / "processed"))

    model_path = (args.model_path
                  or config['inference'].get('model_path', 'checkpoints/best_model.pth'))

    print(f"\n{'='*60}")
    print(f"  VNFood Vision — Active Learning Scanner")
    print(f"  Data dir   : {data_dir}")
    print(f"  Model      : {model_path}")
    mode_str = f"{args.top_n:,} ảnh (thủ công)" if args.top_n else "Tự động (AI quyết định)"
    print(f"  Chế độ     : {mode_str}")
    print(f"  Low conf   : {args.low_conf:.0%}")
    print(f"{'='*60}\n")

    # Load model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device: {device}")

    if not Path(model_path).exists():
        print(f"\n❌ Không tìm thấy model tại: {model_path}")
        print("   Hãy chạy train.py trước để có file best_model.pth!")
        return

    ckpt = torch.load(model_path, map_location=device)
    class_names = ckpt['class_names']
    num_classes  = ckpt['num_classes']

    model = VNFoodModel(
        backbone_name=ckpt.get('backbone', config['model']['backbone']),
        num_classes=num_classes,
        pretrained=False,
        dropout=0.0
    ).to(device)
    model.load_state_dict(ckpt['state_dict'])
    print(f"  Model loaded: {ckpt.get('backbone')} | {num_classes} classes | "
          f"Val acc: {ckpt.get('val_acc1', 0):.2f}%\n")

    # Quét dataset
    suspicious = scan_dataset(
        data_dir=data_dir,
        model=model,
        class_names=class_names,
        image_size=config['data']['image_size'],
        device=device,
        low_conf_threshold=args.low_conf
    )

    # Quyết định số lượng ảnh export
    auto_reason = ""
    if args.top_n is not None:
        # Người dùng chỉ định cứng → dùng luôn
        top_n = args.top_n
    else:
        # AI tự quyết định
        top_n, auto_reason = auto_decide_top_n(suspicious)

    # In tóm tắt
    print_summary(suspicious, top_n, auto_reason)

    # Export kết quả
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    export_csv(suspicious, str(output_dir / "suspicious_images.csv"))
    export_label_studio_json(suspicious, str(output_dir / "label_studio_import.json"),
                              data_dir, top_n)

    print(f"\n✅ Hoàn tất!")
    print(f"   Bước tiếp theo:")
    print(f"   1. Mở Label Studio → Project → Import")
    print(f"   2. Upload file: {output_dir / 'label_studio_import.json'}")
    print(f"   3. Team chỉ cần review {min(top_n, len(suspicious)):,} ảnh này!")


if __name__ == "__main__":
    main()
