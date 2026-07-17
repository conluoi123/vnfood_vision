import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.endpoints import router as api_router
from backend.api import health_router, places_router, rag_router, history_router, analytics_router, settings_router
from backend.core import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="VNFood Vision API - " + settings.app_name,
        description="Backend API phục vụ nhận diện món ăn Việt Nam",
        version=settings.app_version,
    )

    # Cấu hình CORS để Frontend (React/Vite) có thể gọi được API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Trong thực tế nên để ["http://localhost:5173"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def read_root():
        return {"message": "Welcome to VNFood Vision API. Server is running!"}

    # Đăng ký các router (API con)
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(health_router)
    app.include_router(places_router, prefix=settings.api_prefix)
    app.include_router(rag_router, prefix=settings.api_prefix)
    app.include_router(history_router, prefix=settings.api_prefix)
    app.include_router(analytics_router, prefix=settings.api_prefix)
    app.include_router(settings_router, prefix=settings.api_prefix)
    
    return app

app = create_app()
