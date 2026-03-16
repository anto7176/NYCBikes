

#
#   Imports
#

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

# Perso

from api.deps import get_unique_itineraries_service
from models.unique_itinerary import UniqueItinerary
from services.unique_itinerary_service import UniqueItineraryService


#
#   Routes
#

router = APIRouter(prefix="/itineraries")


@router.get(
    "/UniqueItinerary",
    description="Returns every itineraries without duplicates (start lat, start lng, end lat, end lng).",
)
async def get_unique_itineraries(
    unique_itinerary_service: UniqueItineraryService = Depends(get_unique_itineraries_service),

) -> list[UniqueItinerary]:
    """
        Returns the list of itineraries (start lat, start lng, end lat, end lng).
    """

    try:
        return await unique_itinerary_service.get_unique_itineraries()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
