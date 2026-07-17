from backend.api.health import router as health_router
from backend.api.places import router as places_router
from backend.api.rag import router as rag_router
from backend.api.history import router as history_router
from backend.api.analytics import router as analytics_router
from backend.api.settings import router as settings_router

__all__ = ["health_router", "places_router", "rag_router", "history_router", "analytics_router", "settings_router"]
