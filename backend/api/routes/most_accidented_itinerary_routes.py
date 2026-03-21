#
#   Imports
#

from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from typing import List, Optional
from datetime import date

# Perso

from services.most_accidented_itinerary import MostAccidentedItineraryService
from models.itinerary import Itinerary
from api.deps import get_mai_service
from enums.bikes_acc_type import BikeAccType

#
#   Routes  
#

router = APIRouter(prefix="/mai")

@router.get(
    "/topn",
    description="Returns the most accidented itinerary.",
    response_model=List[Itinerary],
)
async def get_top_n_accidented_itinerary(
    n: int = Query(default=5, description="Number of itineraries to return"),
    date_from: Optional[date] = Query(default=None, description="Start date"),
    date_to: Optional[date] = Query(default=None, description="End date"),
    mai_service: MostAccidentedItineraryService = Depends(get_mai_service),
    bike_acc_type: Optional[BikeAccType] = Query(
        default=None,
        description="The type of bike accident to include (None then all accidents including cars)",
    ),
):
    try:
        return await mai_service.get_top_n_accidented_itinerary(n, date_from, date_to, bike_acc_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
