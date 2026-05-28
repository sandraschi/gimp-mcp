"""Automated sim-art import into Gazebo models and avatar-mcp thumbnails."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

import httpx

from .fleet_http import DEFAULT_AVATAR_URL, DEFAULT_ROBOTICS_URL, check_http_health

logger = logging.getLogger(__name__)

DEFAULT_AVATAR_MODELS_DIR = Path.home() / ".avatarmcp" / "models"


def _is_gazebo_model_dir(model_dir: Path) -> bool:
    if not model_dir.is_dir():
        return False
    if (model_dir / "model.config").is_file():
        return True
    if (model_dir / "model.sdf").is_file():
        return True
    return any(model_dir.glob("*.sdf"))


async def call_robotics_tool(
    base_url: str,
    tool_name: str,
    params: dict[str, Any],
    *,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Call robotics-mcp REST tool endpoint POST /api/v1/tools/{tool_name}."""
    url = f"{base_url.rstrip('/')}/api/v1/tools/{tool_name}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=params)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Robotics tool call failed tool=%s url=%s", tool_name, url)
        return {"success": False, "error": str(exc), "tool": tool_name}

    if isinstance(body, dict) and "result" in body:
        result = body["result"]
        if isinstance(result, dict):
            if "success" not in result:
                result = {**result, "success": True}
            return result
        return {"success": True, "result": result}
    return body if isinstance(body, dict) else {"success": False, "error": "Invalid robotics response"}


async def fetch_avatar_models(avatar_url: str = DEFAULT_AVATAR_URL) -> list[dict[str, Any]]:
    """List loaded avatars from avatar-mcp HTTP API."""
    url = f"{avatar_url.rstrip('/')}/api/v1/avatars"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.warning("Avatar list failed: %s", exc)
        return []
    return data if isinstance(data, list) else []


def resolve_avatar_target(
    *,
    model_id: str | None,
    vrm_path: str | None,
    models_dir: Path | None = None,
) -> tuple[Path, str] | None:
    """Resolve avatar thumbnail directory and model id."""
    if vrm_path:
        vrm = Path(vrm_path)
        if vrm.is_file():
            return vrm.parent, vrm.stem

    if not model_id:
        return None

    root = models_dir or DEFAULT_AVATAR_MODELS_DIR
    if root.is_dir():
        for vrm in root.rglob("*.vrm"):
            if vrm.stem == model_id:
                return vrm.parent, model_id

    return None


async def import_icon_to_gazebo_model(
    *,
    icon_path: str,
    model_dir: str,
) -> dict[str, Any]:
    """Copy icon into a local Gazebo model folder (Fuel-style thumbnails)."""
    src = Path(icon_path)
    model = Path(model_dir)
    if not src.is_file():
        return {"success": False, "error": f"Icon not found: {icon_path}"}
    if not _is_gazebo_model_dir(model):
        return {"success": False, "error": f"Not a Gazebo model directory: {model_dir}"}

    try:
        thumb_dir = model / "thumbnails"
        thumb_dir.mkdir(parents=True, exist_ok=True)
        targets = [
            thumb_dir / "1.png",
            model / "model_thumb.png",
            model / "thumbnail.png",
        ]
        written: list[str] = []
        for dest in targets:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            written.append(str(dest))
    except OSError as exc:
        logger.exception("Gazebo model icon import failed")
        return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "model_dir": str(model),
        "icon_path": str(src),
        "import_paths": written,
        "primary_thumbnail": str(thumb_dir / "1.png"),
    }


async def import_icon_to_avatar_model(
    *,
    icon_path: str,
    model_id: str | None = None,
    vrm_path: str | None = None,
    models_dir: str | None = None,
    avatar_url: str = DEFAULT_AVATAR_URL,
) -> dict[str, Any]:
    """Copy icon to avatar-mcp thumbnail path ({model_id}.thumb.png)."""
    src = Path(icon_path)
    if not src.is_file():
        return {"success": False, "error": f"Icon not found: {icon_path}"}

    resolved: tuple[Path, str] | None = None
    avatar_models: list[dict[str, Any]] = []

    if await check_http_health(avatar_url, health_path="/api/v1/health"):
        avatar_models = await fetch_avatar_models(avatar_url)
        if model_id:
            for entry in avatar_models:
                if str(entry.get("id")) == model_id:
                    path = entry.get("path")
                    if path:
                        vrm = Path(str(path))
                        if vrm.is_file():
                            resolved = (vrm.parent, vrm.stem)
                            break

    if resolved is None:
        resolved = resolve_avatar_target(
            model_id=model_id,
            vrm_path=vrm_path,
            models_dir=Path(models_dir) if models_dir else None,
        )

    if resolved is None:
        return {
            "success": False,
            "error": "Could not resolve avatar model. Provide model_id, vrm_path, or start avatar-mcp.",
            "avatar_models_seen": len(avatar_models),
        }

    directory, mid = resolved
    dest = directory / f"{mid}.thumb.png"
    try:
        shutil.copy2(src, dest)
    except OSError as exc:
        logger.exception("Avatar thumbnail import failed")
        return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "model_id": mid,
        "thumbnail_path": str(dest),
        "source_icon": str(src),
        "avatar_url": avatar_url,
        "avatar_api_used": bool(avatar_models),
    }


async def batch_import_gazebo_icons(
    *,
    icons_dir: str,
    models_root: str,
    robotics_url: str = DEFAULT_ROBOTICS_URL,
    notify_robotics: bool = True,
) -> dict[str, Any]:
    """Match icon PNG stems to subfolders under models_root and import thumbnails."""
    icons_path = Path(icons_dir)
    root = Path(models_root)
    if not icons_path.is_dir():
        return {"success": False, "error": f"Icons directory not found: {icons_dir}"}
    if not root.is_dir():
        return {"success": False, "error": f"Models root not found: {models_root}"}

    imports: list[dict[str, Any]] = []
    for icon in sorted(icons_path.glob("*.png")):
        stem = icon.stem
        for suffix in ("_gazebo_icon_256", "_gazebo_icon_512", "_icon_256", "_icon_512"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break

        candidates = [
            root / stem,
            root / "models" / stem,
        ]
        model_dir = next((c for c in candidates if _is_gazebo_model_dir(c)), None)
        if model_dir is None:
            imports.append({"icon": str(icon), "success": False, "error": f"No model dir for {stem}"})
            continue

        result = await import_icon_to_gazebo_model(icon_path=str(icon), model_dir=str(model_dir))
        imports.append({"icon": str(icon), "model_dir": str(model_dir), **result})

    success_count = sum(1 for row in imports if row.get("success"))
    robotics_note: dict[str, Any] | None = None
    if notify_robotics and success_count:
        if await check_http_health(robotics_url, health_path="/api/v1/health"):
            robotics_note = await call_robotics_tool(
                robotics_url,
                "gazebo_models",
                {"operation": "list_local"},
            )

    return {
        "success": success_count > 0 and success_count == len(imports),
        "imported": success_count,
        "total": len(imports),
        "imports": imports,
        "robotics_url": robotics_url,
        "robotics_list_local": robotics_note,
    }
