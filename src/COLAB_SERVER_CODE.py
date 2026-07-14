# =========================================================================
# 1. Kết nối Google Drive và Tải mô hình
# =========================================================================
# Cài đặt thư viện
!pip install fastapi nest-asyncio pyngrok uvicorn pydantic transformers accelerate

from google.colab import drive
drive.mount('/content/drive')

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# CHÚ Ý: Đảm bảo đường dẫn này khớp với nơi bạn đã lưu model trong file 05_llm_finetune
SAVE_DIR = "/content/drive/MyDrive/VietFood-Project/checkpoints/llm/finetuned_model"

print("Đang tải model từ Google Drive (có thể mất 1-2 phút)...")
tokenizer = AutoTokenizer.from_pretrained(SAVE_DIR)
model = AutoModelForCausalLM.from_pretrained(
    SAVE_DIR,
    device_map="auto",
    torch_dtype=torch.float16
)
print("✅ Tải model thành công!")

# =========================================================================
# 2. Khởi tạo FastAPI và Ngrok
# =========================================================================
import nest_asyncio
from pyngrok import ngrok
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json

# --- ĐIỀN NGROK AUTH TOKEN CỦA BẠN VÀO ĐÂY ---
# Vào trang https://dashboard.ngrok.com/get-started/your-authtoken để lấy mã
NGROK_AUTH_TOKEN = "3EP8J1KIjs0FgJVMcNQlYsIAetc_6Jag4EKL93PHeGDQxHbNv"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

app = FastAPI()

# Cho phép tất cả các nguồn gửi yêu cầu tới (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    dish_name: str
    context_str: str

# =========================================================================
# 3. Định nghĩa đường dẫn /chat để nhận yêu cầu từ máy tính của bạn
# =========================================================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Chuẩn bị Prompt giống như lúc bạn train mô hình
    prompt = f"""Dưới đây là một câu hỏi về món ăn Việt Nam, kèm theo danh sách nguyên liệu. Hãy trả lời chính xác và ngắn gọn.

### Câu hỏi:
Dựa vào các thông tin sau, hãy trả lời về món {request.dish_name}:
{request.query}
Hãy trả lời ngắn gọn trong 1-2 câu. Không lặp lại đề bài.

### Nguyên liệu:
{request.context_str}

### Trả lời:
"""
    # Gửi vào mô hình Qwen2.5 đã train
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.3,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    
    # Xử lý đoạn text trả về
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)
    
    # Cắt bỏ các đuôi dư thừa nếu có
    if "###" in response:
        response = response.split("###")[0]
    elif "<|im_end|>" in response:
        response = response.split("<|im_end|>")[0]
        
    return {"reply": response.strip()}

# =========================================================================
# =========================================================================
# 4. Khởi chạy Server
# =========================================================================
import threading
import time

# Mở một đường hầm qua cổng 8000
public_url = ngrok.connect(8000).public_url

print("\n" + "=" * 80)
print(f"🚀 SERVER LLM ĐÃ SẴN SÀNG TẠI LINK DƯỚI ĐÂY:")
print(f"👉 {public_url} 👈")
print("Hãy COPY link này và dán vào file .env ở máy tính của bạn (Dòng COLAB_LLM_URL=...)")
print("=" * 80 + "\n")

# Chạy Uvicorn trong một luồng (thread) riêng để không bị đụng độ asyncio của Colab
def run_server():
    # nest_asyncio có thể vẫn hữu ích ở thread phụ nếu uvicorn cần
    import nest_asyncio
    nest_asyncio.apply()
    
    import os
    # Tiêu diệt tiến trình đang chạy ở port 8000 (nếu có) do bạn lỡ bấm chạy nhiều lần
    os.system("fuser -k 8000/tcp")
    import time
    time.sleep(2)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

thread = threading.Thread(target=run_server)
thread.start()

# Giữ cell luôn chạy để Server không bị tắt
while True:
    time.sleep(100)
