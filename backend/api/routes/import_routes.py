"""
    Handles all the routes linked to the import of the
    collections to the database.
"""

#
#   Imports
#


from fastapi import APIRouter, Depends, status, File, Path
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException

# Perso

from api.deps import get_import_service
from services.import_service import ImportService
from enums.import_types import ImportType

#
#   Constants
#

FILE_SIZE = 1024 * 1024 * 1024 # 1GB

#
#   Routes
#

ALLOWED_CONTENT_TYPES = {"text/csv", "application/vnd.ms-excel"}


router = APIRouter(prefix="/import")

@router.post(
    "/{import_type}",
    status_code=status.HTTP_201_CREATED,
    description="Import a collection to the database",
)
async def import_collection(
    file: UploadFile = File(...),
    import_service: ImportService = Depends(get_import_service),
    import_type: ImportType = Path(..., description="The type of the import")
):

    # Validating the file type 
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file type, CSV expected.",
        )

    # Validating the file size
    if file.size and file.size >= FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large, 1GB max.",
        )

    await import_service.import_collection(import_type, file)

    return None

    