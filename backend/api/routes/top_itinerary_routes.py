

#
#   Imports
#

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

# Perso

from api.deps import get_top_itineraries_service
from models.top_itinerary import TopItinerary
from services.top_itinerary_service import TopItineraryService


#
#   Routes
#

router = APIRouter(prefix="/itineraries")


@router.get(
    "/TopItinerary",
    description="Returns every itineraries without duplicates (start lat, start lng, end lat, end lng).",
)
async def get_top_itineraries(
    top_itineraries_service: TopItineraryService = Depends(get_top_itineraries_service),

) -> list[TopItinerary]:
    """
        Returns the list of itineraries (start lat, start lng, end lat, end lng).
    """

    try:
        return await top_itineraries_service.get_top_itineraries()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
