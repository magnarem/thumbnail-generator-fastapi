from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    # Send a GET request to the root endpoint
    response = client.get("/api")

    # Assert the response status code is 200
    assert response.status_code == 200

    # Assert the response content is as expected
    assert response.text == "API are up and running"
