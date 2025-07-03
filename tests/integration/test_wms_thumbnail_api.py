from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime


def test_generate_wms_thumbnail_success(client: TestClient):
    payload = {
        "id": str(uuid4()),
        "wms_url": "http://example.com/wms",
        "wms_layer": "layer1",
        "wms_style": "",
        "wms_zoom_level": 1,
        "wms_timeout": 10,
        "add_coastlines": True,
        "projection": "PlateCarree",
        "thumbnail_extent": [0, 1, 2, 3],
        "wms_layers_mmd": ["layer1"],
        "start_date": datetime.utcnow().isoformat(),
    }
    response = client.post("/thumbnail/wms/generate_thumbnail", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "thumbnail_url" in data["data"]
    assert data["data"]["message"] == "Celery task added to queue."


def test_generate_wms_thumbnail_invalid_url(client: TestClient):
    payload = {
        "id": str(uuid4()),
        "wms_url": "not-a-url",
        "wms_layer": "layer1",
        "projection": "PlateCarree",
    }
    response = client.post("/thumbnail/wms/generate_thumbnail", json=payload)
    assert response.status_code == 422
