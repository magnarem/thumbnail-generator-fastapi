print("Reading celeryconfig")
WMS_THUMBNAIL_QUEUE = "wms_thumbnail_queue"
WORKDIR = "workdir"

# Specify the path where the celery tasks will store the thumbnails
LOCAL_IMAGE_PATH = WORKDIR + "/thumbs/"

broker_url = "redis://localhost:6379/0"
imports = [
    "flask_celery_redis.celery.tasks.download_pokemon_sprite",
    "flask_celery_redis.celery.tasks.wms_thumbnail_generate",
]
result_backend = "db+sqlite:///results.db"
task_default_queue = WMS_THUMBNAIL_QUEUE
