#
#   Imports
#

from fastapi import APIRouter

# Perso

from api.routes.accidents_routes import router as accidents_router
from api.routes.import_routes import router as import_router
from api.routes.most_accidented_itinerary_routes import router as mai_router
from api.routes.unique_itinerary_routes import router as unique_itinerary_router
from config.config import get_settings
from api.routes.top_itinerary_routes import router as top_itinerary_router

#
#   Routes
#

settings = get_settings()

router = APIRouter(prefix=settings.APP_PREFIX)

router.include_router(accidents_router)
router.include_router(import_router)
router.include_router(mai_router)
router.include_router(unique_itinerary_router)
router.include_router(top_itinerary_router)
