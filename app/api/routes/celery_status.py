
from fastapi import APIRouter
from celery.result import AsyncResult
from ...celery_worker.app import app as celery_app
from ...core.logging import logger

# Update logger name for this file
logger.name = __name__

# Initialise the router
router = APIRouter(tags=['celery'])


@router.get("/tasks/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.ready():
        result = task_result.get()
        status = task_result.status
        response_dict = {"status": status,
                         "result": result}
        if status == 'FAILURE':
            response_dict.update({"traceback": task_result.traceback})

        return response_dict

    else:
        return {"status": "PENDING"}
