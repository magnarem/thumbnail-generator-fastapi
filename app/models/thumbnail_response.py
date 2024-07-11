from pydantic import BaseModel
from uuid import UUID


class ThumbnailResponseData(BaseModel):
    thumbnail_url: str | None = None
    message: str | None = None
    task_id: UUID | None = None


class ThumbnailResponse(BaseModel):
    data: ThumbnailResponseData
    error: str | None = None
    status_code: int
