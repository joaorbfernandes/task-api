# tests/system/test_health.py

def test_health_endpoint_returns_ok(client):
    """
    Test that the health endpoint is reachable and returns the expected response.

    This is usually the simplest test in an API. It confirms that:
    - the FastAPI application is running
    - the router is correctly registered
    - the TestClient can perform requests
    """

    response = client.get("/health")

    # the endpoint must respond with HTTP 200
    assert response.status_code == 200

    # the body should match the expected payload
    assert response.json() == {"status": "ok"}