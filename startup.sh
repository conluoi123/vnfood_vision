#!/bin/bash
# =============================================================================
# startup.sh — Script khởi động Backend trên Render
# =============================================================================
# Lưu ý về HuggingFace repos:
#   - htvien/llm_model_vnfood: Qwen2 LLM (~6GB) — KHÔNG download (quá nặng)
#   - MobileNet best_model.pth: cần upload riêng lên HF nếu muốn dùng
#     endpoint /api/v1/predict/image
# Các endpoint RAG, History, Analytics, Places không cần local model.
# =============================================================================

set -e

MODEL_DIR="checkpoints/mobilenet_v3_large"
MODEL_FILE="$MODEL_DIR/best_model.pth"
HF_MOBILENET_REPO="${HF_MOBILENET_REPO:-}"  # Set env var nếu có repo chứa best_model.pth

echo "============================================"
echo " VNFood Vision Backend — Startup Script"
echo "============================================"

# --- Bước 1: Download MobileNet model (nếu có env var trỏ tới HF repo) ---
if [ ! -f "$MODEL_FILE" ]; then
    if [ -n "$HF_MOBILENET_REPO" ] && [ -n "$HF_MOBILENET_FILENAME" ]; then
        echo "[1/3] Đang tải MobileNet model từ HuggingFace: $HF_MOBILENET_REPO ..."
        mkdir -p "$MODEL_DIR"
        python3 -c "
from huggingface_hub import hf_hub_download
import os

local_path = hf_hub_download(
    repo_id='$HF_MOBILENET_REPO',
    filename='$HF_MOBILENET_FILENAME',
    local_dir='.'
)
print(f'  -> Download thành công: {local_path}')
"
        echo "[1/3] Done — Model đã được tải về."
    else
        echo "[1/3] SKIP — Không có HF_MOBILENET_REPO. Endpoint /predict/image sẽ không khả dụng."
        echo "      (Các endpoint RAG, History, Analytics vẫn hoạt động bình thường)"
    fi
else
    echo "[1/3] Model đã có sẵn."
fi

# --- Bước 2: Kiểm tra ChromaDB / RAG data ---
echo "[2/3] Kiểm tra ChromaDB / RAG data..."
if [ -f "backend/data/knowledge_base/rag_knowledge_base.json" ]; then
    echo "[2/3] Done — RAG knowledge base đã có sẵn."
else
    echo "[2/3] WARNING: Không tìm thấy RAG knowledge base."
    echo "             RAG chat features sẽ không hoạt động."
fi

# --- Bước 3: Khởi động FastAPI ---
echo "[3/3] Khởi động FastAPI server trên port ${PORT:-10000}..."
echo "============================================"

exec uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-10000}" \
    --workers 1 \
    --log-level info

