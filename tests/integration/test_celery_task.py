from fastapi.testclient import TestClient
from celery.contrib.pytest import celery_app
import pytest
import celery
from app.celery_worker.tasks.wms_thumbnail_generate import create_wms_thumbnail_task


@pytest.fixture
def mocked_create_wms_thumbnail_task(mocker):
    # Mock the Celery task
    return mocker.patch(
        "app.celery_worker.tasks.wms_thumbnail_generate.create_wms_thumbnail_task.delay",
        return_value='{"message": "WMS Thumbnail generated successfully"}')


# This test will run the celery task synchronously (not as a real background job)
def test_create_wms_thumbnail_task_minimal(mocked_create_wms_thumbnail_task):
    wmsconfig = {
        "id": "testid",
        "wms_url": "http://example.com/wms",
        "path": "testid.png",
        "wms_layer": "layer1",
        "projection": "PlateCarree",
    }
    # Call the Celery task
    result = mocked_create_wms_thumbnail_task.delay(wmsconfig)
    # Check if the Celery task was called once with the correct arguments
    mocked_create_wms_thumbnail_task.assert_called_once_with(wmsconfig)
    assert result.get() == '{"message": "WMS Thumbnail generated successfully"}'
