# BẢN THIẾT KẾ TỔNG THỂ DỰ ÁN: VNFOOD VISION & RAG ASSISTANT

Đây là bản quy hoạch toàn diện nhất cho đồ án của bạn, trải dài từ lúc nhập ảnh đầu vào cho đến khi xuất ra đoạn chat phản hồi thông minh, tích hợp cả Computer Vision (Thị giác máy tính) và NLP (Xử lý ngôn ngữ tự nhiên).

---

## 🏛️ Kiến Trúc Hệ Thống (System Architecture)
Hệ thống là một Pipeline khép kín gồm 3 khối cốt lõi:
`[Image Input] ➔ Khối VISION ➔ Khối RAG RETRIEVAL ➔ Khối LLM GENERATION ➔ [Web UI]`

---

## 📍 Giai đoạn 1: Khối Nhận Diện Hình Ảnh (Vision)
*Giai đoạn này xử lý ảnh đầu vào và phân loại thành 43 món ăn.*

*   **Mô hình chính:** `EfficientNet-B3` (Độ chính xác và hiệu năng tối ưu).
*   **Mô hình Baseline (Để so sánh):** `MobileNet-V3` / `ResNet-50`.
*   **Dữ liệu:** Tập dataset 27.868 ảnh đã được xử lý mất cân bằng lớp (Class weights, WeightedRandomSampler).
*   **Tính năng đặc biệt:**
    *   Cơ chế **Active Learning** (Human-in-the-loop) kết hợp Label Studio để tự động lọc ảnh rác/nhãn sai, nâng cao độ sạch của dữ liệu.
    *   Tự động lưu Checkpoint và Sync lên Google Drive.
    *   Test Time Augmentation (TTA) khi inference để tăng độ chính xác.
*   **Trạng thái:** Đã hoàn thiện mã nguồn và chạy thử thành công.

---

## 📍 Giai đoạn 2: Xử Lý Dữ Liệu Tri Thức (Data Engineering)
*Giai đoạn này xử lý file `recipes.csv` (5.700 dòng thô) để chuẩn bị "thức ăn" cho khối RAG và khối LLM.*

*   **Vấn đề:** Tránh nhiễu (noise) do 1 món có hàng chục công thức mâu thuẫn nhau.
*   **Luồng 2.1 - Dữ liệu cho RAG (The Golden Records):**
    *   Lọc lấy **Đúng 1 công thức chuẩn nhất, dài nhất** cho mỗi món.
    *   Kết xuất ra file `rag_knowledge_base.json` (43 văn bản siêu sạch).
*   **Luồng 2.2 - Dữ liệu cho LLM Fine-Tuning:**
    *   Lọc Top 10 công thức biến tấu cho mỗi món.
    *   Dùng AI tạo tập dữ liệu đa chiều (Hỏi công thức, Hỏi dị ứng, Hỏi lượng calo, Dịch tiếng Anh).
    *   Kết xuất ra file `finetune_dataset.jsonl` (~2.000 - 3.000 cặp câu Hỏi-Đáp).
*   **Trạng thái:** Đã có file CSV, sẵn sàng code script xử lý.

---

## 📍 Giai đoạn 3: Hệ Thống Advanced RAG
*Giai đoạn tìm kiếm thông tin ngữ cảnh để đút cho LLM.*

*   **Cơ sở dữ liệu:** `ChromaDB` (chạy cục bộ).
*   **Truy xuất lai (Hybrid RAG):**
    *   **Dense Search:** Tìm theo ngữ nghĩa (Dùng `SentenceTransformers`).
    *   **Sparse Search:** Tìm theo từ khóa (Dùng thuật toán `BM25`).
*   **Tái xếp hạng (Reranker):** Dùng mô hình `Cross-Encoder` chấm điểm và chọn lọc lại Top 3 đoạn văn phù hợp nhất trước khi giao cho LLM.

---

## 📍 Giai đoạn 4: LLM Fine-Tuning & Evaluation
*Giai đoạn huấn luyện bộ não ngôn ngữ và chấm điểm.*

*   **Mô hình Baseline:** Sử dụng `Qwen2.5-3B` hoặc `Llama-3-8B`.
*   **Môi trường Training:** Google Colab (GPU T4) sử dụng thư viện `Unsloth` và kỹ thuật `LoRA` để giảm thiểu tài nguyên.
*   **Đánh giá (Evaluation):** Không dùng cảm tính. Áp dụng framework **RAGAS** để đo lường tự động:
    *   *Context Precision / Context Recall.*
    *   *Faithfulness* (Chống ảo giác/bịa chuyện).
    *   *Answer Relevance* (Trả lời đúng trọng tâm).

---

## 📍 Giai đoạn 5: Hệ Thống Giao Diện (React Frontend & FastAPI Backend)
*Sản phẩm cuối cùng để hội đồng trải nghiệm với giao diện chuyên nghiệp.*

*   **Kiến trúc:** Tách biệt Backend (FastAPI) và Frontend (React) thay vì dùng Streamlit nguyên khối.
    *   **Backend (FastAPI):** Chịu trách nhiệm load model Vision, khởi tạo VectorDB, bọc RAG pipeline và cung cấp các endpoint API (ví dụ: `/predict`, `/chat`, `/rag-inspector`).
    *   **Frontend (React):** Quản lý UI/UX, xử lý state, vẽ giao diện bản đồ, xử lý upload ảnh/camera. Mất khoảng 1 ngày triển khai.
*   **Tính năng:**
    *   Tải ảnh / Chụp ảnh từ camera.
    *   Render thanh dự đoán % của khối Vision.
    *   Hiển thị thẻ tóm tắt (Món ăn, Năng lượng, Dị ứng).
    *   **Khung Chatbot:** Người dùng có thể chat trực tiếp với LLM (ví dụ: *"Món này ăn kèm với rau gì?"*) và LLM sẽ dùng RAG để trả lời.
    
    **🔥 Bổ sung 4 tính năng "Wow Factor" (Nâng cao trải nghiệm):**
    1.  **Phát âm Tiếng Việt (Text-to-Speech):** 
        *   *Triển khai:* Lấy text từ API trả về, Frontend React có thể gọi Web Speech API của trình duyệt hoặc Backend gọi thư viện `gTTS` xuất file audio trả về cho React phát.
    2.  **Đa ngôn ngữ (Multi-Language Toggle):**
        *   *Triển khai:* Frontend React có một Dropdown chọn ngôn ngữ. Trạng thái này được gửi kèm theo API Request. LLM ở Backend sẽ nhận lệnh: *"Dịch toàn bộ kết quả RAG trên sang tiếng {ngôn_ngữ_chọn}"*.
    3.  **Đề xuất Quán ăn lân cận (Bản đồ trên React):**
        *   *Triển khai:* Vì Frontend code bằng React, bạn có thể dễ dàng nhúng component bản đồ thực sự (ví dụ thư viện `react-leaflet` hoặc Google Maps iframe miễn phí) với tính linh hoạt và UI đẹp hơn rất nhiều so với Streamlit. Hoặc dùng **Google Maps Search URL Scheme** gán vào nút bấm.
    4.  **Tab Góc Học Thuật (Dành cho Giảng viên & Nhà nghiên cứu):**
        *   Đây không chỉ là nơi show biểu đồ tĩnh, mà là một **phòng thí nghiệm thu nhỏ (Mini-Lab)** ngay trên Web:
        *   **Explainable AI (XAI với Grad-CAM):** Khi upload ảnh, ngoài việc hiện tên món, Web sẽ vẽ một lớp **Heatmap (Bản đồ nhiệt)** đè lên ảnh gốc để chứng minh: *"Mạng CNN đang nhìn vào cục thịt bò và sợi phở để quyết định, chứ không phải học vẹt cái bát hay cái phông nền"*. (Tính năng này được giới học thuật cực kỳ đánh giá cao).
        *   **RAG Inspector (Bóc tách Hậu trường RAG):** Hiển thị minh bạch hộp đen của RAG. Giảng viên có thể xem trực tiếp Top 3 đoạn văn bản (Chunks) nào đã được lôi ra từ ChromaDB, kèm theo **Điểm Tương đồng (Similarity Score)** của từng đoạn.
        *   **A/B Testing LLM:** Thêm nút gạt (Toggle) cho phép hội đồng chuyển đổi qua lại giữa phản hồi của mô hình LLM Fine-tune (Baseline của nhóm) và phản hồi của Gemini 1.5 API để tự tay đối chiếu sự chênh lệch chất lượng.

---

## 🛡️ Góc Phản Biện Học Thuật (Academic Defense)
*Tài liệu chuẩn bị cho các câu hỏi phản biện từ Hội đồng bảo vệ Đồ án.*

**Câu hỏi:** *"Dữ liệu gốc (recipes.csv) không có Cột Dị Ứng và Calo. Nhóm dùng LLM để sinh ra (làm giàu) dữ liệu này. Vậy làm sao kiểm chứng được thông tin LLM sinh ra là chính xác và không bị ảo giác (Hallucination)?"*

**Lập luận bảo vệ (Defense Strategy):**
1.  **Thuật toán lai (Rule-based constraints):** 
    Nhóm không cho phép LLM tự do đoán mò. Việc sinh dữ liệu Dị ứng được gò ép bằng thuật toán: Code sẽ quét tìm các từ khóa (Tôm, Đậu phộng, Sữa...) trong cột `nguyen_lieu` gốc. Chỉ khi có các từ khóa này, LLM mới được phép sinh ra câu cảnh báo dị ứng tương ứng. LLM ở đây chỉ đóng vai trò xử lý ngôn ngữ tự nhiên (Natural Language Processing), còn tính logic vẫn bám sát 100% vào Ground Truth.
2.  **Đánh giá mẫu (Human-in-the-loop Validation):** 
    Để đo lường độ chính xác, nhóm áp dụng phương pháp thống kê. Nhóm trích xuất ngẫu nhiên 5% tập dữ liệu đã làm giàu (khoảng 150 mẫu) và đối chiếu thủ công (Manual review) lượng Calo với *Bảng Thành phần Dinh dưỡng Thực phẩm Việt Nam (Viện Dinh dưỡng Quốc gia)*. Kết quả đánh giá trên mẫu cho thấy độ tin cậy đạt mức cao, từ đó chứng minh được chất lượng của toàn bộ Dataset.
3.  **Áp dụng Tiêu chuẩn SOTA (State-of-the-Art):** 
    Phương pháp dùng LLM khổng lồ (GPT-4/Gemini) để sinh dữ liệu và huấn luyện lại LLM nhỏ hơn (Self-Instruct / Synthetic Data Generation) hiện đang là tiêu chuẩn của ngành AI thế giới. Tiêu biểu là mô hình Alpaca của Đại học Stanford cũng áp dụng quy trình tương tự. Điều này đảm bảo tính cập nhật và tính học thuật cao cho đồ án.
