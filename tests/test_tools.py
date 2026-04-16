from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_tool_registration(mcp_server):
    """Verify that all portmanteau tools are registered with FastMCP."""
    # We need to mock initialize dependencies to avoid looking for GIMP
    with patch("gimp_mcp.main.GimpDetector.detect_gimp_installation", return_value="/mock/gimp"):
        await mcp_server.initialize()

    expected_tools = [
        "gimp_file",
        "gimp_transform",
        "gimp_color",
        "gimp_filter",
        "gimp_layer",
        "gimp_analysis",
        "gimp_batch",
        "gimp_system",
        "gimp_live_status",
    ]

    # FastMCP version-agnostic tool discovery using async list_tools()
    tools_list = await mcp_server.mcp.list_tools()
    registered_tools = [t.name for t in tools_list]
    for tool in expected_tools:
        assert tool in registered_tools


@pytest.mark.asyncio
async def test_gimp_live_status_tool(mock_bridge, mcp_server):
    """Verify gimp_live_status tool returns correct mode."""
    mcp_server.config.bridge_port = mock_bridge.port

    with patch("gimp_mcp.main.GimpDetector.detect_gimp_installation", return_value="/mock/gimp"):
        await mcp_server.initialize()

    # Let's find it in list_tools
    tools_list = await mcp_server.mcp.list_tools()
    tool_obj = next(t for t in tools_list if t.name == "gimp_live_status")
    # We MUST await the tool function since it's async
    result = await tool_obj.fn()

    assert result["success"] is True
    assert result["mode"] == "live"


@pytest.mark.asyncio
async def test_tool_execution_live_fallback(mock_bridge, mcp_server):
    """Verify tool execution falls back to headless if bridge fails."""
    mcp_server.config.bridge_port = mock_bridge.port

    with patch("gimp_mcp.main.GimpDetector.detect_gimp_installation", return_value="/mock/gimp"):
        await mcp_server.initialize()

    # Mock the bridge call to fail
    with patch.object(
        mcp_server.interaction_manager.bridge, "execute_live_python", side_effect=Exception("Bridge failed")
    ):
        # Mock CLI success
        with patch.object(
            mcp_server.interaction_manager.cli, "execute_python_fu", return_value="CLI_SUCCESS|Headless success"
        ):
            # Find a tool that uses interaction_manager, e.g. gimp_system
            tools_list = await mcp_server.mcp.list_tools()
            tool_obj = next(t for t in tools_list if t.name == "gimp_system")
            result = await tool_obj.fn(operation="status")

            assert result["success"] is True
            assert "Headless success" in result["message"]
