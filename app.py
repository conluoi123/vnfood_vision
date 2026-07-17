import os
import uvicorn
from backend.main import app

if __name__ == "__main__":
    # Hugging Face Spaces Gradio yêu cầu chạy ở cổng 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
