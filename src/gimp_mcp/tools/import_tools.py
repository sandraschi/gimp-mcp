"""GIMP fleet import portmanteau (Blender renders -> staging -> Unity)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal

from ..utils.fleet_handoff import push_texture_to_unity
from ..utils.fleet_import import (
    DEFAULT_STAGING_DIR,
    import_file_to_staging,
    import_from_blender_render,
    list_staging_files,
)

logger = logging.getLogger(__name__)

ImportOperation = Literal[
    "import_file",
    "from_blender_render",
    "list_staging",
    "push_unity",
]


async def normalize_texture_png(
    source_path: str,
    output_path: str,
    *,
    size: int = 1024,
) -> dict[str, Any]:
    """Resize/convert to RGBA PNG with power-of-two dimensions for Unity."""
    src = Path(source_path)
    dest = Path(output_path)
    if not src.is_file():
        return {"success": False, "error": f"Source not found: {source_path}"}

    try:
        from PIL import Image

        pot = 1
        while pot < size:
            pot *= 2
        target = min(pot, 4096)

        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as img:
            rgba = img.convert("RGBA")
            resized = rgba.resize((target, target), Image.Resampling.LANCZOS)
            resized.save(dest, "PNG")
    except Exception as exc:
        logger.exception("Texture normalize failed")
        return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "source_path": str(src),
        "output_path": str(dest),
        "width": target,
        "height": target,
    }


async def gimp_import(
    operation: ImportOperation,
    *,
    source_path: str | None = None,
    staging_dir: str | None = None,
    blender_url: str | None = None,
    blender_operation: str = "render_multi_angle",
    angles: int = 4,
    output_path: str | None = None,
    project_path: str | None = None,
    texture_type: str = "diffuse",
    unity_url: str | None = None,
    normalize_size: int = 1024,
) -> dict[str, Any]:
    """Fleet handoff import/export for GIMP texture pipelines."""
    stage = Path(staging_dir) if staging_dir else DEFAULT_STAGING_DIR

    if operation == "import_file":
        if not source_path:
            return {"success": False, "error": "source_path required for import_file"}
        return await import_file_to_staging(source_path=source_path, staging_dir=stage)

    if operation == "from_blender_render":
        return await import_from_blender_render(
            blender_url=blender_url or "http://127.0.0.1:10849",
            output_dir=stage / "blender_renders",
            operation=blender_operation,
            output_path=output_path,
            angles=angles,
        )

    if operation == "list_staging":
        return list_staging_files(stage)

    if operation == "push_unity":
        if not source_path:
            return {"success": False, "error": "source_path required for push_unity"}
        if not project_path:
            return {"success": False, "error": "project_path required for push_unity"}

        processed_dir = stage / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        src = Path(source_path)
        out = processed_dir / f"{src.stem}_pot.png"
        norm = await normalize_texture_png(source_path, str(out), size=normalize_size)
        if not norm.get("success"):
            return norm

        return await push_texture_to_unity(
            texture_path=str(out),
            project_path=project_path,
            texture_type=texture_type,
            unity_url=unity_url or "http://127.0.0.1:10831",
        )

    return {
        "success": False,
        "error": f"Unknown operation: {operation}",
        "available_operations": ["import_file", "from_blender_render", "list_staging", "push_unity"],
    }
