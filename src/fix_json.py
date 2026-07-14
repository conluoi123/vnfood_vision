import json
import os
import tkinter as tk
from tkinter import filedialog

def fix_label_studio_json():
    root = tk.Tk()
    root.withdraw()
    print("Vui lòng chọn file label_studio_import.json gốc (file tải từ Colab về)...")
    json_path = filedialog.askopenfilename(
        title="Chọn file JSON từ Colab", 
        filetypes=[("JSON files", "*.json")]
    )
    
    if not json_path:
        print("Đã hủy.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for item in data:
        if "data" in item:
            old_path = item["data"].get("image") or item["data"].get("img")
            if old_path:
                # Đường dẫn gốc từ Colab có dạng: /data/local-files/?d=/content/drive/MyDrive/VietFood-Project/...
                # Ta cần biến nó thành: /data/local-files/?d=VietFood-Project/...
                # Để khi Label Studio (với DOCUMENT_ROOT là G:\My Drive) nối vào sẽ thành G:\My Drive\VietFood-Project\...
                
                # Trích xuất phần đuôi phía sau MyDrive/
                if "MyDrive/" in old_path:
                    relative_path = old_path.split("MyDrive/")[-1]
                else:
                    # Đề phòng trường hợp đường dẫn khác
                    parts = old_path.replace('\\', '/').split('/')
                    if len(parts) >= 2:
                        relative_path = f"{parts[-2]}/{parts[-1]}"
                    else:
                        relative_path = parts[-1]
                
                # Gỡ bỏ dấu '/' ở đầu nếu có
                if relative_path.startswith('/'):
                    relative_path = relative_path[1:]

                new_path = f"/data/local-files/?d={relative_path}"
                item["data"]["image"] = new_path
                item["data"]["img"] = new_path
                count += 1

    new_json_path = os.path.join(os.path.dirname(json_path), "fixed_import_cho_ngrok_v2.json")
    with open(new_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Đã sửa thành công {count} ảnh!")
    print(f"✅ Đã lưu file mới tại: {new_json_path}")
    print("\n👉 BƯỚC TIẾP THEO:")
    print("Vào Label Studio xóa hết rác cũ, và Import file '_v2.json' này vào nhé!")

if __name__ == "__main__":
    fix_label_studio_json()
