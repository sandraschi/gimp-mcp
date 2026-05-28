"""Tests for automated sim-art import handoff."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def gazebo_model_dir(tmp_path: Path) -> Path:
    model = tmp_path / "TurtleBot"
    model.mkdir()
    (model / "model.config").write_text("<model><name>TurtleBot</name></model>", encoding="utf-8")
    (model / "model.sdf").write_text("<sdf version='1.8'></sdf>", encoding="utf-8")
    return model


@pytest.fixture
def icon_file(tmp_path: Path) -> Path:
    path = tmp_path / "icon.png"
    Image.new("RGBA", (256, 256), (10, 20, 30, 255)).save(path)
    return path


class TestFleetSimHandoff:
    @pytest.mark.asyncio
    async def test_import_gazebo_model(self, gazebo_model_dir: Path, icon_file: Path):
        from gimp_mcp.utils.fleet_sim_handoff import import_icon_to_gazebo_model

        result = await import_icon_to_gazebo_model(
            icon_path=str(icon_file),
            model_dir=str(gazebo_model_dir),
        )
        assert result["success"] is True
        primary = Path(result["primary_thumbnail"])
        assert primary.is_file()
        assert primary.parent.name == "thumbnails"

    @pytest.mark.asyncio
    async def test_import_avatar_model_by_vrm(self, tmp_path: Path, icon_file: Path):
        from gimp_mcp.utils.fleet_sim_handoff import import_icon_to_avatar_model

        vrm = tmp_path / "MyAvatar.vrm"
        vrm.write_bytes(b"vrm")
        result = await import_icon_to_avatar_model(
            icon_path=str(icon_file),
            vrm_path=str(vrm),
        )
        assert result["success"] is True
        thumb = Path(result["thumbnail_path"])
        assert thumb.name == "MyAvatar.thumb.png"
        assert thumb.is_file()

    @pytest.mark.asyncio
    async def test_batch_import_gazebo(self, tmp_path: Path, gazebo_model_dir: Path, icon_file: Path):
        from gimp_mcp.utils.fleet_sim_handoff import batch_import_gazebo_icons

        icons = tmp_path / "icons"
        icons.mkdir()
        named = icons / "TurtleBot_gazebo_icon_256.png"
        named.write_bytes(icon_file.read_bytes())

        result = await batch_import_gazebo_icons(
            icons_dir=str(icons),
            models_root=str(tmp_path),
            notify_robotics=False,
        )
        assert result["success"] is True
        assert result["imported"] == 1

    @pytest.mark.asyncio
    async def test_sim_art_import_operations(self, gazebo_model_dir: Path, icon_file: Path):
        from gimp_mcp.tools.sim_art_tools import gimp_sim_art

        result = await gimp_sim_art(
            "import_gazebo_model",
            icon_path=str(icon_file),
            model_dir=str(gazebo_model_dir),
        )
        assert result["success"] is True
