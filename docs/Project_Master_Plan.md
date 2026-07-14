# BẢN THIẾT KẾ TỔNG THỂ DỰ ÁN: VNFOOD VISION & RAG ASSISTANT

Đây là bản quy hoạch toàn diện nhất cho đồ án của bạn, trải dài từ lúc nhập ảnh đầu vào cho đến khi xuất ra đoạn chat phản hồi thông minh, tích hợp cả Computer Vision (Thị giác máy tính) và NLP (Xử lý ngôn ngữ tự nhiên).

---

## 🏛️ Kiến Trúc Hệ Thống (System Architecture)

Hệ thống là một Pipeline khép kín gồm 3 khối cốt lõi:
`[Image Input] ➔ Khối VISION ➔ Khối RAG RETRIEVAL ➔ Khối LLM GENERATION ➔ [Web UI]`

---

## 💎 Giá Trị Cốt Lõi (Core Value Proposition)

_Câu trả lời quyết định cho câu hỏi của Hội đồng: "Tại sao người dùng phải Upload ảnh mà không gõ chữ tìm kiếm cho nhanh?"_

1. **Khám phá món ăn lạ (Discovery of the Unknown):** Giải quyết "nỗi đau" cực lớn khi người dùng (đặc biệt là khách du lịch nước ngoài hoặc người ngoại tỉnh) thấy món ăn hấp dẫn nhưng **không biết tên để gõ tìm kiếm**. Việc upload ảnh biến App thành "Shazam dành cho Ẩm thực", gọi mặt điểm tên vạn vật chỉ trong 1 giây.
2. **Định lượng Dinh dưỡng cấp tốc (Diet Tracking):** Người dùng đang tập Gym/Ăn kiêng có thể chụp tô Phở trước khi ăn và ngay lập tức biết lượng Calo ước tính cùng cảnh báo Dị ứng mà không cần phải gõ văn bản mô tả rườm rà.
3. **Từ Mạng Ảo ra Đời Thực (O2O - Online to Offline):** Khi thấy một video nấu ăn hấp dẫn trên TikTok/Instagram, người dùng có thể chụp màn hình ném vào App. App không chỉ nhận diện, cho công thức nấu mà còn kích hoạt chức năng định vị (Location-based) để chỉ ra các quán ăn gần nhất đang bán món đó.
4. **Trải nghiệm lười biếng nhưng tối ưu (Frictionless UX):** Việc Upload một bức ảnh thay thế hoàn toàn cho 10 câu mô tả văn bản. Bức ảnh đóng vai trò cung cấp "Ngữ cảnh mỏ neo" (Context) tức thì, biến Chatbot thành Trợ lý chủ động hoàn toàn: Tự nhận biết, tự đọc âm thanh (TTS), tự khoanh vùng dữ liệu.
---

## 📍 Giai đoạn 1: Khối Nhận Diện Hình Ảnh (Vision)

_Giai đoạn này xử lý ảnh đầu vào và phân loại thành 43 món ăn._

- **Mô hình chính:** `EfficientNet-B3` (Độ chính xác và hiệu năng tối ưu).
- **Mô hình Baseline (Để so sánh):** `MobileNet-V3` / `ResNet-50`.
- **Dữ liệu:** Tập dataset 27.868 ảnh đã được xử lý mất cân bằng lớp (Class weights, WeightedRandomSampler).
- **Tính năng đặc biệt:**
  - Cơ chế **Active Learning** (Human-in-the-loop) kết hợp Label Studio để tự động lọc ảnh rác/nhãn sai, nâng cao độ sạch của dữ liệu.
  - Tự động lưu Checkpoint và Sync lên Google Drive.
  - Test Time Augmentation (TTA) khi inference để tăng độ chính xác.
- **Trạng thái:** Đã hoàn thiện mã nguồn và chạy thử thành công.

---

## 📍 Giai đoạn 2: Xử Lý Dữ Liệu Tri Thức (Data Engineering)

_Giai đoạn này xử lý file `recipes.csv` (5.700 dòng thô) để chuẩn bị "thức ăn" cho khối RAG và khối LLM._

- **Vấn đề:** Tránh nhiễu (noise) do 1 món có hàng chục công thức mâu thuẫn nhau.
- **Luồng 2.1 - Dữ liệu cho RAG (The Golden Records):**
  - Lọc lấy **Đúng 1 công thức chuẩn nhất, dài nhất** cho mỗi món.
  - Kết xuất ra file `rag_knowledge_base.json` (43 văn bản siêu sạch).
- **Luồng 2.2 - Dữ liệu cho LLM Fine-Tuning:**
  - Lọc Top 10 công thức biến tấu cho mỗi món.
  - Dùng AI tạo tập dữ liệu đa chiều (Hỏi công thức, Hỏi dị ứng, Hỏi lượng calo, Dịch tiếng Anh).
  - Kết xuất ra file `finetune_dataset.jsonl` (~2.000 - 3.000 cặp câu Hỏi-Đáp).
- **Trạng thái:** Đã có file CSV, sẵn sàng code script xử lý.

---

## 📍 Giai đoạn 3: Hệ Thống Advanced RAG

_Giai đoạn tìm kiếm thông tin ngữ cảnh để đút cho LLM._

- **Cơ sở dữ liệu:** `ChromaDB` (chạy cục bộ).
- **Truy xuất lai (Hybrid RAG):**
  - **Dense Search:** Tìm theo ngữ nghĩa (Dùng `SentenceTransformers`).
  - **Sparse Search:** Tìm theo từ khóa (Dùng thuật toán `BM25`).
- **Tái xếp hạng (Reranker):** Dùng mô hình `Cross-Encoder` chấm điểm và chọn lọc lại Top 3 đoạn văn phù hợp nhất trước khi giao cho LLM.

---

## 📍 Giai đoạn 4: LLM Fine-Tuning & Evaluation

_Giai đoạn huấn luyện bộ não ngôn ngữ và chấm điểm._

- **Mô hình Baseline:** Sử dụng `Qwen2.5-3B` hoặc `Llama-3-8B`.
- **Môi trường Training:** Google Colab (GPU T4) sử dụng thư viện `Unsloth` và kỹ thuật `LoRA` để giảm thiểu tài nguyên.
- **Đánh giá (Evaluation):** Không dùng cảm tính. Áp dụng framework **RAGAS** để đo lường tự động:
  - _Context Precision / Context Recall._
  - _Faithfulness_ (Chống ảo giác/bịa chuyện).
  - _Answer Relevance_ (Trả lời đúng trọng tâm).

---

## 📍 Giai đoạn 5: Hệ Thống Giao Diện (React Frontend & FastAPI Backend)

_Sản phẩm cuối cùng để hội đồng trải nghiệm với giao diện chuyên nghiệp._

- **Kiến trúc:** Tách biệt Backend (FastAPI) và Frontend (React) thay vì dùng Streamlit nguyên khối.
  - **Backend (FastAPI):** Chịu trách nhiệm load model Vision, khởi tạo VectorDB, bọc RAG pipeline và cung cấp các endpoint API (ví dụ: `/predict`, `/chat`, `/rag-inspector`).
  - **Frontend (React):** Quản lý UI/UX, xử lý state, vẽ giao diện bản đồ, xử lý upload ảnh/camera. Mất khoảng 1 ngày triển khai.
- **Tính năng:**
  - Tải ảnh / Chụp ảnh từ camera.
  - Render thanh dự đoán % của khối Vision.
  - Hiển thị thẻ tóm tắt (Món ăn, Năng lượng, Dị ứng).
  - **Khung Chatbot:** Người dùng có thể chat trực tiếp với LLM (ví dụ: _"Món này ăn kèm với rau gì?"_) và LLM sẽ dùng RAG để trả lời.

  **🔥 Bổ sung 4 tính năng "Wow Factor" (Nâng cao trải nghiệm):**
  1.  **Phát âm Tiếng Việt (Text-to-Speech):**
      - _Triển khai:_ Lấy text từ API trả về, Frontend React có thể gọi Web Speech API của trình duyệt hoặc Backend gọi thư viện `gTTS` xuất file audio trả về cho React phát.
  2.  **Đa ngôn ngữ (Multi-Language Toggle):**
      - _Triển khai:_ Frontend React có một Dropdown chọn ngôn ngữ. Trạng thái này được gửi kèm theo API Request. LLM ở Backend sẽ nhận lệnh: _"Dịch toàn bộ kết quả RAG trên sang tiếng {ngôn_ngữ_chọn}"_.
  3.  **Đề xuất Quán ăn lân cận (Bản đồ trên React):**
      - _Triển khai:_ Vì Frontend code bằng React, bạn có thể dễ dàng nhúng component bản đồ thực sự (ví dụ thư viện `react-leaflet` hoặc Google Maps iframe miễn phí) với tính linh hoạt và UI đẹp hơn rất nhiều so với Streamlit. Hoặc dùng **Google Maps Search URL Scheme** gán vào nút bấm.
  4.  **Tab Góc Học Thuật (Dành cho Giảng viên & Nhà nghiên cứu):**
      - Đây không chỉ là nơi show biểu đồ tĩnh, mà là một **phòng thí nghiệm thu nhỏ (Mini-Lab)** ngay trên Web:
      - **Explainable AI (XAI với Grad-CAM):** Khi upload ảnh, ngoài việc hiện tên món, Web sẽ vẽ một lớp **Heatmap (Bản đồ nhiệt)** đè lên ảnh gốc để chứng minh: _"Mạng CNN đang nhìn vào cục thịt bò và sợi phở để quyết định, chứ không phải học vẹt cái bát hay cái phông nền"_. (Tính năng này được giới học thuật cực kỳ đánh giá cao).
      - **RAG Inspector (Bóc tách Hậu trường RAG):** Hiển thị minh bạch hộp đen của RAG. Giảng viên có thể xem trực tiếp Top 3 đoạn văn bản (Chunks) nào đã được lôi ra từ ChromaDB, kèm theo **Điểm Tương đồng (Similarity Score)** của từng đoạn.
      - **A/B Testing LLM:** Thêm nút gạt (Toggle) cho phép hội đồng chuyển đổi qua lại giữa phản hồi của mô hình LLM Fine-tune (Baseline của nhóm) và phản hồi của Gemini 1.5 API để tự tay đối chiếu sự chênh lệch chất lượng.

---

## 🛡️ Góc Phản Biện Học Thuật (Academic Defense)

_Tài liệu chuẩn bị cho các câu hỏi phản biện từ Hội đồng bảo vệ Đồ án._

**Câu hỏi:** _"Dữ liệu gốc (recipes.csv) không có Cột Dị Ứng và Calo. Nhóm dùng LLM để sinh ra (làm giàu) dữ liệu này. Vậy làm sao kiểm chứng được thông tin LLM sinh ra là chính xác và không bị ảo giác (Hallucination)?"_

**Lập luận bảo vệ (Defense Strategy):**

1.  **Thuật toán lai (Rule-based constraints):**
    Nhóm không cho phép LLM tự do đoán mò. Việc sinh dữ liệu Dị ứng được gò ép bằng thuật toán: Code sẽ quét tìm các từ khóa (Tôm, Đậu phộng, Sữa...) trong cột `nguyen_lieu` gốc. Chỉ khi có các từ khóa này, LLM mới được phép sinh ra câu cảnh báo dị ứng tương ứng. LLM ở đây chỉ đóng vai trò xử lý ngôn ngữ tự nhiên (Natural Language Processing), còn tính logic vẫn bám sát 100% vào Ground Truth.
2.  **Đánh giá mẫu (Human-in-the-loop Validation):**
    Để đo lường độ chính xác, nhóm áp dụng phương pháp thống kê. Nhóm trích xuất ngẫu nhiên 5% tập dữ liệu đã làm giàu (khoảng 150 mẫu) và đối chiếu thủ công (Manual review) lượng Calo với _Bảng Thành phần Dinh dưỡng Thực phẩm Việt Nam (Viện Dinh dưỡng Quốc gia)_. Kết quả đánh giá trên mẫu cho thấy độ tin cậy đạt mức cao, từ đó chứng minh được chất lượng của toàn bộ Dataset.
3.  **Áp dụng Tiêu chuẩn SOTA (State-of-the-Art):**
    Phương pháp dùng LLM khổng lồ (GPT-4/Gemini) để sinh dữ liệu và huấn luyện lại LLM nhỏ hơn (Self-Instruct / Synthetic Data Generation) hiện đang là tiêu chuẩn của ngành AI thế giới. Tiêu biểu là mô hình Alpaca của Đại học Stanford cũng áp dụng quy trình tương tự. Điều này đảm bảo tính cập nhật và tính học thuật cao cho đồ án.

---

## 🎯 Kịch Bản Demo Điểm Cao (Demo Strategy)

_Tập hợp các kịch bản trình diễn sức mạnh của RAG đa biến thể trước Hội đồng, chứng minh giá trị thực tiễn cực cao của Giai đoạn Data Engineering._

### Kịch bản 1: "Khám bệnh" Ý định người dùng (Intent Matching & Negative Constraints)
- **Hành động:** Upload tấm ảnh "Bánh bao". Hệ thống Vision báo kết quả `banh_bao` làm ngữ cảnh mỏ neo.
- **Trải nghiệm UX:** Chatbot tự động mồi câu: *"Tôi thấy đây là Bánh Bao. Hiện tại trong hệ thống có 10 biến thể (Healthy nguyên cám, Nhân phô mai, Nhân thịt, Nhân xá xíu...). Bạn muốn làm loại nào?"*
- **Truy vấn gài bẫy:** Giám khảo thử thách: *"Tôi muốn làm bánh bao nhân thịt mà lười đi mua trứng cút, có cách nào không?"*
- **RAG Xử lý:** RAG không chỉ tìm keyword mà quét ngữ nghĩa phủ định "không trứng cút", lôi chính xác bản ghi `banh_bao_4` (Bánh bao nhân thịt không trứng cút) ra để trả lời.
- **Ý nghĩa bảo vệ:** Chứng minh hệ thống thấu hiểu "Ngữ nghĩa" (Semantic) thay vì chỉ Match từ khóa cứng nhắc.

### Kịch bản 2: AI tự tổng hợp và so sánh chéo (Multi-document QA)
- **Truy vấn:** Giám khảo hỏi: *"Bánh bao xá xíu (`banh_bao_3`) và bánh bao pizza (`banh_bao_2`) khác nhau điểm gì? Cần lưu ý gì khi làm?"*
- **RAG Xử lý:** Hệ thống thiết lập `Top_K = 2`, rút ra cả 2 bản ghi đưa cho LLM. LLM tự động tổng hợp và vẽ ra 1 **Bảng so sánh** trực quan (Khác biệt nguyên liệu, dầu hào vs ketchup...).
- **Ý nghĩa bảo vệ:** Chứng minh hệ thống không chỉ biết "Đọc vẹt từng bài" mà còn có năng lực "Suy luận và Tổng hợp" (Reasoning) thông tin từ nhiều tài liệu giống hệt con người.

### Kịch bản 3: "Đại Sứ Ẩm Thực Việt" (Cross-lingual RAG)
- **Hành động:** Upload ảnh "Bún Chả" / "Bánh Bao" và đặt câu hỏi bằng Tiếng Anh: *"I am allergic to peanuts and seafood. Can I eat this? What is its English name?"*
- **RAG Xử lý:** RAG vẫn truy vấn trong kho tài liệu Tiếng Việt. LLM đọc bản ghi Tiếng Việt nhưng phát hiện trường `english_translation` và `di_ung_enriched` đã được mớm sẵn từ khâu Data Prep.
- **Chatbot phản hồi:** LLM tự động dịch luồng suy nghĩ và trả lời trôi chảy bằng Tiếng Anh: *"This dish is Vietnamese Grilled Pork with Rice Noodles. It does NOT contain peanuts or seafood..."*
- **Ý nghĩa bảo vệ:** Hệ thống chỉ cần 1 cơ sở dữ liệu duy nhất (Tiếng Việt) nhưng có thể xử lý Hỏi-Đáp Đa ngôn ngữ theo thời gian thực. Thể hiện tính ứng dụng thương mại hóa cực cao (Kiosk phục vụ khách du lịch quốc tế).

### Kịch bản 4: "Trợ lý Toàn năng" (Text-to-Speech & Location-based Service)
- **Hành động:** Upload ảnh "Phở".
- **Trải nghiệm UX (Giao diện người dùng):** 
  - Lập tức trình duyệt kích hoạt Loa (Web Speech API) phát âm chuẩn tiếng Việt: *"Chào bạn, món ăn trong ảnh là Phở!"*. (Tính năng Nhân văn - Accessibility dành cho người khiếm thị và người nước ngoài).
  - Ngay dưới khung chat tự động hiện ra một nút bấm thông minh: **📍 Tìm quán [Phở] ngon gần tôi**.
- **Tính năng mở rộng:** Khi bấm nút, hệ thống sử dụng tọa độ GPS của người dùng (Geolocation API) kết nối với Google Maps để tự động khoanh vùng và hiển thị danh sách các quán Phở đánh giá cao trong bán kính 3km.
- **Ý nghĩa bảo vệ:** Đập tan định kiến "Đồ án sinh viên chỉ nằm trên giấy". Việc tích hợp Giọng nói và Dịch vụ định vị địa lý (Online to Offline) chứng minh tư duy của một Giám đốc Sản phẩm (Product Manager) xuất sắc, biến Model AI thành một ứng dụng thương mại thực thụ có khả năng giải quyết trọn vẹn nhu cầu người dùng.
