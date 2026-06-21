"""Tests for Agent Lab Phase 3 fleet handoff."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image


@pytest.fixture
def sample_texture(tmp_path: Path) -> Path:
    path = tmp_path / "albedo.png"
    Image.new("RGBA", (512, 512), (200, 100, 50, 255)).save(path)
    return path


@pytest.fixture
def unity_project(tmp_path: Path) -> Path:
    assets = tmp_path / "Assets"
    assets.mkdir()
    return tmp_path


class TestGimpImport:
    @pytest.mark.asyncio
    async def test_import_file_staging(self, sample_texture: Path, tmp_path: Path):
        from gimp_mcp.tools.import_tools import gimp_import

        result = await gimp_import(
            "import_file",
            source_path=str(sample_texture),
            staging_dir=str(tmp_path / "stage"),
        )
        assert result["success"] is True
        assert Path(result["staging_path"]).is_file()

    @pytest.mark.asyncio
    async def test_normalize_texture(self, sample_texture: Path, tmp_path: Path):
        from gimp_mcp.tools.import_tools import normalize_texture_png

        out = tmp_path / "out.png"
        result = await normalize_texture_png(str(sample_texture), str(out), size=512)
        assert result["success"] is True
        assert out.is_file()
        with Image.open(out) as img:
            assert img.size == (512, 512)


class TestGimpVisionRefine:
    @pytest.mark.asyncio
    async def test_review_bundle(self, sample_texture: Path, tmp_path: Path):
        from gimp_mcp.tools.vision_refine_tools import gimp_vision_refine

        folder = tmp_path / "review"
        folder.mkdir()
        dest = folder / "tex.png"
        dest.write_bytes(sample_texture.read_bytes())

        result = await gimp_vision_refine("review_bundle", input_dir=str(folder))
        assert result["success"] is True
        assert result["image_count"] == 1
        assert "agent_prompt" in result


class TestFleetPipeline:
    @pytest.mark.asyncio
    async def test_pipeline_with_texture_skip_blender(
        self,
        sample_texture: Path,
        unity_project: Path,
        tmp_path: Path,
    ):
        from gimp_mcp.utils.fleet_pipeline import run_fleet_pipeline

        with patch(
            "gimp_mcp.utils.fleet_pipeline.push_texture_to_unity",
            new=AsyncMock(
                return_value={
                    "success": True,
                    "destination_path": str(unity_project / "Assets" / "GimpImports" / "albedo_pot.png"),
                }
            ),
        ):
            with patch(
                "gimp_mcp.utils.fleet_pipeline.check_http_health",
                new=AsyncMock(return_value=True),
            ):
                report = await run_fleet_pipeline(
                    project_path=str(unity_project),
                    texture_path=str(sample_texture),
                    staging_dir=tmp_path / "stage",
                    skip_blender=True,
                    skip_review=True,
                )

        assert any(s.name == "gimp_normalize" and s.success for s in report.steps)
        assert report.success is True


class TestPhase3ToolRegistration:
    @pytest.mark.asyncio
    async def test_phase3_tools_registered(self):
        from gimp_mcp.http_app import _mcp

        tools = await _mcp.list_tools()
        names = {t.name for t in tools}
        assert "gimp_import_tool" in names
        assert "gimp_vision_refine_tool" in names
