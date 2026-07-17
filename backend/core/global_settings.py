from pydantic import BaseModel

class AppSettings(BaseModel):
    llm_engine: str = "Gemini 3.1 Flash Lite"
    vision_model: str = "MobileNetV3 (Fast)"
    top_k: int = 3

# Singleton instance to hold dynamic user settings in-memory
settings_store = AppSettings()
