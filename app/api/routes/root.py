# File: app/api/routes/root.py
from fastapi import APIRouter, status, Response

# import logging

# logger = logging.getLogger('uvicorn.error')

router = APIRouter(tags=["root"])


@router.get("/")
async def root() -> Response:
    """
    Simple endpoint for checking that the app is running.
    Returns a simple message.
    """
    return Response(content="API are up and running", status_code=status.HTTP_200_OK)
