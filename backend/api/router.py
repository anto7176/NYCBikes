#
#   Imports
#

from fastapi import APIRouter

# Perso

from api.routes.accidents_routes import router as accidents_router
from api.routes.import_routes import router as import_router
from config.config import get_settings

#
#   Routes
#

settings = get_settings()

router = APIRouter(prefix=settings.APP_PREFIX)

router.include_router(accidents_router)
router.include_router(import_router)