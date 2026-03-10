"""
    Handles all the routes linked to accidents (read-only).
"""

#
#   Imports
#

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

# Perso

from api.deps import get_accidents_service
from models.heatmap_point import HeatmapPoint
from services.accidents_services import AccidentsService

#
#   Routes
#

router = APIRouter(prefix="/accidents")


@router.get(
    "/heatmap",
    description="Returns accident positions for heatmap (lat, lng, count).",
)
async def get_accidents_heatmap(
    accidents_service: AccidentsService = Depends(get_accidents_service),
) -> list[HeatmapPoint]:
    """
        Returns the list of accidents as heatmap points (lat, lng, count=1).
    """

    try:
        return await accidents_service.get_heatmap_data()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
