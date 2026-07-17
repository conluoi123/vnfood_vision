#!/bin/bash
# =============================================================================
# startup.sh — Script khởi động Backend trên Render
# =============================================================================
# Model checkpoints được lưu trên Google Drive và tải về khi deploy:
#   - GDRIVE_MOBILENET_ID : File ID của MobileNetV3 best_model.pth
#   - GDRIVE_EFFICIENTNET_ID : File ID của EfficientNetB3 best_model.pth
#
# Các endpoint RAG, History, Analytics, Places không cần local model.
# =============================================================================

# set -e is intentionally NOT used here so that download failures do not
# abort the startup — the server starts with mock fallbacks when models are missing.

MOBILENET_DIR="checkpoints/mobilenet_v3_large"
MOBILENET_FILE="$MOBILENET_DIR/best_model.pth"

EFFICIENTNET_DIR="checkpoints/efficientnet_b3"
EFFICIENTNET_FILE="$EFFICIENTNET_DIR/best_model.pth"

echo "============================================"
echo " VNFood Vision Backend — Startup Script"
echo "============================================"

# --- Bước 0: Cài gdown nếu chưa có ---
if ! command -v gdown &> /dev/null; then
    echo "[0/4] Đang cài đặt gdown để tải file từ Google Drive..."
    pip install -q gdown
    echo "[0/4] Done — gdown đã sẵn sàng."
else
    echo "[0/4] gdown đã có sẵn."
fi

# --- Bước 1: Download MobileNetV3 model ---
if [ ! -f "$MOBILENET_FILE" ]; then
    if [ -n "$GDRIVE_MOBILENET_ID" ]; then
        echo "[1/4] Đang tải MobileNetV3 checkpoint từ Google Drive (ID: $GDRIVE_MOBILENET_ID)..."
        mkdir -p "$MOBILENET_DIR"
        gdown --id "$GDRIVE_MOBILENET_ID" -O "$MOBILENET_FILE" --fuzzy
        if [ -f "$MOBILENET_FILE" ]; then
            echo "[1/4] Done — MobileNetV3 checkpoint đã được tải về: $MOBILENET_FILE"
        else
            echo "[1/4] WARNING: Tải MobileNetV3 thất bại. Endpoint nhận diện ảnh sẽ dùng fallback mock."
        fi
    else
        echo "[1/4] SKIP — Không có GDRIVE_MOBILENET_ID. Endpoint /predict/image sẽ dùng fallback mock."
        echo "      (Các endpoint RAG, History, Analytics vẫn hoạt động bình thường)"
    fi
else
    MOBILENET_SIZE=$(du -sh "$MOBILENET_FILE" | cut -f1)
    echo "[1/4] MobileNetV3 checkpoint đã có sẵn ($MOBILENET_SIZE)."
fi

# --- Bước 2: Download EfficientNetB3 model ---
if [ ! -f "$EFFICIENTNET_FILE" ]; then
    if [ -n "$GDRIVE_EFFICIENTNET_ID" ]; then
        echo "[2/4] Đang tải EfficientNetB3 checkpoint từ Google Drive (ID: $GDRIVE_EFFICIENTNET_ID)..."
        mkdir -p "$EFFICIENTNET_DIR"
        gdown --id "$GDRIVE_EFFICIENTNET_ID" -O "$EFFICIENTNET_FILE" --fuzzy
        if [ -f "$EFFICIENTNET_FILE" ]; then
            echo "[2/4] Done — EfficientNetB3 checkpoint đã được tải về: $EFFICIENTNET_FILE"
        else
            echo "[2/4] WARNING: Tải EfficientNetB3 thất bại. Endpoint nhận diện ảnh sẽ dùng fallback mock."
        fi
    else
        echo "[2/4] SKIP — Không có GDRIVE_EFFICIENTNET_ID."
    fi
else
    EFFICIENTNET_SIZE=$(du -sh "$EFFICIENTNET_FILE" | cut -f1)
    echo "[2/4] EfficientNetB3 checkpoint đã có sẵn ($EFFICIENTNET_SIZE)."
fi

# --- Bước 3: Kiểm tra ChromaDB / RAG data ---
echo "[3/4] Kiểm tra ChromaDB / RAG data..."
if [ -f "backend/data/knowledge_base/rag_knowledge_base.json" ]; then
    echo "[3/4] Done — RAG knowledge base đã có sẵn."
else
    echo "[3/4] WARNING: Không tìm thấy RAG knowledge base."
    echo "             RAG chat features sẽ không hoạt động."
fi

# Kiểm tra ChromaDB index đã build chưa
if [ -d "backend/data/chroma_db" ]; then
    echo "[3/4] ChromaDB index đã có sẵn."
else
    echo "[3/4] ChromaDB index chưa có. Đang khởi tạo RAG index từ knowledge base..."
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from src.rag.rag_index import build_index
    build_index()
    print('  -> ChromaDB index đã được build thành công!')
except Exception as e:
    print(f'  -> WARNING: Không thể build ChromaDB index: {e}')
    print('  -> RAG chat có thể không hoạt động đầy đủ.')
" || echo "[3/4] WARNING: Build ChromaDB index thất bại. RAG chat có thể bị hạn chế."
fi

# --- Bước 4: Khởi động FastAPI ---
echo "[4/4] Khởi động FastAPI server trên port ${PORT:-10000}..."
echo "============================================"
echo " Backend URL: http://0.0.0.0:${PORT:-10000}"
echo " Swagger UI : http://0.0.0.0:${PORT:-10000}/docs"
echo "============================================"

exec uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-10000}" \
    --workers 1 \
    --log-level info
