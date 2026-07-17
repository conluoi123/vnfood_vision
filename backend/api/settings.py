from fastapi import APIRouter
from backend.core.global_settings import settings_store
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingsUpdateRequest(BaseModel):
    llmEngine: str
    visionModel: str
    topK: int

@router.post("/update")
def update_settings(request: SettingsUpdateRequest):
    settings_store.llm_engine = request.llmEngine
    settings_store.vision_model = request.visionModel
    settings_store.top_k = request.topK
    
    return {
        "success": True, 
        "message": "Settings updated successfully",
        "current_settings": {
            "llmEngine": settings_store.llm_engine,
            "visionModel": settings_store.vision_model,
            "topK": settings_store.top_k
        }
    }
