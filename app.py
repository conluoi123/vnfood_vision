import gradio as gr
from backend.main import app as fastapi_app

# Tạo một giao diện Gradio ảo cực nhẹ để "Lừa" Hugging Face
with gr.Blocks() as demo:
    gr.Markdown("# 🍜 VNFood API Backend đang chạy rất ổn định!")
    gr.Markdown("Đây là máy chủ AI dành cho frontend Vercel. Giao diện này chỉ dùng để giữ cho máy chủ luôn sống.")
    gr.Markdown("Các API chính nằm ở đường dẫn `/api/v1`")

# Gắn giao diện ảo này vào FastAPI của chúng ta
app = gr.mount_gradio_app(fastapi_app, demo, path="/")
