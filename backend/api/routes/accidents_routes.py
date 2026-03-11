"""
    Handles all the routes linked to accidents (read-only).
"""

#
#   Imports
#

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
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
    date_from: Annotated[
        date | None,
        Query(description="Start date (inclusive)"),
    ] = None,
    date_to: Annotated[
        date | None,
        Query(description="End date (inclusive)"),
    ] = None,
) -> list[HeatmapPoint]:
    """
        Returns the list of accidents as heatmap points (lat, lng, count=1).
        Optional date filter: date_from (inclusive), date_to (inclusive).
    """

    try:
        return await accidents_service.get_heatmap_data(
            date_from=date_from,
            date_to=date_to,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
