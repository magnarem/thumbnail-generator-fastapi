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


def test_get_status(client):
    response = client.get("/celery/task/status/123")
    assert response.status_code == 200


def test_get_status_not_found(client: TestClient, mocker):
    with patch("app.api.routes.celery_status.AsyncResult") as mock_async_result:
        mock_instance = MagicMock()
        mock_instance.state = "PENDING"
        mock_instance.result = None
        mock_async_result.return_value = mock_instance

        response = client.get("/api/tasks/doesnotexist")
        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"
