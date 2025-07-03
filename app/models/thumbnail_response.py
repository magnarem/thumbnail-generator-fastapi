from uuid import UUID

from pydantic import BaseModel


class ThumbnailResponseData(BaseModel):
    thumbnail_url: str | None
    message: str | None
    task_id: UUID | None


class ThumbnailResponse(BaseModel):
    data: ThumbnailResponseData | None
    error: str | None
