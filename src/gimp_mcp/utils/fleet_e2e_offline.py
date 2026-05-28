"""In-process Phase 6 fleet smoke checks (no HTTP services required)."""

from __future__ import annotations

from pathlib import Path


async def run_offline_smoke(*, work_dir: Path) -> dict[str, object]:
    """Run PBR pack, decal sheet, and AI refine loop locally for CI."""
    from PIL import Image

    from ..tools.batch import gimp_batch
    from ..tools.sim_art_tools import gimp_sim_art
    from ..tools.validation import gimp_validation
    from ..tools.vision_refine_tools import gimp_vision_refine

    steps: list[dict[str, object]] = []
    pbr_in = work_dir / "pbr_in"
    pbr_out = work_dir / "pbr_out"
    decals_in = work_dir / "decals_in"
    pbr_in.mkdir(parents=True, exist_ok=True)
    decals_in.mkdir(parents=True, exist_ok=True)

    Image.new("RGB", (1024, 1024), (200, 120, 80)).save(pbr_in / "hero_albedo.png")
    Image.new("RGB", (1024, 1024), (128, 128, 255)).save(pbr_in / "hero_normal.png")
    Image.new("L", (1024, 1024), 180).save(pbr_in / "hero_roughness.png")
    for idx, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 128, 255)], start=1):
        Image.new("RGBA", (256, 256), (*color, 255)).save(decals_in / f"decal_{idx}.png")

    pack = await gimp_batch(
        "pbr_pack",
        str(pbr_in),
        str(pbr_out),
        map_size=512,
        validate_pbr=True,
        pack_prefix="hero",
    )
    steps.append({"name": "offline_pbr_pack", "success": bool(pack.get("success")), "detail": pack})

    audit = await gimp_validation("audit_pbr_pack", str(pbr_out), target_platform="pbr")
    steps.append({"name": "offline_audit_pbr_pack", "success": bool(audit.get("data", {}).get("passed")), "detail": audit})

    decal = await gimp_sim_art(
        "build_decal_sheet",
        input_dir=str(decals_in),
        output_path=str(work_dir / "decal_sheet.png"),
        layout="2x2",
        cell_size=128,
    )
    steps.append({"name": "offline_decal_sheet", "success": bool(decal.get("success")), "detail": decal})

    refine = await gimp_vision_refine(
        "ai_refine_loop",
        input_dir=str(pbr_out),
        goal="CI PBR pack refine",
        target_platform="pbr",
    )
    steps.append({"name": "offline_ai_refine_loop", "success": bool(refine.get("success")), "detail": refine})

    return {
        "success": all(bool(s.get("success")) for s in steps),
        "mode": "offline",
        "steps": steps,
    }
