#
#   Imports
#

import asyncio
import time

from collections import defaultdict
from datetime import datetime
from typing import Any
from pymongo import AsyncMongoClient
from pymongo.operations import UpdateOne

# Perso

from config.config import get_settings

#
#   Constants
#

ACC_BATCH_SIZE = 1000
UPDATING_BATCH_SIZE = 10000

#
#   Matching Service
#

settings = get_settings()

class MatchingService:
    """
        Service to match the accidents with the bikes itinerary.
    """

    def __init__(self, db: AsyncMongoClient[Any]):
        self._db = db[settings.DB_NAME]

    async def match_acc_bi_by_month(
        self, start_date: datetime, end_date: datetime
    ) -> None:
        """
            Matches accidents with bikes itinerary for the given monthly period.
            Processes accidents in batches and updates bikes_itinerary with
            accident_month_ids.

            Params:
                - start_date: Start of the period (inclusive).
                - end_date: End of the period (exclusive).
        """

        # Fetching accidents in the period
        accs = self._db["accidents"].find(
            {
                "started_at": {"$gte": start_date, "$lt": end_date}
            },
            projection={"_id": 1, "position": 1},
        )

        # Processing accidents by batch
        batch_acc: list[dict[str, Any]] = []
        tasks: list[asyncio.Task[None]] = []
        i = 0
        async for acc in accs:
            batch_acc.append(acc)
            if len(batch_acc) >= ACC_BATCH_SIZE:
                i += 1

                tasks.append(asyncio.create_task(
                    self._process_acc_batch(batch_acc, start_date, end_date, i)
                ))

                batch_acc = []

        # Processing the remaining batch
        if batch_acc:
            tasks.append(asyncio.create_task(
                self._process_acc_batch(batch_acc, start_date, end_date, i + 1)
            ))

        await asyncio.gather(*tasks)

    async def _process_acc_batch(
        self,
        acc_batch: list[dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
        n: int,
    ) -> None:
        """
            For a batch of accidents, finds intersecting bikes itinerary and
            updates each itinerary with the linked accident ids.

            Params:
                - acc_batch: List of accidents (_id, position).
                - start_date: Start of the period (inclusive).
                - end_date: End of the period (exclusive).
                - n: The number of the batch.
        """
        
        time_start = time.time()
        print(f"Processing batch {n}")

        # Building links: bi_id -> set of acc_ids
        links: dict[Any, set[Any]] = defaultdict(set)

        for acc in acc_batch:
            acc_id = acc["_id"]
            pt = acc["position"]

            # Finding bikes itinerary whose buffer intersects the accident
            bis = self._db["bikes_itinerary"].find(
                {
                    "started_at": {"$gte": start_date, "$lt": end_date},
                    "buffer": {
                        "$geoIntersects": {
                            "$geometry": pt
                        }
                    },
                },
                projection={"_id": 1},
            )

            async for bi in bis:
                links[bi["_id"]].add(acc_id)

        # Building bulk updates from links
        updates: list[UpdateOne] = []
        for bi_id, acc_ids in links.items():
            updates.append(
                UpdateOne(
                    {"_id": bi_id},
                    {"$addToSet": {"accident_month_ids": {"$each": list(acc_ids)}}},
                )
            )

            # Flushing updates when batch size is reached
            if len(updates) >= UPDATING_BATCH_SIZE:
                await self._db["bikes_itinerary"].bulk_write(updates, ordered=False)
                updates = []

        # Writing remaining updates
        if updates:
            await self._db["bikes_itinerary"].bulk_write(updates, ordered=False)

        print(f"Batch {n} processed in {time.time() - time_start} seconds")
