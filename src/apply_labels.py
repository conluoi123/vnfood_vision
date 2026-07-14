import json
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import unicodedata
import re

def normalize_label(label):
    # Xóa dấu tiếng Việt, chuyển thành chữ thường, thay khoảng trắng bằng gạch dưới
    text = unicodedata.normalize('NFKD', label).encode('ASCII', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'[\s\-]+', '_', text)
    text = re.sub(r'[^a-z0-9_]', '', text)
    return text

def apply_label_studio_export():
    # 1. Chọn file Export JSON từ Label Studio
    root = tk.Tk()
    root.withdraw()
    print("Vui lòng chọn file JSON vừa Export từ Label Studio...")
    json_path = filedialog.askopenfilename(
        title="Chọn file Export từ Label Studio", 
        filetypes=[("JSON files", "*.json")]
    )
    
    if not json_path:
        print("Đã hủy.")
        return

    # 2. Đọc file JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 3. Yêu cầu thư mục Data gốc
    print("\nFile Export đã chọn:", json_path)
    print("\nNhập đường dẫn thư mục 'data' gốc (Chứa các thư mục món ăn).")
    print("Ví dụ: G:\My Drive\Machine Learning\Project Food\vnfood_vision\data")
    base_dir = input("Đường dẫn thư mục data: ").strip()

    if not os.path.isdir(base_dir):
        print(f"Lỗi: Thư mục {base_dir} không tồn tại!")
        return

    # 4. Phân tích và di chuyển file
    moved_count = 0
    skipped_count = 0

    for item in data:
        # Kiểm tra xem ảnh này đã được con người gán nhãn chưa
        if "annotations" in item and len(item["annotations"]) > 0:
            annotation = item["annotations"][0]
            
            # Lấy nhãn (label) do con người chọn (Hỗ trợ cả vẽ khung Bounding Box và Chọn thẳng)
            human_label = None
            try:
                results = annotation.get("result", [])
                if not results:
                    continue # Bị bỏ qua không gán nhãn
                
                # Duyệt qua các result để tìm nhãn món ăn hoặc nhãn Rác
                for res in results:
                    val = res.get("value", {})
                    # Nếu dùng kiểu phân loại (Choices)
                    if "choices" in val:
                        human_label = val["choices"][0]
                        break
                    # Nếu dùng kiểu vẽ khung (RectangleLabels / PolygonLabels)
                    elif "rectanglelabels" in val:
                        human_label = val["rectanglelabels"][0]
                        break
                    elif "polygonlabels" in val:
                        human_label = val["polygonlabels"][0]
                        break
                
                if not human_label:
                    continue

                # Chuẩn hóa nhãn (Ví dụ: "Bánh xèo" -> "banh_xeo")
                human_label = normalize_label(human_label)

            except (KeyError, IndexError):
                continue

            # Lấy đường dẫn cũ tương đối từ chuỗi /data/local-files/?d=...
            img_url = item["data"].get("image", "") or item["data"].get("img", "")
            if "?d=" not in img_url:
                continue
            
            relative_path = img_url.split("?d=")[-1]
            old_abs_path = os.path.join(base_dir, relative_path.replace("/", os.sep))

            if not os.path.exists(old_abs_path):
                print(f"Cảnh báo: Không tìm thấy ảnh {old_abs_path}")
                continue

            # Xóa ảnh nếu người dùng chọn "Lỗi ảnh" hoặc "Rác"
            if human_label in ["loi_anh", "rac", "khong_phai_do_an"]:
                try:
                    os.remove(old_abs_path)
                    print(f"🗑️ Đã xóa rác: {os.path.basename(old_abs_path)}")
                    moved_count += 1
                except Exception as e:
                    print(f"Lỗi khi xóa {old_abs_path}: {e}")
                continue

            # Thư mục gốc chứa ảnh hiện tại (Ví dụ: banh_bot_loc)
            current_label = os.path.basename(os.path.dirname(old_abs_path))

            # Nếu con người sửa lại nhãn khác với thư mục hiện tại -> Di chuyển ảnh
            if human_label != current_label:
                new_label_dir = os.path.join(base_dir, human_label)
                os.makedirs(new_label_dir, exist_ok=True) # Tạo thư mục nếu chưa có
                
                new_abs_path = os.path.join(new_label_dir, os.path.basename(old_abs_path))
                
                # Di chuyển file
                shutil.move(old_abs_path, new_abs_path)
                print(f"Đã chuyển: {os.path.basename(old_abs_path)} | {current_label} -> {human_label}")
                moved_count += 1
            else:
                skipped_count += 1

    print(f"\n✅ HOÀN TẤT CẤU TRÚC LẠI DATASET!")
    print(f"👉 Số ảnh đã được dời sang đúng thư mục: {moved_count}")
    print(f"👉 Số ảnh giữ nguyên (đã đúng sẵn): {skipped_count}")

if __name__ == "__main__":
    apply_label_studio_export()
