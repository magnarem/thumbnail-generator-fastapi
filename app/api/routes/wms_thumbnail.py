from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from ...celery_worker.tasks.wms_thumbnail_generate import create_wms_thumbnail_task
from ...core.config import settings
from ...core.logging import logger
from ...models.thumbnail_response import ThumbnailResponse, ThumbnailResponseData
from ...models.wms_thumbnail import WMSThumbRequest

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
    wms_url = str(request.wms_url)
    identifier = request.id
    req_dict = dict(request)
    logger.debug(req_dict)
    logger.debug(wms_url)

    # Remove query parameters from url
    if "?" in wms_url:
        wms_url = wms_url.split("?", maxsplit=1)[0]

    # Parse wms_url and generate url path for thumbnail
    parsed_url = urlparse(wms_url)
    path = f"{parsed_url.netloc}{parsed_url.path}/{identifier}.png"
    path = path.replace("//", "/")
    full_path = f"{thumb_host}{image_path}{path}"

    # Test the wms-url endpoint that it is answering
    # async with httpx.AsyncClient(http2=True, timeout=request.wms_timeout) as client:
    #     try:
    #         response = await client.get(wms_url)
    #         response.raise_for_status()
    #         if response.status_code != 200:
    #             msg = str(response.text)
    #             resp = ThumbnailResponse(data=ThumbnailResponseData(),
    #                                      error=f"Could not create wms thumbnail task: {msg}",
    #                                      status_code=response.status_code)
    #             logger.error("Got status code: %d from wms_url.", response.status_code)
    #             return jsonable_encoder(resp)

    #     except httpx.ReadTimeout as exc:
    #         resp = ThumbnailResponse(data=ThumbnailResponseData(),
    #                                  error=f"HTTP TimeoutError creating thumbnail task: {str(exc)}",
    #                                  status_code=504)
    #         logger.error("Timeout error creating thumbnail task.")
    #         return jsonable_encoder(resp)

    #     except httpx.HTTPStatusError as exc:
    #         resp = ThumbnailResponse(data=ThumbnailResponseData(),
    #                                  error=f"HTTPStatusError creating thumbnail task: {str(exc)}",
    #                                  status_code=exc.response.status_code)
    #         logger.error("Got status code: %d from wms_url.", exc.response.status_code)
    #         return jsonable_encoder(resp)

    #     except Exception as exc:
    #         resp = ThumbnailResponse(data=ThumbnailResponseData(),
    #                                  error=f"Exception creating thumbnail task: {str(exc)}",
    #                                  status_code=response.status_code)
    #         logger.error("Got status code: %d from wms_url.", response.status_code)
    #         return jsonable_encoder(resp)

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
