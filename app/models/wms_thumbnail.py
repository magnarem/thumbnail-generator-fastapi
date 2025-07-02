from datetime import datetime
from enum import Enum
from pydantic import BaseModel, HttpUrl


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
    projection: Projections | Projections.PlateCarree
    thumbnail_extent: list[float] | None
    wms_layers_mmd: list[str] = None
    start_date: datetime | None


class WMSThumbnail:
    def __init__(self):
        self.wms_layer = None
        self.wms_style = None
        self.wms_zoom_level = None
        self.wms_timeout = None
        self.add_coastlines = None
        self.thumbnail_extent = None
