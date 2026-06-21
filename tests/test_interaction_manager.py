import pytest


@pytest.mark.asyncio
async def test_get_status_live(mock_bridge, interaction_manager):
    """Verify status reports 'live' when mock bridge is running."""
    status = await interaction_manager.get_status()
    assert status["mode"] == "live"
    assert status["live_available"] is True
    assert status["bridge_port"] == mock_bridge.port


@pytest.mark.asyncio
async def test_get_status_headless(interaction_manager):
    """Verify status reports 'headless' when no bridge is reachable."""
    # Note: we don't use the mock_bridge fixture here so no server is listening on 5001
    status = await interaction_manager.get_status()
    assert status["mode"] == "headless"
    assert status["live_available"] is False


@pytest.mark.asyncio
async def test_execute_python_fu_live_success(mock_bridge, interaction_manager):
    """Verify primary execution path via Live Bridge."""
    mock_bridge.response_data = {"result": "processed_image_v3"}

    code = "pdb.gimp_image_new(100, 100, 0)"
    result = await interaction_manager.execute_python_fu(code)

    assert result == "LIVE_SUCCESS|processed_image_v3"
    assert interaction_manager.last_mode == "live"


@pytest.mark.asyncio
async def test_execute_python_fu_fallback(interaction_manager, mock_cli_wrapper):
    """Verify fallback to Headless CLI when bridge is offline."""
    async def _fallback(code, timeout=None):
        return "CLI_SUCCESS|fallback_done"

    mock_cli_wrapper.execute_python_fu.side_effect = _fallback

    code = "pdb.gimp_quit(0)"
    result = await interaction_manager.execute_python_fu(code)

    assert result == "CLI_SUCCESS|fallback_done"
    assert interaction_manager.last_mode == "headless"
    mock_cli_wrapper.execute_python_fu.assert_called_once_with(code, None)


@pytest.mark.asyncio
async def test_execute_script_fu_always_headless(interaction_manager, mock_cli_wrapper):
    """Verify Script-Fu always routes to CLI (current implementation restriction)."""
    code = "(gimp-quit 0)"
    result = await interaction_manager.execute_script_fu(code)

    assert "CLI_SUCCESS" in result
    assert interaction_manager.last_mode == "headless"
    mock_cli_wrapper.execute_script_fu.assert_called_once_with(code, None)
