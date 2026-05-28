"""Tests for Agent Lab Phase 2 validation and tool registration."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    path = tmp_path / "sample.png"
    Image.new("RGBA", (512, 512), (128, 64, 32, 255)).save(path)
    return path


@pytest.fixture
def bad_size_png(tmp_path: Path) -> Path:
    path = tmp_path / "bad.png"
    Image.new("RGB", (500, 500), (255, 0, 0)).save(path)
    return path


class TestGimpValidation:
    @pytest.mark.asyncio
    async def test_validate_image_passes(self, sample_png: Path):
        from gimp_mcp.tools.validation import gimp_validation

        result = await gimp_validation("validate_image", str(sample_png))
        assert result["success"] is True
        assert result["data"]["passed"] is True
        assert result["issues"] == []

    @pytest.mark.asyncio
    async def test_audit_texture_power_of_two(self, bad_size_png: Path):
        from gimp_mcp.tools.validation import gimp_validation

        result = await gimp_validation(
            "audit_texture",
            str(bad_size_png),
            target_platform="unity",
        )
        assert result["success"] is True
        assert result["data"]["passed"] is False
        assert any("power-of-two" in issue for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_check_alpha_missing(self, bad_size_png: Path):
        from gimp_mcp.tools.validation import gimp_validation

        result = await gimp_validation(
            "check_alpha",
            str(bad_size_png),
            require_alpha=True,
        )
        assert result["success"] is True
        assert result["data"]["passed"] is False


class TestPhase2ToolRegistration:
    @pytest.mark.asyncio
    async def test_validation_tool_on_http_server(self):
        from gimp_mcp.http_app import _mcp

        tools = await _mcp.list_tools()
        names = {t.name for t in tools}
        assert "gimp_validation_tool" in names
        assert "gimp_bridge_tool" in names
        assert "gimp_render_tool" in names
