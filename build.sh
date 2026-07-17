#!/bin/bash
# =============================================================================
# build.sh — Script build trên Render (Build Phase)
# =============================================================================
# Tất cả các tác vụ tải model, cài đặt thư viện và khởi tạo database
# phải chạy ở đây để tránh block việc khởi động cổng mạng (port binding) ở startup.
# =============================================================================

set -e

# Thiết lập HF_HOME vào thư mục dự án để lưu cache model Hugging Face
export HF_HOME="backend/data/hf_cache"
mkdir -p "$HF_HOME"

echo "============================================"
echo " [Build] Cài đặt dependencies..."
echo "============================================"
pip install --no-cache-dir -r requirements-deploy.txt

# Cài đặt gdown để tải model từ Google Drive
pip install -q gdown

echo "============================================"
echo " [Build] Kiểm tra & tải các model checkpoints..."
echo "============================================"
MOBILENET_DIR="checkpoints/mobilenet_v3_large"
MOBILENET_FILE="$MOBILENET_DIR/best_model.pth"
EFFICIENTNET_DIR="checkpoints/efficientnet_b3"
EFFICIENTNET_FILE="$EFFICIENTNET_DIR/best_model.pth"

# 1. Tải MobileNetV3
if [ -n "$GDRIVE_MOBILENET_ID" ]; then
    echo " -> Đang tải MobileNetV3 checkpoint (ID: $GDRIVE_MOBILENET_ID)..."
    mkdir -p "$MOBILENET_DIR"
    gdown --id "$GDRIVE_MOBILENET_ID" -O "$MOBILENET_FILE" --fuzzy || echo " WARNING: Tải MobileNetV3 thất bại!"
else
    echo " -> SKIP: Không tìm thấy biến GDRIVE_MOBILENET_ID."
fi

# 2. Tải EfficientNetB3
if [ -n "$GDRIVE_EFFICIENTNET_ID" ]; then
    echo " -> Đang tải EfficientNetB3 checkpoint (ID: $GDRIVE_EFFICIENTNET_ID)..."
    mkdir -p "$EFFICIENTNET_DIR"
    gdown --id "$GDRIVE_EFFICIENTNET_ID" -O "$EFFICIENTNET_FILE" --fuzzy || echo " WARNING: Tải EfficientNetB3 thất bại!"
else
    echo " -> SKIP: Không tìm thấy biến GDRIVE_EFFICIENTNET_ID."
fi

echo "============================================"
echo " [Build] Khởi tạo ChromaDB RAG Index..."
echo "============================================"
if [ -f "backend/data/knowledge_base/rag_knowledge_base.json" ]; then
    echo " -> Đang chạy build_index()..."
    python3 -c "
import sys
sys.path.insert(0, '.')
from src.rag.rag_index import build_index
build_index()
"
    echo " -> Done: ChromaDB index đã được build thành công."
else
    echo " -> WARNING: Không thấy file rag_knowledge_base.json. Bỏ qua bước build index."
fi

echo "============================================"
echo " [Build] Hoàn tất quá trình Build thành công!"
echo "============================================"
