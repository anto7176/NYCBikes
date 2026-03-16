#
#   Imports
#

from typing import Any

from pymongo import AsyncMongoClient

# Perso

from config.config import get_settings

#
#   Session
#

settings = get_settings()

def get_db() -> AsyncMongoClient[Any]:
    """Return a MongoDB client."""

    return AsyncMongoClient[Any](
        settings.DB_STRING,
        uuidRepresentation="standard",
    )