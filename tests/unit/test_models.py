import pytest
from pydantic import ValidationError
from app.models.wms_thumbnail import WMSThumbRequest, Projections
from app.models.thumbnail_response import ThumbnailResponse, ThumbnailResponseData
from datetime import datetime
from uuid import uuid4


def test_wms_thumb_request_valid():
    req = WMSThumbRequest(
        id="testid",
        wms_url="http://example.com/wms",
        wms_layer="layer1",
        wms_style="style1",
        wms_zoom_level=2,
        wms_timeout=60,
        add_coastlines=False,
        projection=Projections.Mercator,
        thumbnail_extent=[0.0, 1.0, 2.0, 3.0],
        wms_layers_mmd=["layer1", "layer2"],
        start_date=datetime.utcnow(),
    )
    assert req.id == "testid"
    assert req.wms_url.scheme == "http"
    assert req.projection == Projections.Mercator


def test_wms_thumb_request_invalid_url():
    with pytest.raises(ValidationError):
        WMSThumbRequest(
            id="testid",
            wms_url="not-a-url",
            wms_layer="layer1",
            projection=Projections.PlateCarree,
        )


def test_wms_thumb_request_missing_required_fields():
    with pytest.raises(ValidationError):
        WMSThumbRequest(
            id="testid",
            wms_url="http://example.com/wms",
            projection=Projections.PlateCarree,
        )


def test_thumbnail_response():
    data = ThumbnailResponseData(
        thumbnail_url="/some/path.png",
        message="ok",
        task_id=uuid4(),
    )
    resp = ThumbnailResponse(data=data, error=None, status_code=200)
    assert resp.data.thumbnail_url == "/some/path.png"
    assert resp.status_code == 200
