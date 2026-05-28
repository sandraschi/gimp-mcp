"""Fleet import helpers (Blender renders -> GIMP staging)."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

from .fleet_http import DEFAULT_BLENDER_URL, call_http_tool

logger = logging.getLogger(__name__)

DEFAULT_STAGING_DIR = Path("D:/Temp/fleet_pipeline/gimp_staging")
SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tga", ".tif", ".tiff", ".exr"}


async def import_file_to_staging(
    *,
    source_path: str,
    staging_dir: Path | None = None,
    subdir: str = "imports",
) -> dict[str, Any]:
    """Copy an image into the GIMP fleet staging directory."""
    src = Path(source_path)
    if not src.is_file():
        return {"success": False, "error": f"Source file not found: {source_path}"}

    if src.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
        return {
            "success": False,
            "error": f"Unsupported image suffix: {src.suffix}",
            "supported": sorted(SUPPORTED_IMAGE_SUFFIXES),
        }

    root = staging_dir or DEFAULT_STAGING_DIR
    dest_dir = root / subdir
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
    except OSError as exc:
        logger.exception("Failed to copy to staging")
        return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "source_path": str(src),
        "staging_path": str(dest),
        "staging_dir": str(dest_dir),
    }


async def import_from_blender_render(
    *,
    blender_url: str = DEFAULT_BLENDER_URL,
    output_dir: Path | None = None,
    operation: str = "render_multi_angle",
    output_path: str | None = None,
    angles: int = 4,
) -> dict[str, Any]:
    """Fetch renders from blender-mcp into a GIMP staging folder."""
    root = output_dir or DEFAULT_STAGING_DIR / "blender_renders"
    root.mkdir(parents=True, exist_ok=True)

    params: dict[str, Any] = {"operation": operation}
    if operation == "render_multi_angle":
        params["output_dir"] = str(root)
        params["angles"] = angles
    elif operation == "screenshot_viewport":
        if not output_path:
            output_path = str(root / "blender_viewport.png")
        params["output_path"] = output_path
    else:
        return {"success": False, "error": f"Unsupported blender render operation: {operation}"}

    result = await call_http_tool(
        blender_url,
        "blender_render",
        params,
        tool_path="/tool",
    )
    if not result.get("success", True):
        return {
            "success": False,
            "error": result.get("error") or "Blender render failed",
            "blender_response": result,
        }

    files = sorted(
        p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    )
    if operation == "screenshot_viewport" and output_path and Path(output_path).is_file():
        files = [Path(output_path)]

    if not files:
        return {
            "success": False,
            "error": "Blender render reported success but no image files found",
            "staging_dir": str(root),
            "blender_response": result,
        }

    return {
        "success": True,
        "operation": operation,
        "staging_dir": str(root),
        "files": [str(p) for p in files],
        "count": len(files),
        "blender_response": result,
    }


def list_staging_files(staging_dir: Path | None = None) -> dict[str, Any]:
    root = staging_dir or DEFAULT_STAGING_DIR
    if not root.is_dir():
        return {"success": True, "files": [], "count": 0, "staging_dir": str(root)}

    files = sorted(
        str(p) for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    )
    return {"success": True, "files": files, "count": len(files), "staging_dir": str(root)}
