import pytest


def test_api_health_basic(api_client):
    """Verify the /api/health endpoint returns 200 OK and basic fields."""
    response = api_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "server_name" in data


def test_api_status_consistency(api_client):
    """Verify that /api/status is an alias for /api/health."""
    res1 = api_client.get("/api/health")
    res2 = api_client.get("/api/status")
    assert res1.status_code == res2.status_code
    assert res1.json() == res2.json()


@pytest.mark.skip(reason="live_mode health fields are served by GimpMCPServer, not http_app")
def test_api_health_live_mode(mock_bridge, mcp_server):
    pass


@pytest.mark.skip(reason="live_mode health fields are served by GimpMCPServer, not http_app")
def test_api_health_offline_mode(mcp_server):
    pass
