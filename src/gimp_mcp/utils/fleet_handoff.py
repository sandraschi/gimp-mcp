"""Push processed textures into Unity project Assets."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

from .fleet_http import DEFAULT_UNITY_URL, call_http_tool

logger = logging.getLogger(__name__)

DEFAULT_UNITY_TEXTURES_SUBDIR = "GimpImports"


async def push_texture_to_unity(
    *,
    texture_path: str,
    project_path: str,
    texture_type: str = "diffuse",
    assets_subdir: str = DEFAULT_UNITY_TEXTURES_SUBDIR,
    unity_url: str = DEFAULT_UNITY_URL,
) -> dict[str, Any]:
    """Copy texture into Unity Assets and notify unity3d-mcp import_texture."""
    src = Path(texture_path)
    if not src.is_file():
        return {"success": False, "error": f"Texture not found: {texture_path}"}

    project = Path(project_path)
    if not project.is_dir():
        return {"success": False, "error": f"Unity project not found: {project_path}"}

    dest_dir = project / "Assets" / assets_subdir
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
    except OSError as exc:
        logger.exception("Failed to copy texture into Unity Assets")
        return {"success": False, "error": str(exc)}

    unity_result = await call_http_tool(
        unity_url,
        "import_texture",
        {
            "texture_path": str(dest),
            "project_path": project_path,
            "texture_type": texture_type,
        },
        tool_path="/api/v1/tool",
    )

    success = dest.is_file() and unity_result.get("success", True)
    return {
        "success": success,
        "source_path": str(src),
        "destination_path": str(dest),
        "project_path": project_path,
        "texture_type": texture_type,
        "unity_response": unity_result,
        "error": None if success else unity_result.get("error") or "Unity texture handoff failed",
    }
