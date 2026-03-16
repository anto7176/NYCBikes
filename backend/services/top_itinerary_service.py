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

            {
                "$addFields": {
                    "round_slat": {"$round": ["$start_lat", 4]},
                    "round_slng": {"$round": ["$start_lng", 4]},
                    "round_elat": {"$round": ["$end_lat", 4]},
                    "round_elng": {"$round": ["$end_lng", 4]}
                }
            },
            
            # Groupage + Comptage
            {
                "$group": {
                    "_id": {
                        "slat": "$round_slat",
                        "slng": "$round_slng",
                        "elat": "$round_elat",
                        "elng": "$round_elng"
                    },
                    "count": {"$sum": 1},
                    "real_start_lat": {"$first": "$start_lat"},
                    "real_start_lng": {"$first": "$start_lng"},
                    "real_end_lat": {"$first": "$end_lat"},
                    "real_end_lng": {"$first": "$end_lng"}
                }
            },
            
            # 3. Tri par occurrences décroissantes
            {
                "$sort": {"count": -1}
            },
            
            # 4. On limite le nombre de résultats (ex: Top 10)
            {
                "$limit": limit
            },
            
            # 5. On reformate pour matcher avec le modèle Pydantic
            {
                "$project": {
                    "_id": 0,
                    "count": 1,
                    "start_lat": "$real_start_lat",
                    "start_lng": "$real_start_lng",
                    "end_lat": "$real_end_lat",
                    "end_lng": "$real_end_lng"
                }
            }
        ]

        # Execution de l'agrégation sur la base de données
        cursor = await self._db["bikes_itinerary"].aggregate(pipeline)
        raw = await cursor.to_list(length=limit)
        
        # Retourne des objets TopItinerary
        return [TopItinerary(**item) for item in raw]