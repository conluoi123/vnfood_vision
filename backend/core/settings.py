from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "VNFood Vision API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]


settings = Settings()
