"""Tests for Agent Lab Phase 1 bridge wiring and vision capture."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestGimpRuntime:
    @pytest.mark.asyncio
    async def test_bridge_unavailable(self):
        from gimp_mcp.utils.gimp_runtime import bridge_available

        bridge = MagicMock()
        bridge.is_alive = AsyncMock(return_value=False)
        assert await bridge_available(bridge) is False

    @pytest.mark.asyncio
    async def test_bridge_available(self):
        from gimp_mcp.utils.gimp_runtime import bridge_available

        bridge = MagicMock()
        bridge.is_alive = AsyncMock(return_value=True)
        assert await bridge_available(bridge) is True


class TestExecutionMode:
    @pytest.mark.asyncio
    async def test_hands_in_when_bridge_alive(self, mock_bridge, interaction_manager):
        from gimp_mcp.utils.execution_mode import describe_execution_mode

        interaction_manager.config.bridge_port = mock_bridge.port
        result = await describe_execution_mode(interaction_manager=interaction_manager)
        assert result["success"] is True
        assert result["mode"] == "hands_in"
        assert result["bridge_connected"] is True

    @pytest.mark.asyncio
    async def test_hands_off_when_bridge_offline(self, interaction_manager):
        from gimp_mcp.utils.execution_mode import describe_execution_mode

        result = await describe_execution_mode(interaction_manager=interaction_manager)
        assert result["success"] is True
        assert result["mode"] == "hands_off"
        assert result["bridge_connected"] is False


class TestBridgeTools:
    @pytest.mark.asyncio
    async def test_gimp_bridge_status_live(self, mock_bridge, interaction_manager):
        from gimp_mcp.tools.bridge_tools import gimp_bridge

        interaction_manager.config.bridge_port = mock_bridge.port
        result = await gimp_bridge("status", interaction_manager=interaction_manager)
        assert result["success"] is True
        assert result["status"] == "connected"
        assert result["mode"] == "hands_in"

    @pytest.mark.asyncio
    async def test_gimp_render_requires_bridge_for_capture(self, interaction_manager):
        from gimp_mcp.tools.bridge_tools import gimp_render

        result = await gimp_render(
            "capture_active",
            output_path="D:/Temp/gimp_test_capture.png",
            interaction_manager=interaction_manager,
        )
        assert result["success"] is False
        assert "Bridge" in result["error"]


class TestPhase1ToolRegistration:
    @pytest.mark.asyncio
    async def test_new_tools_registered(self, mcp_server):
        with patch("gimp_mcp.main.GimpDetector.detect_gimp_installation", return_value="/mock/gimp"):
            await mcp_server.initialize()

        tools = await mcp_server.mcp.list_tools()
        names = {t.name for t in tools}
        assert "gimp_bridge_tool" in names
        assert "gimp_render_tool" in names
        assert "gimp_live_status" in names
