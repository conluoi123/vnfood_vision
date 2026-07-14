from urllib.parse import quote_plus

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/places", tags=["Places"])


class NearbySearchRequest(BaseModel):
    food_name: str = Field(..., min_length=1)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_km: float = Field(default=3.0, gt=0, le=50)


def build_google_maps_search_url(
    food_name: str,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float = 3.0,
) -> str:
    query = f"{food_name} quán ăn"

    if latitude is not None and longitude is not None:
        encoded_query = quote_plus(query)
        return (
            "https://www.google.com/maps/search/"
            f"{encoded_query}/@{latitude},{longitude},{14}z"
        )

    encoded_query = quote_plus(f"{query} gần tôi")
    return f"https://www.google.com/maps/search/{encoded_query}"


@router.post("/search-url")
def create_nearby_search_url(request: NearbySearchRequest):
    maps_url = build_google_maps_search_url(
        food_name=request.food_name,
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
    )

    return {
        "food_name": request.food_name,
        "radius_km": request.radius_km,
        "maps_url": maps_url,
        "provider": "google_maps_url",
        "requires_api_key": False,
    }
