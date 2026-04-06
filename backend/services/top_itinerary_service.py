#
#   Imports
#

from typing import Any
from pymongo import AsyncMongoClient

from config.config import get_settings
from models.top_itinerary import TopItinerary

settings = get_settings()


class TopItineraryService :

    def __init__(self, db: AsyncMongoClient[Any]):
        self._db = db[settings.DB_NAME]


    async def get_top_itineraries(self, limit: int = 10) -> list[TopItinerary]:
        pipeline = [
        # Groupage + Comptage
        {
            "$group": {
                "_id": {
                    "start_lat": "$start_lat",
                    "start_lng": "$start_lng",
                    "end_lat": "$end_lat",
                    "end_lng": "$end_lng"
                },
                "count": {"$sum": 1} # Incrementation de "count" à chaque ajout dans un group
            }
        },
        {
            "$sort": {"count": -1}  # Tri decroissant
        },
        {
            "$limit": limit
        },
        {
            # Reformatage
            "$project": {
                "_id": 0,
                "count": 1,
                "start_lat": "$_id.start_lat",
                "start_lng": "$_id.start_lng",
                "end_lat": "$_id.end_lat",
                "end_lng": "$_id.end_lng"
            }
        }
    ]

        # Execution de l'agrégation sur la base de données
        cursor = await self._db["bikes_itinerary"].aggregate(pipeline)
        raw = await cursor.to_list(length=limit)
        
        # Retourne des objets TopItinerary
        return [TopItinerary(**item) for item in raw]