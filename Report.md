# BÁO CÁO PHÂN TÍCH CHUYÊN SÂU: ĐÁNH GIÁ MÔ HÌNH NHẬN DIỆN MÓN ĂN VIỆT NAM (VNFOOD VISION)

## 1. TỔNG QUAN VÀ BỐI CẢNH ĐÁNH GIÁ (EXECUTIVE SUMMARY)

Báo cáo này trình bày phân tích chi tiết về hiệu năng của hai kiến trúc mạng Convolutional Neural Networks (`MobileNet_V3_Large` và `EfficientNet_B3`) trên bài toán phân loại đa lớp (Multi-class Classification) với 43 món ăn đặc trưng của Việt Nam.

**Đặc tả tập dữ liệu kiểm thử (Test Set):**

- **Quy mô:** 3.935 hình ảnh độc lập (không trùng lặp với tập Train/Validation).
- **Phân phối:** Dữ liệu có sự mất cân bằng nhẹ (Imbalanced Data) giữa các class, thể hiện qua khoảng cách giữa Macro Avg và Weighted Avg.

### Bảng Tổng Hợp Chỉ Số Hiệu Năng (Metrics)

| Tiêu chí Đánh giá                    | Model 1: MobileNet_V3_Large | Model 2: EfficientNet_B3 | Chênh lệch |
| :----------------------------------- | :-------------------------: | :----------------------: | :--------: |
| **Accuracy (Độ chính xác tổng thể)** |       **0.92 (92%)**        |        0.88 (88%)        |  `+ 4.0%`  |
| **Macro Precision**                  |          **0.88**           |           0.84           |  `+ 4.0%`  |
| **Macro Recall**                     |          **0.88**           |           0.87           |  `+ 1.0%`  |
| **Macro F1-Score**                   |          **0.88**           |           0.85           |  `+ 3.0%`  |
| **Weighted F1-Score**                |          **0.92**           |           0.88           |  `+ 4.0%`  |

**Kết luận Kiến trúc:**
Sự vượt trội của `MobileNet_V3_Large` (92% Accuracy) so với `EfficientNet_B3` (88%) mang lại một insight kỹ thuật rất quan trọng: Đối với tập dữ liệu hiện tại, một mô hình có dung lượng (Model Capacity) quá lớn như EfficientNet_B3 có thể đã rơi vào trạng thái "Underfitting" ở những epoch đầu do thiếu dữ liệu hoặc cần số lượng epoch huấn luyện dài hơn rất nhiều (hơn 50-100 epochs) để hội tụ. Ngược lại, kiến trúc `MobileNet_V3_Large` với các block Squeeze-and-Excitation (SE) và hàm kích hoạt h-swish đã hội tụ xuất sắc, trích xuất chính xác đặc trưng mà không bị Overfitting.
👉 **Quyết định: Chọn MobileNet_V3_Large làm mô hình Production.**

![Biểu đồ so sánh tổng quan](./reports/so_sanh_tong_quan.png)

---

## 2. EXPERIMENT SETUP & HYPERPARAMETERS (CẤU HÌNH HUẤN LUYỆN)

Quá trình huấn luyện được thực thi trên môi trường Google Colab (GPU T4) sử dụng phương pháp Transfer Learning kết hợp Fine-tuning hai giai đoạn (đóng băng 5 epochs đầu và mở khóa toàn mạng sau đó).

### 2.1. Hàm mất mát (Loss Function)

Mô hình không sử dụng Cross-Entropy truyền thống mà nâng cấp lên **Focal Loss** ($\alpha=0.25, \gamma=2.0$) kết hợp cùng **Label Smoothing** ($0.1$).

- **Cơ chế Focal Loss:** Giải quyết triệt để bài toán mất cân bằng dữ liệu (Class Imbalance) vốn rất phổ biến ở các dataset thu thập từ thực tế. Tham số $\gamma=2.0$ ép mô hình giảm trọng số phạt ở các mẫu dễ (như Trà sữa, Bánh mì) và dồn toàn lực tập trung vào các "Hard Examples" (các món khó phân biệt như cụm Lẩu, cụm Gà).
- **Label Smoothing:** Thay vì ép mô hình phải tự tin tuyệt đối (đầu ra 1.0 cho đúng, 0.0 cho sai), nhãn được "làm mềm". Điều này giúp hạn chế sự tự tin thái quá (Overconfidence) của kiến trúc phân loại đối với các điểm nhiễu, từ đó gia tăng mạnh mẽ khả năng Generalization.

### 2.2. Thuật toán tối ưu (Optimization Algorithm)

Lựa chọn **AdamW** (Adam with Decoupled Weight Decay) làm thuật toán tối ưu hóa cốt lõi.

- **Tính ưu việt của AdamW:** Khác với Adam thông thường (cộng trực tiếp L2 Regularization vào hàm Loss gây nhiễu gradient), AdamW tách biệt phần Weight Decay (`1.0e-4`) ra khỏi bước tính gradient. Sự phân tách này giúp các trọng số (weights) được phạt (penalize) một cách độc lập và tinh tế hơn, mang lại khả năng tối ưu hóa mượt mà ngang ngửa SGD with Momentum nhưng vẫn giữ được tốc độ hội tụ siêu tốc đặc trưng của họ nhà Adam.
- **Điều hướng tốc độ học (LR Scheduler):** Triển khai **Cosine Annealing** kết hợp **3 Epochs Warmup**. Tốc độ học (Learning Rate) khởi động rất chậm ở 3 epochs đầu để tránh hiện tượng sốc gradient phá hỏng bộ trọng số Pre-trained. Sau đó, nó đẩy lên mức Max (`1.0e-3`) và lướt giảm dần theo đường cong hàm Cosine về mức Min (`1.0e-6`), giúp mô hình từ từ "hạ cánh" an toàn vào đáy điểm cực tiểu (Global Minima).

### 2.3. Lựa chọn Siêu tham số (Hyperparameters)

- **Input Resolution & Batch Size:** Kích thước đầu vào chuẩn `224x224` kết hợp `Batch Size = 16` là điểm "Sweet Spot" được tính toán để tối đa hóa tài nguyên VRAM (16GB) của GPU Tesla T4 trên Colab mà không gây ra lỗi tràn bộ nhớ (Out-of-Memory).
- **Dropout (0.3):** Áp dụng ở lớp Classifier cuối cùng, hoạt động như một màng lọc ngắt kết nối ngẫu nhiên 30% số lượng neuron trong quá trình Forward Pass. Đây là hàng rào phòng thủ cuối cùng để triệt tiêu hiện tượng Overfitting ở các lớp kết nối đầy đủ (Fully Connected Layers).

### 2.4. Data Augmentation Pipeline (Ép xung dữ liệu)

Để tăng tính chống chịu (Robustness) của mô hình trước các biến đổi ngoại cảnh, Pipeline áp dụng loạt kỹ thuật xử lý ảnh "hạng nặng":

- Trải qua bộ lọc **RandAugment** (n=2, m=9) kết hợp Gaussian Blur và Color Jitter để đa dạng hóa ánh sáng, góc chụp.
- **MixUp** ($\alpha=0.2$) và **CutMix** ($\alpha=1.0$): Trộn lẫn nhãn (labels) và ma trận pixel của các bức ảnh, tạo thành một vùng không gian siêu phẳng (hyper-plane) liên tục. Kỹ thuật này ép mô hình không được "học vẹt" bất kỳ vùng pixel tĩnh nào, giải thích lý do tại sao Test Accuracy lại bứt phá mạnh mẽ dù Train Accuracy ban đầu lẹt đẹt ở mức rất thấp.

---

## 3. PHÂN TÍCH ĐỘ HỘI TỤ (CONVERGENCE ANALYSIS)

### 3.1. MobileNet_V3_Large

![Biểu đồ quá trình Training của MobileNet](./reports/training_mobile_log.png)

- **Đồ thị Loss:** Validation Loss giảm đều đặn và luôn duy trì ở mức thấp hơn hoặc bám sát Training Loss. Đây là minh chứng tuyệt đối cho thấy kỹ thuật Regularization (MixUp, CutMix, Dropout) đã phát huy tối đa hiệu quả, giúp mô hình **không bị Overfitting**.
- **Đồ thị Accuracy:** Sự phân kỳ giữa Train Acc (thấp) và Val Acc (cao) phản ánh chính xác bản chất của việc ép xung dữ liệu (Heavy Augmentation). Mô hình học các đặc trưng cục bộ (local features) cực kỳ khó trong lúc train, nên dễ dàng vượt qua các bức ảnh sạch trong tập Validation/Test.

### 3.2. EfficientNet_B3

![Biểu đồ quá trình Training của EfficientNet](./reports/training_efficientnet_log.png)

- **Độ dao động:** Đường Validation Loss của EfficientNet có dấu hiệu rung lắc (fluctuations) mạnh hơn ở các epoch giữa. Điều này cho thấy thuật toán tối ưu (Optimizer) đang gặp khó khăn trong việc tìm điểm cực tiểu toàn cục (Global Minima) trong không gian siêu tham số của một mô hình quá lớn.

---

## 4. ERROR ANALYSIS & ACTIONABLE INSIGHTS

Mặc dù MobileNet đạt độ chính xác 92%, việc mổ xẻ 8% sai sót còn lại mang lại những hiểu biết cốt lõi về bản chất dữ liệu (Data Nature).

![Ma trận nhầm lẫn Confusion Matrix của MobileNet](./reports/confusion_matrix_mobile.png)

### 4.1. Nhóm hội tụ xuất sắc (F1 > 0.95)

Các món ăn đạt F1-score cực cao như **Trà sữa (1.00), Bánh mì (0.98), Cơm tấm (0.97)** có chung đặc điểm:

- **Inter-class Variance lớn:** Hình dáng vật lý (ống hút, ly nhựa của trà sữa; ổ bánh mì thuôn dài) hoàn toàn khác biệt so với phần còn lại của dataset.
- **Global Context ổn định:** Bối cảnh xuất hiện của các món này thường tĩnh và ít bị che khuất.

### 4.2. Điểm mù 1: Nhiễu Ngoại Cảnh & Cấu Trúc Hỗn Loạn (Nhóm Lẩu)

**Dữ liệu phân tích:**

- Lẩu hải sản (Recall: 0.69, F1: 0.69)
- Lẩu Thái (Recall: 0.91, nhưng Precision thấp -> F1: 0.80)
  **Nguyên nhân Kỹ thuật:**
- **Severe Occlusion (Bị che khuất vật lý):** Khói hơi nước bốc lên từ nồi lẩu làm thay đổi hoàn toàn giá trị pixel ở vùng trung tâm (Region of Interest), khiến thuật toán tích chập (Convolution) thu về các feature map mờ nhạt.
- **Visual Clutter (Độ nhiễu thị giác cao):** Một nồi lẩu chứa quá nhiều object nhỏ lẻ (tôm, nghêu, nấm, rau). Model bị quá tải thông tin và có xu hướng đoán bừa dựa trên màu sắc nước dùng (Broth color). Nếu nước lẩu hải sản bị ám màu đỏ/cam do ánh sáng đèn, model lập tức False Positive sang "Lẩu Thái".

### 4.3. Điểm mù 2: Thiếu Biến Thiên Giữa Các Lớp (Nhóm Cơm & Gà)

**Dữ liệu phân tích:**

- Cơm gà (F1: 0.75)
- Gà nướng (F1: 0.77), Cơm chiên (F1: 0.77)
  **Nguyên nhân Kỹ thuật:**
- **Low Inter-class Variance:** Color histogram (biểu đồ phân phối màu) của các món này gần như trùng khớp hoàn toàn (Tone Vàng/Nâu/Cam).
- **Mất bối cảnh toàn cục (Loss of Global Context):** Khi ảnh bị cắt (crop) quá cận vào miếng thịt gà nướng trên dĩa cơm, Receptive Field của mạng CNN chỉ nhìn thấy "Da gà nướng" mà không nhìn thấy "Hạt cơm". Dẫn đến mô hình tự tin dự đoán là món "Gà nướng" thay vì "Cơm gà".

### 4.4. Điểm mù 3: Khuyết Băng Tần Dữ Liệu (`banh_trang_tron`)

**Dữ liệu phân tích:** Support = 0, F1 = 0.00.
**Nguyên nhân Kỹ thuật:**

- Lỗi quy trình chia dữ liệu (Data Pipeline Splitting Flaw). Việc hàm `random_split` tạo ra tập Test hoàn toàn không chứa sample nào của class `banh_trang_tron` minh chứng cho sự thất bại trong việc cân bằng phân phối (Stratification). Trong môi trường Production, điều này dẫn đến rủi ro "Data Drift" không được kiểm chứng.

---

## 5. CHIẾN LƯỢC TỐI ƯU HÓA (ENGINEERING ACTION PLAN)

Để nâng cấp mô hình từ 92% lên mốc Production-grade >95%, hệ thống cần triển khai các giải pháp sau:

### Phase 1: Giải Pháp Tập Trung Dữ Liệu (Data-Centric Strategy)
1. **Hard Negative Mining:** Thiết lập hệ thống tự động cào (crawl) và gán nhãn bổ sung riêng biệt cho cụm "Cơm Gà / Gà Nướng" và "Lẩu Thái / Lẩu Hải Sản". Cố ý chọn các bức ảnh có góc chụp hiểm hóc để ép mô hình học đặc trưng biên (Edge features).
2. **Sửa lỗi Stratified K-Fold:** Thay thế hoàn toàn hàm `random_split` thông thường bằng `StratifiedShuffleSplit` của scikit-learn để đảm bảo tỷ lệ class phân bố đồng đều 100% xuyên suốt Train/Val/Test.

### Phase 2: Giải Pháp Tiền Xử Lý (Preprocessing Optimization)
1. **Dynamic Center Cropping:** Thay vì Resize và Crop tĩnh, cân nhắc áp dụng mạng phát hiện vật thể nhẹ (ví dụ: YOLOv8-nano) ở bước tiền xử lý để khoanh vùng (Bounding Box) chính xác trọng tâm món ăn, loại bỏ hoàn toàn nhiễu từ bát đĩa, khăn trải bàn hay khói bốc lên.
2. **Color Constancy Algorithms:** Áp dụng thuật toán cân bằng trắng hoặc xám hóa một phần (Color Jittering mạnh hơn) để triệt tiêu sự phụ thuộc của mô hình vào màu sắc nước dùng (Broth color bias) ở các món lẩu/bún.

### Phase 3: Deployment & MLOps
1. **Model Quantization:** Biến đổi trọng số mô hình `best_model.pth` từ FP32 (32-bit float) sang FP16 hoặc INT8 bằng TensorRT hoặc ONNX Runtime. Thao tác này có thể giảm dung lượng model xuống 4 lần và tăng tốc độ suy luận (Inference Speed) lên 2-3 lần trên CPU/Mobile mà không làm tụt Accuracy.
2. **API Endpointing:** Xây dựng luồng Inference sử dụng FastAPI, thiết lập cấu hình theo dõi thời gian thực (Prometheus/Grafana) để log lại các truy vấn mà mô hình trả về độ tự tin thấp (Confidence < 0.6) nhằm làm nguyên liệu học lại (Continuous Learning) sau này.
