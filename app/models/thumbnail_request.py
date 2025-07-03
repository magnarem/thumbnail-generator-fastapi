from datetime import datetime
from enum import Enum
from pydantic import BaseModel, HttpUrl, model_validator


class Projections(str, Enum):
    Mercator = "Mercator"
    PlateCarree = "PlateCarree"
    PolarStereographic = "PolarStereographic"


class WMSThumbRequest(BaseModel):
    id: str
    wms_url: HttpUrl
    wms_layer: str | None
    wms_style: str | None
    wms_zoom_level: int = 0
    wms_timeout: int = 120
    add_coastlines: bool = True
    projection: Projections = Projections.PlateCarree
    thumbnail_extent: list[float] | None
    wms_layers_mmd: list[str] = None
    start_date: datetime | None

    @model_validator(mode='before')
    @classmethod
    def validate_projection(cls, values):
        if not isinstance(values['projection'], Projections):
            raise ValueError(
                "Invalid projection. Must be one of PlateCarree, Mercator or PolarStereographic."
            )
        return values
