"""Tests for Agent Lab Phase 5 robotics and sim-art tools."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image


@pytest.fixture
def icon_sources(tmp_path: Path) -> Path:
    folder = tmp_path / "sources"
    folder.mkdir()
    for idx, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)], start=1):
        path = folder / f"icon_{idx}.png"
        Image.new("RGBA", (640, 480), (*color, 255)).save(path)
    return folder


class TestSimArtTemplates:
    @pytest.mark.asyncio
    async def test_list_templates(self):
        from gimp_mcp.tools.sim_art_tools import gimp_sim_art

        result = await gimp_sim_art("list_templates")
        assert result["success"] is True
        assert result["data"]["templates"]
        assert result["data"]["atlas_layouts"]


class TestGazeboIcons:
    @pytest.mark.asyncio
    async def test_gazebo_model_icons(self, icon_sources: Path, tmp_path: Path):
        from gimp_mcp.tools.sim_art_tools import gimp_sim_art

        out = tmp_path / "gazebo"
        result = await gimp_sim_art(
            "gazebo_model_icons",
            input_dir=str(icon_sources),
            output_dir=str(out),
            template_id="gazebo_icon_256",
            validate=False,
        )
        assert result["success"] is True
        assert result["data"]["count"] == 3
        for path in result["files"]:
            with Image.open(path) as img:
                assert img.size == (256, 256)


class TestAtlas:
    @pytest.mark.asyncio
    async def test_build_atlas(self, icon_sources: Path, tmp_path: Path):
        from gimp_mcp.tools.sim_art_tools import gimp_sim_art

        atlas_path = tmp_path / "atlas.png"
        result = await gimp_sim_art(
            "build_atlas",
            input_dir=str(icon_sources),
            output_path=str(atlas_path),
            layout="2x2",
            cell_size=128,
        )
        assert result["success"] is True
        assert atlas_path.is_file()
        manifest = atlas_path.with_suffix(".manifest.json")
        assert manifest.is_file()
        with Image.open(atlas_path) as img:
            assert img.size == (256, 256)


class TestVrchatBatch:
    @pytest.mark.asyncio
    async def test_vrchat_icon_batch(self, icon_sources: Path, tmp_path: Path):
        from gimp_mcp.tools.sim_art_tools import gimp_sim_art

        out = tmp_path / "vrchat"
        result = await gimp_sim_art(
            "vrchat_icon_batch",
            input_dir=str(icon_sources),
            output_dir=str(out),
            template_id="vrchat_profile_256",
            validate=False,
        )
        assert result["success"] is True
        assert len(result["files"]) == 3


class TestSimPipeline:
    @pytest.mark.asyncio
    async def test_gazebo_pipeline(self, icon_sources: Path, tmp_path: Path):
        from gimp_mcp.utils.fleet_sim_pipeline import run_sim_art_pipeline

        with patch(
            "gimp_mcp.utils.fleet_sim_pipeline.gimp_sim_art",
            new=AsyncMock(
                side_effect=[
                    {
                        "success": True,
                        "data": {"count": 3, "files": []},
                        "files": [],
                    },
                    {
                        "success": True,
                        "data": {"cell_count": 3},
                        "files": ["atlas.png"],
                    },
                    {
                        "success": True,
                        "data": {"count": 3},
                        "files": [],
                    },
                ]
            ),
        ):
            report = await run_sim_art_pipeline(
                input_dir=str(icon_sources),
                staging_dir=tmp_path / "stage",
                skip_robotics=False,
            )
        assert report.success is True
        assert len(report.steps) == 3
