#
#   Imports
#

from typing import List
from typing import Any
from pymongo import AsyncMongoClient

# Perso

from config.config import get_settings
from models.itinerary import Itinerary

#
#   MostAccidentedItineraryService
#

settings = get_settings()

class MostAccidentedItineraryService:
    """
        Service to get the most accidented itinerary.
    """

    def __init__(self, db: AsyncMongoClient[Any]):
        self._db = db[settings.DB_NAME]

    async def get_top_n_accidented_itinerary(
        self,
        n: int = 5,
    ) -> List[Itinerary]:
        """
            Returns the most accidented itineraries.

            Params:
                - n: Number of itineraries to return.

            Returns:
                - List of Itinerary.
        """
        
        query: List[dict[str, Any]] = [
            {
                "$group": {
                    "_id": {
                        "start_station_name": "$start_station_name",
                        "end_station_name": "$end_station_name"
                    },
                    "firstAcc": {
                        "$first": "$accident_month_ids"
                    },
                    "start_station_lat": { "$first": "$start_lat" },
                    "start_station_lng": { "$first": "$start_lng" },
                    "end_station_lat": { "$first": "$end_lat" },
                    "end_station_lng": { "$first": "$end_lng" },
                },
            },
            {
                "$addFields": {
                    "nb_acc": {
                        "$size": {
                            "$ifNull": ["$firstAcc", []]
                        }
                    }
                },
            },
            {
                "$sort": {
                    "nb_acc": -1
                }
            },
            {"$limit": n},
            {
                "$project": {
                    "_id": 0,
                    "start_station_name": "$_id.start_station_name",
                    "end_station_name": "$_id.end_station_name",
                    "positions": [
                        [ "$start_station_lat", "$start_station_lng" ],
                        [ "$end_station_lat", "$end_station_lng" ]
                    ],
                    "nb_acc": 1
                }
            }
        ]

        result = await self._db["bikes_itinerary"].aggregate(query)

        return await result.to_list(length=n)