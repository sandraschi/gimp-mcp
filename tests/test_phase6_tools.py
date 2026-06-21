"""Tests for Agent Lab Phase 6 PBR packs, decal sheets, and AI refine loop."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def pbr_sources(tmp_path: Path) -> Path:
    folder = tmp_path / "pbr_in"
    folder.mkdir()
    Image.new("RGB", (800, 800), (180, 90, 40)).save(folder / "mat_albedo.png")
    Image.new("RGB", (800, 800), (128, 128, 255)).save(folder / "mat_normal.png")
    Image.new("L", (800, 800), 200).save(folder / "mat_roughness.png")
    return folder


@pytest.fixture
def decal_sources(tmp_path: Path) -> Path:
    folder = tmp_path / "decals"
    folder.mkdir()
    for idx, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)], start=1):
        Image.new("RGBA", (320, 240), (*color, 255)).save(folder / f"sticker_{idx}.png")
    return folder


class TestPbrPresets:
    def test_detect_pbr_maps(self, pbr_sources: Path):
        from gimp_mcp.utils.pbr_presets import detect_pbr_maps, list_pbr_presets

        maps = detect_pbr_maps(pbr_sources)
        assert set(maps) == {"albedo", "normal", "roughness"}
        catalog = list_pbr_presets()
        assert "albedo" in catalog["required_slots"]


class TestPbrBatch:
    @pytest.mark.asyncio
    async def test_pbr_pack(self, pbr_sources: Path, tmp_path: Path):
        from gimp_mcp.tools.batch import gimp_batch

        out = tmp_path / "pbr_out"
        result = await gimp_batch(
            "pbr_pack",
            str(pbr_sources),
            str(out),
            map_size=512,
            validate_pbr=True,
            pack_prefix="mat",
        )
        assert result["success"] is True
        assert (out / "mat_albedo.png").is_file()
        assert (out / "mat_normal.png").is_file()
        assert (out / "mat_roughness.png").is_file()


class TestPbrValidation:
    @pytest.mark.asyncio
    async def test_audit_pbr_pack(self, pbr_sources: Path, tmp_path: Path):
        from gimp_mcp.tools.batch import gimp_batch
        from gimp_mcp.tools.validation import gimp_validation

        out = tmp_path / "pbr_out"
        await gimp_batch("pbr_pack", str(pbr_sources), str(out), map_size=512, validate_pbr=False)
        audit = await gimp_validation("audit_pbr_pack", str(out), target_platform="pbr")
        assert audit["success"] is True
        assert audit["data"]["passed"] is True


class TestDecalSheet:
    @pytest.mark.asyncio
    async def test_build_decal_sheet_margin_bleed(self, decal_sources: Path, tmp_path: Path):
        from gimp_mcp.tools.sim_art_tools import gimp_sim_art

        atlas_path = tmp_path / "decals.png"
        result = await gimp_sim_art(
            "build_decal_sheet",
            input_dir=str(decal_sources),
            output_path=str(atlas_path),
            layout="2x2",
            cell_size=128,
            margin_px=4,
            bleed_px=2,
        )
        assert result["success"] is True
        assert result["data"]["margin_px"] == 4
        assert result["data"]["bleed_px"] == 2
        manifest = atlas_path.with_suffix(".manifest.json")
        assert manifest.is_file()
        with Image.open(atlas_path) as img:
            assert img.size == (260, 260)


class TestAiRefineLoop:
    @pytest.mark.asyncio
    async def test_ai_refine_loop(self, pbr_sources: Path, tmp_path: Path):
        from gimp_mcp.tools.batch import gimp_batch
        from gimp_mcp.tools.vision_refine_tools import gimp_vision_refine

        out = tmp_path / "pbr_out"
        await gimp_batch("pbr_pack", str(pbr_sources), str(out), map_size=512, validate_pbr=False)
        result = await gimp_vision_refine(
            "ai_refine_loop",
            input_dir=str(out),
            goal="Fleet PBR QA",
            target_platform="pbr",
        )
        assert result["success"] is True
        assert "ai_handoff" in result
        assert result["ai_handoff"]["refine_loop"]


class TestFleetE2eOffline:
    @pytest.mark.asyncio
    async def test_offline_smoke(self, tmp_path: Path):
        from gimp_mcp.utils.fleet_e2e_offline import run_offline_smoke

        report = await run_offline_smoke(work_dir=tmp_path / "e2e")
        assert report["success"] is True
        assert report["mode"] == "offline"
        assert len(report["steps"]) >= 4
