#
#   Imports
#

from typing import Any
from pymongo import MongoClient, ASCENDING

# Perso

from backend.config.config import get_settings

#
#   Config
#

settings = get_settings()

#
#   Main
#

client = MongoClient[Any](settings.DB_STRING)

db = client["nycbikes"]

coll_bi = db["bikes_itinerary"]
coll_acc = db["accidents"]

# Creating the indexes

coll_bi.drop_indexes()

coll_bi.create_index({
    "started_at": ASCENDING,
    "ended_at": ASCENDING,
    "start_lat": ASCENDING,
    "start_lng": ASCENDING,
    "end_lat": ASCENDING,
    "end_lng": ASCENDING,
}, unique=True)

coll_bi.create_index({
    "started_at": ASCENDING,
})

coll_acc.drop_indexes()

coll_acc.create_index({
    "DATETIME": ASCENDING,
    "LONGITUDE": ASCENDING,
    "LATITUDE": ASCENDING,
}, unique=True)

coll_acc.create_index({
    "DATETIME": ASCENDING,
})
