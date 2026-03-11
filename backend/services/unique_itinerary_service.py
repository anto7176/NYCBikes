#
#   Imports
#

from typing import Any
from pymongo import AsyncMongoClient

from config.config import get_settings
from models.unique_itinerary import UniqueItinerary

settings = get_settings()


class UniqueItineraryService :

    def __init__(self, db: AsyncMongoClient[Any]):
        self._db = db[settings.DB_NAME]


    async def get_unique_itineraries(self) -> list[UniqueItinerary]:
        
        pipeline = [
            # Regroupe les doublons, et n'en garde qu'un
            {
                "$group": {
                    "_id": {
                        "slat": "$start_lat",
                        "slng": "$start_lng",
                        "elat": "$end_lat",
                        "elng": "$end_lng"
                    }
                }
            },
            
            # Reformatage
            {
                "$project": {
                    "_id": 0,
                    "start_lat": "$_id.slat",
                    "start_lng": "$_id.slng",
                    "end_lat": "$_id.elat",
                    "end_lng": "$_id.elng"
                }
            }
        ]

        # Exectution de $group et $project sur la db
        cursor = self._db["bikes_itinerary"].aggregate(pipeline)
        # Stockage des itineraire dans une liste
        raw = await cursor.to_list(length=None)
        # parcourt raw et renvoie chaque ligne au format UniqueItinerary
        return [UniqueItinerary(**item) for item in raw]