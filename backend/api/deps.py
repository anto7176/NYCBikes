#
#   Imports
#

from typing import Any
from fastapi import Depends
from pymongo import AsyncMongoClient

# Perso

from db.session import get_db
from services.accidents_services import AccidentsService
from services.import_service import ImportService
from services.matching_service import MatchingService
from services.unique_itinerary_service import UniqueItineraryService


#
#   Dependencies
#

async def get_db_client(
    db: AsyncMongoClient[Any] = Depends(get_db)
) -> AsyncMongoClient[Any]:
    """Return a MongoDB client."""

    return db

async def get_import_service(
    db: AsyncMongoClient[Any] = Depends(get_db_client)
) -> ImportService:
    """Return an ImportService instance."""

    return ImportService(db)

async def get_accidents_service(
    db: AsyncMongoClient[Any] = Depends(get_db_client)
) -> AccidentsService:
    """Return an AccidentsService instance."""

    return AccidentsService(db)

async def get_matching_service(
    db: AsyncMongoClient[Any] = Depends(get_db_client)
) -> MatchingService:
    """Return a MatchingService instance."""

    return MatchingService(db)

async def get_unique_itineraries_service(
    db: AsyncMongoClient[Any] = Depends(get_db_client)
) -> UniqueItineraryService:
    """Return an UniqueItineraryService instance."""

    return UniqueItineraryService(db)


