import logging

from celery import Celery
from kombu import Exchange, Queue

from ..core.config import settings

logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M",
    handlers=[
        logging.FileHandler("celery_worker.log"),
        logging.StreamHandler(),
    ],
)

app = Celery(
    __name__,
    broker=settings.BROKER_URL,
    backend=settings.RESULT_BACKEND,
    broker_connection_retry_on_startup=True,
)
# app.conf.set('LOCAL_IMAGE_PATH', settings.IMAGE_PATH)
app.add_defaults(
    {
        "LOCAL_IMAGE_PATH": settings.IMAGE_PATH,
        "THUMB_HOST_BASE_PATH": settings.THUMB_HOST_BASE_PATH,
    }
)


app.conf.task_queues = (
    Queue(
        name=settings.WMS_THUMBNAIL_QUEUE,
        exchange=Exchange(settings.WMS_THUMBNAIL_QUEUE),
        routing_key=settings.WMS_THUMBNAIL_QUEUE,
    ),
    Queue(
        name="celery",
        exchange=Exchange("celery"),
        routing_key="celery",
    ),
)

from . import tasks  # noqa
