# 🍜 Viet Food AI: Vietnamese Food Recognition

[![GitHub](https://img.shields.io/badge/Repo-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/viet-food-ai/vnfood_vision)
[![W&B](https://img.shields.io/badge/Tracking-W%26B-FFBE00?style=for-the-badge&logo=weightsandbiases&logoColor=white)](https://wandb.ai/)
[![Colab](https://img.shields.io/badge/Platform-Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)](https://colab.research.google.com/)
[![Kaggle](https://img.shields.io/badge/Platform-Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/)

Dự án nghiên cứu và phát triển hệ thống nhận diện món ăn Việt Nam sử dụng các kỹ thuật Deep Learning tiên tiến. Dự án được tối ưu hóa cho làm việc nhóm từ xa với các công cụ miễn phí và mạnh mẽ.

---

## 🏗️ Kiến trúc Hệ thống

### 1. Quản lý Mã nguồn (GitHub)
Toàn bộ mã nguồn được lưu trữ tập trung tại GitHub với quy tắc phân nhánh nghiêm ngặt:
- `main`: Chỉ chứa code đã kiểm thử (stable).
- `dev`: Nhánh tích hợp chung cho các tính năng mới.
- `feat/*`: Các nhánh tính năng riêng biệt (ví dụ: `feat/1a-eda`, `feat/1b-crawler`).

### 2. Lưu trữ Dữ liệu (Google Drive)
Do giới hạn dung lượng của GitHub, toàn bộ dữ liệu ảnh được lưu trữ trên **Shared Google Drive**:
- `data/raw/`: Dữ liệu thô (VietFood67, 30VNFoods).
- `data/processed/`: Dữ liệu đã qua xử lý và lọc bởi CLIP.
- `data/crawled/`: Dữ liệu mới thu thập từ crawler.
- `checkpoints/`: Lưu trữ trọng số mô hình (.pth).

### 3. Nền tảng Huấn luyện
| Nhóm | Nhiệm vụ | Nền tảng | Lý do |
| :--- | :--- | :--- | :--- |
| **1A** | EDA & CLIP Filtering | Colab T4 | Cần GPU nhẹ, ổn định |
| **1B** | Crawler (Selenium) | Local/Colab | Không yêu cầu GPU mạnh |
| **3** | Pipeline Test | Colab | Test nhanh với dummy data |
| **4** | Training | Kaggle | 30h GPU/tuần, ổn định cho chạy lâu |

---

## 📁 Cấu trúc Thư mục

```text
viet-food-ai/
├── data/                  # Dữ liệu (Bị ignore, lưu trên Drive)
│   ├── raw/               
│   └── processed/         
├── notebooks/             # Jupyter Notebooks cho thí nghiệm
│   ├── 1A_eda.ipynb
│   ├── 1B_crawler.ipynb
│   ├── 2_labeling_setup.ipynb
│   ├── 3_pipeline.ipynb
│   └── 4_training.ipynb
├── src/                   # Mã nguồn chính (.py)
│   ├── dataset.py         # Custom Dataset & Dataloader
│   ├── model.py           # Định nghĩa kiến trúc Model
│   ├── train.py           # Script huấn luyện
│   └── utils.py           # Tiện ích bổ trợ
├── configs/               # File cấu hình (YAML)
├── reports/               # Báo cáo EDA, biểu đồ, logs
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔄 Quy trình Làm việc (Workflow)

1. **Nhóm 1A (EDA)**: Hoàn thành phân tích dữ liệu ➔ Xuất `shortage_report.json` lên GitHub.
2. **Nhóm 1B (Crawler)**: Dựa vào report để crawl thêm dữ liệu thiếu ➔ Đẩy lên Drive.
3. **Nhóm 3+4**: Kéo dữ liệu từ Drive về để phát triển Pipeline và huấn luyện Model.

**Tracking:** Sử dụng **Weights & Biases (W&B)** để theo dõi metrics, loss và so sánh các thí nghiệm theo thời gian thực.

---

## 🛠️ Hướng dẫn Cài đặt

### 1. Clone Project
```bash
git clone https://github.com/viet-food-ai/vnfood_vision.git
cd vnfood_vision
```

### 2. Cài đặt Môi trường
```bash
pip install -r requirements.txt
```

### 3. Kết nối Google Drive (Trên Colab)
Sử dụng đoạn code sau để mount Drive và truy cập dữ liệu:
```python
from google.colab import drive
drive.mount('/content/drive')

# Đường dẫn đến thư mục dự án trên Drive
PROJECT_PATH = '/content/drive/MyDrive/VietFood-Project'
```

---

## ✅ Checklist cho Team
- [ ] Tham gia Collaborator trên GitHub.
- [ ] Truy cập Shared Google Drive của dự án.
- [ ] Tạo tài khoản W&B và join Team Project.
- [ ] Test mount Drive trên Colab cá nhân.

---
*Dự án được thực hiện bởi Nhóm VietFood AI - 2026*