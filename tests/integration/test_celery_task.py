from fastapi.testclient import TestClient
from celery.contrib.pytest import celery_app
import pytest
import celery
from app.celery_worker.tasks.wms_thumbnail_generate import create_wms_thumbnail_task


@pytest.fixture
def mocked_reate_wms_thumbnail_task(mocker):
    # Mock the Celery task
    return mocker.patch(
        "app.celery_worker.tasks.wms_thumbnail_generate.create_wms_thumbnail_task.delay",
        return_value="olleh")


# This test will run the celery task synchronously (not as a real background job)
def test_create_wms_thumbnail_task_minimal(mocked_reate_wms_thumbnail_task):
    wmsconfig = {
        "id": "testid",
        "wms_url": "http://example.com/wms",
        "path": "testid.png",
        "wms_layer": "layer1",
        "projection": "PlateCarree",
    }
    # Call the Celery task
    result = mocked_reate_wms_thumbnail_task.delay("hello")
