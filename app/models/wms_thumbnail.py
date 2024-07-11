from pydantic import BaseModel, HttpUrl
from enum import Enum
from typing import List, Optional


class Projections(str, Enum):
    Mercator = "Mercator"
    PlateCarree = "PlateCarree"
    PolarStereographic = "PolarStereographic"


class WMSThumbRequest(BaseModel):
    id: str
    wms_url: HttpUrl
    wms_layer: Optional[str] = None
    wms_style: Optional[str] = None
    wms_zoom_level: Optional[int] = 0
    wms_timeout: Optional[int] = 120
    add_coastlines: Optional[bool] = True
    projection: Projections = Projections.PlateCarree
    thumbnail_extent: Optional[List[float]] = None
    wms_layers_mmd: Optional[List[str]] = []
