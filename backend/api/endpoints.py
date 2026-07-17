import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
import sys
from pathlib import Path

# Thêm root dự án vào path để có thể import src.vision.inference
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Lazy import: không import lúc khởi động để tránh crash server
# khi model chưa có hoặc dependencies chưa load được
_predict_fn = None
_predict_error = None

def _get_predict():
    """Load hàm predict theo kiểu lazy — chỉ load khi thực sự cần."""
    global _predict_fn, _predict_error
    if _predict_fn is not None:
        return _predict_fn
    if _predict_error is not None:
        raise _predict_error
    try:
        from src.vision.inference import predict
        _predict_fn = predict
        return _predict_fn
    except Exception as e:
        import traceback
        traceback.print_exc()
        _predict_error = e
        raise e

router = APIRouter()

@router.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên một file ảnh hợp lệ.")

    # Kiểm tra predict function có khả dụng không
    try:
        predict = _get_predict()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Vision model không khả dụng trên server này: {str(e)}"
        )

    # Lưu file ảnh do Frontend gửi lên vào thư mục tạm
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
            
        # Ở Windows, BẮT BUỘC phải thoát khỏi lệnh `with` (đóng file tạm) 
        # thì hàm Image.open() bên trong predict mới đọc được file, nếu không sẽ bị PermissionError!

        # Đường dẫn tuyệt đối đến config và model
        config_path = str(root_dir / "configs" / "config.yaml")
        model_path = str(root_dir / "checkpoints" / "mobilenet_v3_large" / "best_model.pth")
        
        # Gọi hàm predict từ mô hình AI
        results = predict(
            image_path=tmp_path,
            config_path=config_path,
            use_tta=False, # Tắt TTA để API phản hồi tức thời
            model_path_override=model_path
        )

        # Xóa file tạm để dọn dẹp ổ cứng
        os.remove(tmp_path)

        if not results:
            return {"success": False, "message": "Không thể nhận diện ảnh này."}

        # Lấy kết quả Top 1
        best_match = results[0]
        confidence = best_match.get("confidence", 0)

        # Bộ lọc Confidence: Dưới 40% thì coi như ảnh lạ/ngoài phân phối
        if confidence < 0.4:
            class_name = "Unrecognized Object"
        else:
            class_name = best_match.get("class", "Unknown").replace("_", " ").title()

        # Trả về Frontend
        return {
            "success": True,
            "data": {
                "class_name": class_name,
                "confidence": confidence,
                "nutrition": {
                    "calories": 450,
                    "protein": 30,
                    "carbs": 60,
                    "fat": 12,
                    "allergen": "Tùy món"
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

