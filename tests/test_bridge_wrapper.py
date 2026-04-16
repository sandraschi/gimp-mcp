import pytest

from gimp_mcp.bridge_wrapper import GimpBridgeWrapper
from gimp_mcp.config import GimpConfig


@pytest.mark.asyncio
async def test_bridge_is_alive_success(mock_bridge):
    """Verify that is_alive returns True when bridge is reachable."""
    config = GimpConfig(bridge_port=mock_bridge.port, enable_live_mode=True)
    wrapper = GimpBridgeWrapper(config)
    assert await wrapper.is_alive() is True


@pytest.mark.asyncio
async def test_bridge_is_alive_failure():
    """Verify that is_alive returns False when bridge is unreachable."""
    config = GimpConfig(bridge_port=65530, enable_live_mode=True)
    wrapper = GimpBridgeWrapper(config)
    assert await wrapper.is_alive() is False


@pytest.mark.asyncio
async def test_bridge_disabled_mode():
    """Verify that is_alive returns False when live mode is disabled in config."""
    config = GimpConfig(enable_live_mode=False)
    wrapper = GimpBridgeWrapper(config)
    assert await wrapper.is_alive() is False


@pytest.mark.asyncio
async def test_execute_live_python_success(mock_bridge):
    """Verify successful command execution via bridge."""
    config = GimpConfig(bridge_port=mock_bridge.port, enable_live_mode=True)
    wrapper = GimpBridgeWrapper(config)
    mock_bridge.response_data = {"result": "image_resized"}

    code = "gimp.context_set_interpolation(0)"
    result = await wrapper.execute_live_python(code)

    assert result == {"result": "image_resized"}
    assert mock_bridge.last_request == {"code": code}


@pytest.mark.asyncio
async def test_execute_live_python_error_response(mock_bridge):
    """Verify handling of error responses from the bridge."""
    config = GimpConfig(bridge_port=mock_bridge.port, enable_live_mode=True)
    wrapper = GimpBridgeWrapper(config)
    mock_bridge.response_data = {"error": "Execution failed", "traceback": "..."}

    result = await wrapper.execute_live_python("invalid_code()")
    assert "error" in result
    assert result["error"] == "Execution failed"


@pytest.mark.asyncio
async def test_execute_live_python_connection_failure():
    """Verify handling of connection failures during execution."""
    config = GimpConfig(bridge_port=65530, enable_live_mode=True)
    wrapper = GimpBridgeWrapper(config)

    result = await wrapper.execute_live_python("print(1)")
    assert "error" in result
    # Error message comes from exception string or timeout
