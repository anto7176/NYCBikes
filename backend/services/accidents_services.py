"""
    Service for reading accident data from the database.
"""

#
#   Imports
#

from typing import Any
from pymongo import AsyncMongoClient

# Perso

from config.config import get_settings
from models.heatmap_point import HeatmapPoint

#
#   Constants
#

# Same field names as in import_service (accidents: LATITUDE, LONGITUDE)
LAT_FIELD = "LATITUDE"
LNG_FIELD = "LONGITUDE"

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

    async def get_heatmap_data(self) -> list[HeatmapPoint]:
        """
            Returns accident positions in heatmap format (lat, lng, count).

            Returns:
                - List of HeatmapPoint (count is always 1).
        """

        cursor = self._db["accidents"].find(
            {},
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
