from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from app.util.path_utils import generate_thumbnail_paths

from ...celery_worker.tasks.wms_thumbnail_generate import create_wms_thumbnail_task
from ...core.config import settings
from ...core.logging import logger
from ...models.thumbnail_response import ThumbnailResponse, ThumbnailResponseData
from ...models.thumbnail_request import WMSThumbRequest

# Set the logger name to this file
logger.name = __name__

# Initialize the router
router = APIRouter(tags=["thumbnail"])

# Get required settings
thumb_host = settings.THUMB_HOST
image_path = settings.IMAGE_PATH


@router.post("/thumbnail/wms/generate_thumbnail")
async def generate_wms_thumbnail(request: WMSThumbRequest) -> ThumbnailResponse:
    """
    Generate a thumbnail on disk and return filepath
    :param id and url
    :return: Path 200
    """
    req_dict = dict(request)
    logger.debug(req_dict)
    wms_url = str(request.wms_url)
    logger.debug(wms_url)

    # Use the new utility function for path generation
    path, full_path = generate_thumbnail_paths(request, thumb_host, image_path)

    # Update dict to send to task
    req_dict.update({"wms_url": wms_url, "path": path})
    logger.debug(req_dict)
    logger.debug("Thumbnail url: %s", full_path)
    try:
        task = create_wms_thumbnail_task.delay(req_dict)
        logger.info(f"Celery task created! Task ID: {task.id}")
        resp = ThumbnailResponse(
            data={
                "thumbnail_url": full_path,
                "message": "Celery task added to queue.",
                "task_id": task.id,
            },
            status_code=200,
        )
        return jsonable_encoder(resp)
    except Exception as e:
        logger.error(f"Could not create generate wms thumbnail task, reason: {e}")
        resp = ThumbnailResponse(
            data=ThumbnailResponseData(),
            error=f"Could not create generate wms thumbnail task: {e}",
            status_code=400,
        )
        return jsonable_encoder(resp)
