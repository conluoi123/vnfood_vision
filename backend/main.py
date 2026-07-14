from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import router as api_router

app = FastAPI(
    title="VNFood Vision API",
    description="Backend API phục vụ nhận diện món ăn Việt Nam",
    version="1.0.0"
)

# Cấu hình CORS để Frontend (React/Vite) có thể gọi được API mà không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế nên để ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router (API con)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to VNFood Vision API. Server is running!"}
