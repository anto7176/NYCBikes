"""
    Service for reading accident data from the database.
"""

#
#   Imports
#

from datetime import date, datetime
from typing import Any
from pymongo import AsyncMongoClient

# Perso

from config.config import get_settings
from models.heatmap_point import HeatmapPoint
from enums.bikes_acc_type import BikeAccType

#
#   Constants
#

LAT_FIELD = "LATITUDE"
LNG_FIELD = "LONGITUDE"
STARTED_AT_FIELD = "started_at"

settings = get_settings()

#
#   AccidentsService
#

class AccidentsService:
    """
        Service to read accidents from the database.
    """

    def __init__(self, db: AsyncMongoClient[Any]):
        self._db = db[settings.DB_NAME]

    async def get_heatmap_data(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        bike_acc_type: BikeAccType | None = None,
    ) -> list[HeatmapPoint]:
        """
            Returns accident positions in heatmap format (lat, lng, count).

            Params:
                - date_from: Start date (inclusive). If None, no lower bound.
                - date_to: End date (inclusive). If None, no upper bound.
                - bikes_only: Whether to only include bikes accidents.

            Returns:
                - List of HeatmapPoint (count is always 1).
        """

        query: dict[str, Any] = {}
        if date_from is not None or date_to is not None:
            query[STARTED_AT_FIELD] = {}
            if date_from is not None:
                dt_from = datetime.combine(date_from, datetime.min.time())
                query[STARTED_AT_FIELD]["$gte"] = dt_from
            if date_to is not None:
                dt_to = datetime.combine(date_to, datetime.max.time())
                query[STARTED_AT_FIELD]["$lte"] = dt_to

        if bike_acc_type is not None:
            if bike_acc_type == BikeAccType.BIKE_INJURED:
                query["NUMBER OF CYCLIST INJURED"] = 1
            elif bike_acc_type == BikeAccType.BIKE_KILLED:
                query["NUMBER OF CYCLIST KILLED"] = 1

        cursor = self._db["accidents"].find(
            query,
            projection={LAT_FIELD: 1, LNG_FIELD: 1}
        )

        result: list[HeatmapPoint] = []
        async for doc in cursor:
            lat = doc.get(LAT_FIELD)
            lng = doc.get(LNG_FIELD)

            if lat is None or lng is None:
                continue

            result.append(HeatmapPoint(
                lat=float(lat),
                lng=float(lng),
                count=1
            ))
        
        return result
