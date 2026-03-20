#
#   Imports
#

from typing import List, Optional
from datetime import date, datetime
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
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Itinerary]:
        """
            Returns the most accidented itineraries.

            Params:
                - n: Number of itineraries to return.
                - date_from: Start date.
                - date_to: End date.

            Returns:
                - List of Itinerary.
        """

        query: List[dict[str, Any]] = []

        if date_from is not None or date_to is not None:

            query.append({
                "$match": {
                    "started_at": {}
                }
            })

            # Adapts the date format to the MongoDB format
            if date_from is not None:
                date_from = datetime.combine(date_from, datetime.min.time())
                query[0]["$match"]["started_at"]["$gte"] = date_from
            if date_to is not None:
                date_to = datetime.combine(date_to, datetime.max.time())
                query[0]["$match"]["started_at"]["$lte"] = date_to
        
        query.extend([
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
        ])

        result = await self._db["bikes_itinerary"].aggregate(query)

        ret: List[Itinerary] = []
        async for doc in result:
            itinerary = Itinerary(
                positions=doc["positions"],
                start_station_name=doc["start_station_name"],
                end_station_name=doc["end_station_name"],
                nb_acc=doc["nb_acc"],
                popup_text=doc["start_station_name"] + " => " + doc["end_station_name"],
            )
            ret.append(itinerary)

        return ret