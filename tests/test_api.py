from fastapi.testclient import TestClient


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


def test_api_health_live_mode(mock_bridge, mcp_server):
    """Verify that API correctly reports 'live' mode when bridge is running."""
    # We need to manually initialize the server components with the mock port
    # because GimpMCPServer() in conftest might have defaulted to auto-detection.
    mcp_server.config.bridge_port = mock_bridge.port
    mcp_server.config.enable_live_mode = True

    # Re-initialize interaction manager to pick up mock port
    from gimp_mcp.cli_wrapper import GimpCliWrapper
    from gimp_mcp.interaction_manager import GimpInteractionManager

    # Mock CLI wrapper to avoid actual GIMP check
    mock_cli = GimpCliWrapper.__new__(GimpCliWrapper)
    mock_cli.config = mcp_server.config
    mcp_server.interaction_manager = GimpInteractionManager(mcp_server.config, mock_cli)

    client = TestClient(mcp_server.mcp.app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()

    assert data["live_mode"]["mode"] == "live"
    assert data["live_mode"]["live_available"] is True


def test_api_health_offline_mode(mcp_server):
    """Verify that API reports 'offline' when no interaction manager is set."""
    mcp_server.interaction_manager = None
    client = TestClient(mcp_server.mcp.app)

    response = client.get("/api/health")
    data = response.json()
    assert data["live_mode"]["mode"] == "offline"
