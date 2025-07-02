from app.celery_worker.tasks.wms_thumbnail_generate import create_wms_thumbnail_task
import pytest


# This test will run the celery task synchronously (not as a real background job)
def test_create_wms_thumbnail_task_minimal(monkeypatch):
    wmsconfig = {
        "id": "testid",
        "wms_url": "http://example.com/wms",
        "path": "testid.png",
        "wms_layer": "layer1",
        "projection": "PlateCarree",
    }
    # Patch out actual WMS and plotting logic if needed for speed
    monkeypatch.setattr("app.celery_worker.tasks.wms_thumbnail_generate.WebMapService",
                        lambda url, **kwargs: None)
    monkeypatch.setattr("app.celery_worker.tasks.wms_thumbnail_generate.plt", "dummy")
    try:
        create_wms_thumbnail_task.run(wmsconfig)
        # The function does not return, but should not raise
    except Exception as e:
        pytest.fail(f"Task raised an exception: {e}")
