# 🏷️ Hướng dẫn Khởi động Label Studio + Ngrok

> Mục đích: Chạy Label Studio trên máy local, chia sẻ cho cả team gán nhãn từ xa qua link Ngrok.

---

## ⚠️ Lưu ý quan trọng

- **Không được tắt máy tính hoặc bất kỳ cửa sổ CMD nào** trong suốt quá trình team đang gán nhãn.
- Mỗi lần bật lại Ngrok sẽ tạo ra **link mới** → phải cập nhật lại lệnh `LABEL_STUDIO_HOST` và `CSRF_TRUSTED_ORIGINS`.
- Google Drive Desktop phải đang **chạy và đồng bộ** trước khi bắt đầu.

---

## 📋 Quy trình mỗi lần làm việc

### BƯỚC 1: Bật Ngrok (Cửa sổ CMD thứ nhất)

1. Mở **Command Prompt** (Start → gõ `cmd` → Enter).
2. Chạy lệnh (kéo thả file `ngrok.exe` vào CMD, thêm `http 8080`):
   ```cmd
   ngrok http 8080
   ```
3. Chờ màn hình hiện lên dòng **Forwarding**, sao chép đường link `https://...ngrok-free.app`.

   Ví dụ:
   ```
   Forwarding   https://eudaemonistically-metallographical-kasha.ngrok-free.dev -> http://localhost:8080
   ```
4. **Copy link đó lại** (link sẽ thay đổi mỗi lần bật Ngrok).

---

### BƯỚC 2: Bật Label Studio (Cửa sổ CMD thứ hai)

Mở **một cửa sổ CMD mới** (không tắt cửa sổ Ngrok), rồi chạy **lần lượt từng dòng** (Enter sau mỗi dòng):

```cmd
set LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
```

```cmd
set LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=D:\GoogleDrive\My Drive
```

> ⚠️ Thay `D:\GoogleDrive\My Drive` bằng đúng đường dẫn Google Drive Desktop trên máy bạn nếu khác.

```cmd
set LABEL_STUDIO_HOST=https://LINK_NGROK_CUA_BAN
```

```cmd
set CSRF_TRUSTED_ORIGINS=https://LINK_NGROK_CUA_BAN
```

> 📌 Thay `LINK_NGROK_CUA_BAN` bằng link bạn vừa copy ở Bước 1. Ví dụ:
> `set LABEL_STUDIO_HOST=https://eudaemonistically-metallographical-kasha.ngrok-free.dev`

```cmd
label-studio
```

3. Chờ CMD hiện ra dòng chữ:
   ```
   Starting development server at http://0.0.0.0:8080/
   ```
   Lúc đó hệ thống mới thực sự sẵn sàng.

---

### BƯỚC 3: Gửi link cho team

Gửi link Ngrok từ Bước 1 cho cả team. Ví dụ:
```
https://eudaemonistically-metallographical-kasha.ngrok-free.dev
```

Khi bạn bè bấm vào và thấy màn hình cảnh báo của Ngrok → bảo họ bấm nút **"Visit Site"** để vào.

---

## 🛑 Khi kết thúc làm việc

1. Vào cửa sổ CMD chạy Label Studio → bấm `Ctrl + C`.
2. Vào cửa sổ CMD chạy Ngrok → bấm `Ctrl + C`.
3. Tắt 2 cửa sổ CMD đó đi.

---

## 💡 Mẹo: Tạo file .bat để khởi động nhanh

Tạo file `run_label.bat` (click đúp chuột là chạy, không cần gõ lệnh tay):

> ⚠️ Trước tiên phải bật Ngrok ở Bước 1 để lấy link mới, rồi mới cập nhật link vào file `.bat` này.

```bat
@echo off
set LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
set LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=D:\GoogleDrive\My Drive
set LABEL_STUDIO_HOST=https://LINK_NGROK_CUA_BAN
set CSRF_TRUSTED_ORIGINS=https://LINK_NGROK_CUA_BAN
label-studio
```

---

## ❓ Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|-----|-------------|----------|
| `403 Forbidden - CSRF verification failed` | Chưa khai báo `LABEL_STUDIO_HOST` và `CSRF_TRUSTED_ORIGINS` | Tắt Label Studio, chạy lại với đủ 5 dòng lệnh |
| `Site can't be reached` | Label Studio chưa khởi động xong | Chờ thêm 1-2 phút rồi F5 lại |
| Link Ngrok cũ không vào được | Link thay đổi sau mỗi lần bật | Lấy link mới từ cửa sổ Ngrok, cập nhật lại |
| `LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT is not recognized` | Copy nhiều dòng vào CMD một lúc | Dán **từng dòng một**, ấn Enter sau mỗi dòng |

---

# 🎯 Kiến trúc & Kế hoạch Demo cho Thầy

> Đây là đánh giá dựa trên các repo tham khảo (VLPCook, clip-retrieval, Cook Assistant...) và papers (FoodLMM, FoodCHA) — kết hợp với thực tế của dự án VNFood Vision.

---

## 🗺️ Pipeline Demo End-to-End (cốt lõi cần hoàn thiện)

```
📱 Ảnh món ăn (chụp điện thoại, góc lạ, ánh sáng thực tế)
        ↓
🧠 EfficientNet-B3 / ResNet50
   → Top-5 nhận diện + Confidence Score
        ↓
🔍 CLIP + FAISS Retrieval
   → Tìm ảnh tương tự trong database (semantic search)
        ↓
📚 RAG (ChromaDB / FAISS)
   → Trả ra Top-3 công thức nấu ăn phù hợp nhất
        ↓
🗺️ UMAP / t-SNE Embedding Explorer
   → Visualize "AI đang hiểu" các món ăn như thế nào
        ↓
🔥 Grad-CAM Visualization
   → Show "AI đang nhìn vào vùng nào" của ảnh khi predict
```

> **Tại sao pipeline này đủ mạnh?** Vì nó có đủ cả 4 yếu tố: **Vision + Retrieval + RAG + Explainability** — vượt xa "CNN nhận diện thông thường".

---

## ✅ Những module nên làm NGAY (ROI cao, ít tốn công)

| Module | Đánh giá | Lý do ưu tiên |
|--------|----------|---------------|
| **CLIP + FAISS Retrieval** | ⭐⭐⭐⭐⭐ | Đã có ảnh + công thức từ crawler rồi, chỉ cần build index. Clone repo `clip-faiss` về là xong trong 1–2 ngày. **Thay thế ChromaDB text-search** bằng visual search mạnh hơn nhiều |
| **UMAP Embedding Explorer** | ⭐⭐⭐⭐ | Cực kỳ đẹp khi demo cho thầy — thầy nhìn thấy ngay AI đang "cluster" các món ăn như thế nào. Code UMAP chỉ ~20 dòng |
| **Grad-CAM Visualization** | ⭐⭐⭐⭐⭐ | Đã có trong plan (Tuần 3 - Người 5). Cực kỳ thuyết phục về mặt học thuật — chứng minh model nhìn vào đặc trưng đúng chứ không học vẹt |
| **Taxonomy 3 tầng (FoodCHA style)** | ⭐⭐⭐⭐⭐ | Paper FoodCHA xác nhận cấu trúc nhãn 3 cấp (Vùng miền → Loại món → Tên món) của nhóm đang đi đúng hướng học thuật |

---

## ⚠️ Những module cân nhắc kỹ trước khi thêm

| Module | Vấn đề | Khuyến nghị |
|--------|---------|-------------|
| **Food Agent (LangGraph)** | Cần LLM, tốn thời gian tích hợp | Nếu muốn làm, dùng **Gemini API / OpenAI API free tier** thay vì tự host LLM để tiết kiệm effort |
| **Nutrition Analysis** | Cần dataset dinh dưỡng Việt Nam riêng, không có sẵn | Bỏ qua ở giai đoạn này |

---

## ❌ Những thứ KHÔNG nên thêm vào lúc này

- **YOLO / Object Detection / Segmentation:** Paper FoodLMM là roadmap 2–3 năm của team full-time, không phải scope đồ án. Thêm vào sẽ loãng effort toàn team.
- **Ingredient Detection chi tiết:** Tốn công label bbox cực kỳ nhiều, không xứng với thời gian bỏ ra.

---

## 🔄 Kiến trúc MLOps Lite & Engineering Roadmap

> Nhóm xây dựng một hệ thống có vòng đời tương đối hoàn chỉnh: từ Dữ liệu → Mô hình → API → Giao diện → Theo dõi → Cải thiện mô hình. Đây không còn là "đồ án CNN" — mà là một **AI Application có tư duy Engineer thực tế**.

### 📋 Roadmap 4 Pha

#### Phase 1: AI Core
- ✅ Vision (EfficientNet-B3 + Baseline so sánh)
- ✅ CLIP + FAISS Retrieval (Visual Semantic Search)
- ✅ Advanced RAG (Hybrid Search + Reranker + LLM)
- ✅ Explainable AI: Grad-CAM + UMAP Embedding Explorer

#### Phase 2: System (Fullstack)
- ✅ FastAPI Backend (API `/predict`, `/chat`, `/dashboard`)
- ✅ React Frontend (Upload ảnh, Chatbot, Bản đồ, TTS)
- ✅ Docker (`docker-compose up` → toàn bộ service chạy)

#### Phase 3: Engineering Best Practices
- ✅ Logging (Dữ liệu vận hành — Operational Data)
- ✅ Application Monitoring Dashboard (Biểu đồ theo dõi hiệu năng)
- ✅ Config Management (`pydantic-settings`, `.env`)
- ✅ Health Check Endpoint (`GET /health`)
- ✅ Model Metadata Endpoint (`GET /model/info`)
- ✅ API Documentation (Swagger UI — có sẵn từ FastAPI)

#### Phase 4: MLOps Lite (Active Learning)
- ✅ Ảnh confidence thấp (40-70%) → tự động lưu lại
- ✅ Label Studio → gán nhãn thủ công (Human-in-the-loop)
- ✅ Retrain model với dữ liệu mới
- ✅ Version model (v1.0, v1.1, v1.2...)

---

### 📝 Logging — Dữ liệu vận hành (Operational Data)

Logging không chỉ để debug lỗi. Nó tạo ra **dữ liệu vận hành** — sau vài tuần chạy hệ thống, ta sẽ biết:
- Có bao nhiêu request?
- Món nào được nhận diện nhiều nhất?
- Class nào confidence thấp (Model yếu ở đâu)?
- Thời gian infer trung bình?
- Request nào bị lỗi?

**Thư viện:** `loguru` (gọn, đẹp, 1 dòng setup).

```python
from loguru import logger
logger.add("logs/api_{time:YYYY-MM-DD}.log", rotation="1 day")
```

**Ví dụ log mỗi request:**
```text
2026-09-01 10:20 | image=pho_001.jpg | predict=Pho | confidence=0.97 | latency=41ms | status=200
```

---

### 📊 Application Monitoring Dashboard

**Kiến trúc dữ liệu:** Dùng **SQLite** (nhẹ, nhanh, truy vấn SQL chuẩn) thay vì đọc file log bằng regex.

```
React Dashboard → GET /api/v1/dashboard/stats → SQLite → JSON
```

**Bảng `predict_history` trong SQLite:**

| Cột | Mô tả |
|-----|-------|
| `id` | Auto increment |
| `time` | Timestamp của request |
| `class` | Tên món ăn được dự đoán |
| `confidence` | Độ tự tin (0.0 - 1.0) |
| `latency` | Thời gian xử lý (ms) |
| `filename` | Tên file ảnh |

**Truy vấn Dashboard chỉ cần:**
```sql
SELECT AVG(latency) FROM predict_history;                         -- Latency trung bình
SELECT class, COUNT(*) FROM predict_history GROUP BY class;        -- Top món nhận diện
SELECT COUNT(*) FROM predict_history WHERE confidence < 0.7;       -- Số ảnh "khó"
```

> ⚠️ **Lưu ý diễn đạt:** Dashboard này là **Application Monitoring Dashboard** (theo dõi hiệu năng hệ thống và hỗ trợ vòng lặp Active Learning). Không nên gọi là "MLOps Monitoring" đầy đủ — vì MLOps hoàn chỉnh còn bao gồm Model Registry, CI/CD, Drift Detection, Feature Store, Canary Deployment, Rollback... Đồ án không cần đến mức đó.

---

### ⚙️ Config Management — Không Hard-code

Dùng `pydantic-settings` (cách chuẩn của FastAPI) thay vì hard-code `API_KEY`, `MODEL_PATH` trong code:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_path: str = "checkpoints/best_model.pth"
    model_backbone: str = "efficientnet_b3"
    confidence_threshold: float = 0.4
    sqlite_db_path: str = "logs/predictions.db"
    log_dir: str = "logs"

    class Config:
        env_file = ".env"

settings = Settings()
```

Mọi config đều đọc từ file `.env` hoặc biến môi trường → dễ thay đổi khi deploy mà không cần sửa code.

---

### 🏥 Health Check Endpoint

```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model": "loaded",
        "vector_db": "connected",
        "uptime": "..."
    }
```

Khi deploy bằng Docker hoặc trên Cloud, Health Check là cách hệ thống tự kiểm tra "mình còn sống không".

---

### 🧬 Model Metadata Endpoint

```python
@app.get("/model/info")
def model_info():
    return {
        "name": "EfficientNet-B3",
        "version": "1.2.0",
        "num_classes": 43,
        "accuracy": 0.967,
        "trained_at": "2026-07-10",
        "dataset_size": 27868
    }
```

Khi retrain model (v1.0 → v1.1 → v1.2...), endpoint này giúp quản lý phiên bản rõ ràng. Hội đồng hỏi "model version nào?" → trả lời bằng API luôn.

---

### 🐳 Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./logs:/app/logs
      - ./checkpoints:/app/checkpoints
    env_file: .env
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
```

Demo chỉ cần `docker compose up` → toàn bộ hệ thống (React + FastAPI + ChromaDB) lên cùng lúc.

---

### 🔄 Vòng lặp Data Flywheel (Active Learning) — 5 Bước

```
📱 User upload ảnh
    ↓
🧠 API dự đoán + Log vào SQLite
    ↓
🔍 Script lọc ảnh confidence 40-70% (Data Edge Cases)
    ↓
🏷️ Đẩy ảnh "khó" lên Label Studio → Team gán nhãn (Human-in-the-loop)
    ↓
📦 Export JSON → apply_labels.py → Trộn vào Dataset gốc
    ↓
🔥 Retrain trên GPU → Model v1.x+1 → Thay best_model.pth
    ↓
🔁 Lặp lại
```

> Cách diễn đạt đúng khi bảo vệ đồ án: _"Nhóm xây dựng một Application Monitoring Dashboard để theo dõi hiệu năng hệ thống và hỗ trợ vòng lặp Active Learning, giúp model tự cải thiện qua mỗi chu kỳ sử dụng."_

---



## 🎬 Kịch bản Demo Chi Tiết cho Thầy (Tuần 3)

### Slide 1–3: Đặt vấn đề (3 phút)
- Bài toán: Việt Nam có 43+ món ăn đặc trưng, chụp 1 tấm ảnh làm sao nhận ra ngay?
- Thách thức: Ảnh thực tế (góc lạ, ánh sáng kém), dữ liệu mất cân bằng nặng.
- Giải pháp của nhóm: Pipeline 4 tầng Vision → Retrieval → RAG → Explainability.

### Slide 4–6: Pipeline & Dữ liệu (5 phút)
- Show cấu trúc dữ liệu 3 cấp (Bắc/Trung/Nam → Loại món → Tên món).
- Số liệu: ~28,577 ảnh gốc + ~5,600 ảnh crawl từ Cooky/Monngon.
- Quy trình gán nhãn (Label Studio, double-check, QA).

### Slide 7–9: Kết quả Model (5 phút)
- Bảng so sánh ResNet50 vs EfficientNet-B3 (accuracy / inference time / model size).
- **Grad-CAM live demo:** Đưa ảnh bún bò Huế vào → show vùng AI đang nhìn vào (màu đỏ = vùng quan trọng nhất).
- Confusion matrix: Chỉ ra những class hay bị nhầm (ví dụ: bún bò vs phở bò) và giải thích tại sao.

### Slide 10–11: CLIP + UMAP Visualization (3 phút)
- **UMAP demo:** Show bản đồ 2D của tất cả ảnh trong dataset — các món cùng loại cluster lại thành cụm rõ ràng.
- **CLIP search demo:** Gõ "spicy noodle soup" → ra ảnh Bún bò Huế / Bún riêu / Mì cay.

### Slide 12–13: Demo Live End-to-End (5 phút) ← Phần quan trọng nhất
**Kịch bản demo live (thực hiện trực tiếp trước thầy):**

1. Mở giao diện web (đã deploy bằng Docker hoặc FastAPI).
2. Upload ảnh chụp điện thoại thực tế (ảnh trong tập `test_realworld/`).
3. Hệ thống hiển thị:
   - Tên món ăn nhận diện được + confidence score.
   - Top-5 dự đoán.
   - Hình ảnh Grad-CAM overlay.
   - Top-3 công thức nấu ăn tương ứng từ RAG.
4. Thử thêm 2–3 ảnh khó (góc lạ, nhiều món trong 1 tấm) để show độ robust của model.

### Slide 14–15: Hướng phát triển (2 phút)
- Ngắn hạn: Tăng accuracy, thêm class mới.
- Dài hạn: Food Agent (LangGraph + Gemini API), Multimodal Search, App mobile.

---

## 📦 Repo tham khảo đáng đọc

| Repo | Điểm nổi bật | Áp dụng vào dự án |
|------|-------------|-------------------|
| [VLPCook](https://github.com/mshukor/VLPCook) | Image ↔ Recipe Cross-modal Retrieval | Học cách xây Joint Embedding cho CLIP + Retrieval |
| [clip-retrieval](https://github.com/rom1504/clip-retrieval) | CLIP + FAISS end-to-end | Clone pipeline này cho Visual Search |
| [clip-faiss](https://github.com/abinthomasonline/clip-faiss) | Nhỏ gọn, dễ hiểu, clone trong 1–2 ngày | Xây Text/Image Search cho demo |
| [Cook Assistant](https://github.com/zwe-htet-paing/cook-assistant) | RAG + Recipe QA có Chat UI | Tham khảo cấu trúc RAG production |
| [ChefMate AI](https://github.com/ThakkarVidhi/chefmate-ai) | Conversational Food Agent | Hướng phát triển dài hạn sau đồ án |

## 📄 Paper nên đọc

| Paper | Điểm đáng chú ý |
|-------|----------------|
| [FoodCHA (arXiv)](https://arxiv.org/abs/2605.05499) | Taxonomy 3 tầng **giống hệt** nhóm bạn đang dùng → dùng làm reference trong báo cáo |
| [FoodLMM (arXiv)](https://arxiv.org/abs/2312.14991) | Roadmap dài hạn của hệ thống Food AI hoàn chỉnh → dùng làm "Future Work" trong slide |
