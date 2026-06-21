from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_tool_registration(mcp_server):
    """Verify that all portmanteau tools are registered with FastMCP."""
    # We need to mock initialize dependencies to avoid looking for GIMP
    with patch("gimp_mcp.main.GimpDetector.detect_gimp_installation", return_value="/mock/gimp"):
        await mcp_server.initialize()

    expected_tools = [
        "gimp_file_tool",
        "gimp_transform_tool",
        "gimp_color_tool",
        "gimp_filter_tool",
        "gimp_layer_tool",
        "gimp_analysis_tool",
        "gimp_batch_tool",
        "gimp_system_tool",
        "gimp_bridge_tool",
        "gimp_render_tool",
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
    assert result["mode"] in ("live", "hands_in")


@pytest.mark.asyncio
async def test_tool_execution_live_fallback(mock_bridge, mcp_server):
    """Verify PDB tool falls back to headless when bridge fails."""
    mcp_server.config.bridge_port = mock_bridge.port

    with patch("gimp_mcp.main.GimpDetector.detect_gimp_installation", return_value="/mock/gimp"):
        await mcp_server.initialize()

    pdb_output = 'CLI_SUCCESS|PDB_RESULT:{"success": true, "result": null}'
    with patch.object(
        mcp_server.interaction_manager.bridge, "execute_live_python", side_effect=Exception("Bridge failed")
    ):
        with patch.object(
            mcp_server.interaction_manager.cli,
            "is_available",
            return_value=True,
        ):
            with patch.object(
                mcp_server.interaction_manager,
                "execute_python_fu",
                new=AsyncMock(return_value=pdb_output),
            ):
                tools_list = await mcp_server.mcp.list_tools()
                tool_obj = next(t for t in tools_list if t.name == "gimp_pdb_tool")
                result = await tool_obj.fn(procedure="gimp-quit", args=[])

                assert result["success"] is True
