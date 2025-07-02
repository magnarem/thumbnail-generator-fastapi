from fastapi import APIRouter

from .celery_status import router as celery_status_router
from .root import router as root_router
from .wms_thumbnail import router as wms_thumbnail_router

router = APIRouter(prefix="/v1")
router.include_router(root_router)
router.include_router(celery_status_router)
router.include_router(wms_thumbnail_router)
