#!/bin/bash
# =============================================================================
# startup.sh — Script khởi động Backend trên Render
# =============================================================================

# Đảm bảo hệ thống sử dụng cache model Hugging Face đã tải trong Build Phase
export HF_HOME="backend/data/hf_cache"

echo "============================================"
echo " VNFood Vision Backend — Startup Script"
echo "============================================"
echo " Starting FastAPI server on port ${PORT:-10000}..."
echo "============================================"

exec uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-10000}" \
    --workers 1 \
    --log-level info
