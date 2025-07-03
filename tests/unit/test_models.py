from pydantic import ValidationError
from app.models.thumbnail_request import WMSThumbRequest, Projections
from app.models.thumbnail_response import ThumbnailResponse, ThumbnailResponseData
from datetime import datetime
import pytest
import uuid

# Some test constants used in the tests
FIXED_TASK_ID = "12345678-1234-5678-1234-567812345678"
TEST_DATE = "2019-10-24T09:00:00Z"


# Test cases for WMSThumbRequest and ThumbnailResponse models
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
        start_date=datetime.strptime(TEST_DATE, "%Y-%m-%dT%H:%M:%SZ"),
        wms_layers_mmd=["layer1", "layer2"],
    )
    assert req.id == "testid"
    assert req.wms_url.scheme == "http"
    assert req.projection == Projections.Mercator
    assert req.start_date == datetime.strptime(TEST_DATE, "%Y-%m-%dT%H:%M:%SZ")


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


def test_wms_thumb_request_invalid_iso_date():
    with pytest.raises(ValidationError):
        WMSThumbRequest(
            id="testid",
            wms_url="http://example.com/wms",
            wms_layer="layer1",
            projection=Projections.PlateCarree,
            start_date="not-a-date"
        )


# Test cases for ThumbnailResponse model
def test_thumbnail_response_data():
    data = ThumbnailResponseData(
        thumbnail_url="/some/path.png",
        message="ok",
        task_id=uuid.UUID(FIXED_TASK_ID),  # Use a fixed UUID4 string
    )
    assert data.thumbnail_url == "/some/path.png"
    assert data.message == "ok"
    assert str(data.task_id) == FIXED_TASK_ID


def test_thumbnail_response_valid():
    data = ThumbnailResponseData(
        thumbnail_url="/some/path.png",
        message="ok",
        task_id=uuid.UUID(FIXED_TASK_ID),
    )
    resp_model = ThumbnailResponse(data=data, error=None)
    assert resp_model.data.thumbnail_url == "/some/path.png"
    assert resp_model.data.message == "ok"
    assert str(data.task_id) == FIXED_TASK_ID


def test_thumbnail_response_invalid_data():
    resp_model = ThumbnailResponse(data=None, error="Invalid data")
    assert resp_model.data is None
    assert resp_model.error == "Invalid data"


# Test case for ThumbnailResponse model object where task_id is not a valid UUID
def test_thumbnail_response_data_invalid_task_id():
    with pytest.raises(ValueError):
        ThumbnailResponseData(
            thumbnail_url="/some/path.png",
            message="ok",
            task_id="12345678-1234-5678-notuuid-567812345678"  # Invalid UUID string
        )
