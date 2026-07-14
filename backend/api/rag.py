from functools import lru_cache
from typing import List, Dict, Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGInspectorRequest(BaseModel):
    query: str = Field(..., min_length=1)

class AnalyzeFoodRequest(BaseModel):
    dishKey: Optional[str] = None
    image: Optional[str] = None
    language: str = "VN"

class ChatRagRequest(BaseModel):
    message: str
    dishKey: str = "pho"
    dishName: Optional[str] = None
    history: List[Dict[str, Any]] = []
    language: str = "VN"

@lru_cache(maxsize=1)
def get_rag_service():
    from backend.core.rag_service import RAGService
    return RAGService()


@router.post("/inspector")
def inspect_rag(request: RAGInspectorRequest):
    service = get_rag_service()
    return service.inspect(request.query)

@router.post("/analyze-food")
def analyze_food(request: AnalyzeFoodRequest):
    service = get_rag_service()
    # Nếu có ảnh upload mà không có dishKey thì tự set là "custom"
    dish_key = request.dishKey if request.dishKey else ("custom" if request.image else "pho")
    return service.analyze_food(dish_key, request.image, request.language)

class AnalyzeNutritionRequest(BaseModel):
    dishName: str

@router.post("/analyze-nutrition")
def analyze_nutrition(request: AnalyzeNutritionRequest):
    service = get_rag_service()
    return service.analyze_nutrition(request.dishName)

@router.post("/chat-rag")
def chat_rag(request: ChatRagRequest):
    service = get_rag_service()
    return service.chat_with_rag(request.message, request.dishKey, request.history, request.dishName, request.language)

class TTSRequest(BaseModel):
    text: str

@router.post("/tts")
def text_to_speech(request: TTSRequest):
    from fastapi.responses import StreamingResponse
    import io
    try:
        from gtts import gTTS
        tts = gTTS(text=request.text, lang='vi')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return StreamingResponse(mp3_fp, media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS error: {e}")
        return {"error": str(e)}

@router.get("/logs")
def get_system_logs(limit: int = 50):
    from backend.core.logger import get_logs
    return get_logs(limit)
