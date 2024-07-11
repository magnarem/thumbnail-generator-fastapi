import os
import threading
from fastapi import APIRouter
from ...core.logging import logger

# import logging

# logger = logging.getLogger('uvicorn.error')

router = APIRouter(tags=['root'])


@router.get('/')
async def root() -> dict:
    """
    Simple endpoint
    """
    logger.debug(f"Current thread: {threading.current_thread().name} \
                {threading.current_thread().native_id} | PID: {os.getpid()}")
    return {'message': 'Hello, I am an fastAPI app using celery workers'}
