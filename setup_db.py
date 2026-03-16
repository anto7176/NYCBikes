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
})

coll_bi.create_index({
    "buffer": "2dsphere",
})

coll_bi.create_index({
    "_id": ASCENDING,
})

coll_acc.drop_indexes()

coll_acc.create_index({
    "started_at": ASCENDING,
    "position": "2dsphere",
}, unique=True)

coll_acc.create_index({
    "started_at": ASCENDING,
})
