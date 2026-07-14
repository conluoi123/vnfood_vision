from fastapi import APIRouter


router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    return {
        "name": "VNFood Vision API",
        "status": "running",
    }


@router.get("/health")
def health():
    return {"status": "ok"}
