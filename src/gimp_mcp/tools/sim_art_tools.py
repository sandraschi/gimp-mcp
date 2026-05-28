"""Robotics and sim-art portmanteau (Gazebo icons, atlases, VRChat handoff)."""

from __future__ import annotations

import json
import logging
import shutil
import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from ..utils.fleet_http import DEFAULT_AVATAR_URL, DEFAULT_ROBOTICS_URL, check_http_health
from ..utils.fleet_sim_handoff import (
    batch_import_gazebo_icons,
    import_icon_to_avatar_model,
    import_icon_to_gazebo_model,
)
from ..utils.sim_art_templates import (
    ATLAS_LAYOUTS,
    DEFAULT_SIM_STAGING,
    list_atlas_layouts,
    list_template_catalog,
    resolve_template,
)
from .validation import gimp_validation

logger = logging.getLogger(__name__)

SimArtOperation = Literal[
    "list_templates",
    "gazebo_model_icons",
    "build_atlas",
    "build_decal_sheet",
    "vrchat_icon_batch",
    "stage_for_robotics",
    "push_avatar_handoff",
    "import_gazebo_model",
    "import_avatar_model",
    "batch_import_gazebo",
]


class SimArtResult(BaseModel):
    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    files: list[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    error: str | None = None


def _resize_cover(img: Any, target_w: int, target_h: int) -> Any:
    from PIL import Image

    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _iter_images(input_dir: Path, *, recursive: bool = False) -> list[Path]:
    patterns = ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.tga")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(input_dir.rglob(pattern) if recursive else input_dir.glob(pattern))
    return sorted({p.resolve() for p in files if p.is_file()})


async def _batch_template_icons(
    *,
    input_dir: Path,
    output_dir: Path,
    template_id: str,
    validate: bool,
    target_platform: str,
) -> dict[str, Any]:
    template = resolve_template(template_id)
    if template is None:
        return {"success": False, "error": f"Unknown template: {template_id}"}
    if not input_dir.is_dir():
        return {"success": False, "error": f"Input directory not found: {input_dir}"}

    try:
        from PIL import Image
    except ImportError as exc:
        return {"success": False, "error": f"Pillow required: {exc}"}

    output_dir.mkdir(parents=True, exist_ok=True)
    tw = int(template["width"])
    th = int(template["height"])
    outputs: list[str] = []
    failures: list[dict[str, str]] = []

    for src in _iter_images(input_dir):
        dest = output_dir / f"{src.stem}_{template_id}.png"
        try:
            with Image.open(src) as img:
                rgba = img.convert("RGBA")
                fitted = _resize_cover(rgba, tw, th)
                fitted.save(dest, "PNG")
            outputs.append(str(dest))
            if validate:
                audit = await gimp_validation(
                    "audit_texture",
                    str(dest),
                    target_platform=target_platform,
                    require_alpha=bool(template["require_alpha"]),
                )
                passed = bool(audit.get("data", {}).get("passed", not audit.get("issues")))
                if not passed:
                    failures.append({"path": str(dest), "issues": str(audit.get("issues", []))})
        except Exception as exc:
            logger.exception("Sim art batch failed for %s", src)
            failures.append({"path": str(src), "issues": str(exc)})

    if not outputs:
        return {"success": False, "error": "No input images processed", "failures": failures}

    return {
        "success": len(failures) == 0,
        "template_id": template_id,
        "output_dir": str(output_dir),
        "files": outputs,
        "count": len(outputs),
        "failures": failures,
    }


async def _build_texture_atlas(
    *,
    input_dir: Path,
    output_path: Path,
    layout: str,
    cell_size: int,
    margin_px: int = 0,
    bleed_px: int = 0,
) -> dict[str, Any]:
    if layout not in ATLAS_LAYOUTS:
        return {"success": False, "error": f"Unknown layout: {layout}. Use list_templates layouts."}

    cols, rows = ATLAS_LAYOUTS[layout]
    sources = _iter_images(input_dir)
    max_cells = cols * rows
    if not sources:
        return {"success": False, "error": f"No images in {input_dir}"}
    if len(sources) > max_cells:
        sources = sources[:max_cells]

    margin_px = max(0, margin_px)
    bleed_px = max(0, bleed_px)
    stride = cell_size + margin_px

    try:
        from PIL import Image
    except ImportError as exc:
        return {"success": False, "error": f"Pillow required: {exc}"}

    atlas_w = cols * stride - margin_px
    atlas_h = rows * stride - margin_px
    atlas = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    manifest_entries: list[dict[str, Any]] = []

    for index, src in enumerate(sources):
        col = index % cols
        row = index // cols
        x = col * stride
        y = row * stride
        with Image.open(src) as img:
            inner = max(1, cell_size - bleed_px * 2)
            cell = _resize_cover(img.convert("RGBA"), inner, inner)
            if bleed_px > 0:
                padded = Image.new("RGBA", (cell_size, cell_size), (0, 0, 0, 0))
                padded.paste(cell, (bleed_px, bleed_px))
                cell = padded
            else:
                cell = cell.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
            atlas.paste(cell, (x, y))
        content_u0 = (x + bleed_px) / atlas_w if atlas_w else 0.0
        content_v0 = (y + bleed_px) / atlas_h if atlas_h else 0.0
        content_u1 = (x + cell_size - bleed_px) / atlas_w if atlas_w else 1.0
        content_v1 = (y + cell_size - bleed_px) / atlas_h if atlas_h else 1.0
        manifest_entries.append(
            {
                "source": str(src),
                "name": src.stem,
                "cell_index": index,
                "column": col,
                "row": row,
                "margin_px": margin_px,
                "bleed_px": bleed_px,
                "cell_size": cell_size,
                "pixel_rect": {"x": x, "y": y, "w": cell_size, "h": cell_size},
                "uv": {
                    "u0": round(x / atlas_w, 6),
                    "v0": round(y / atlas_h, 6),
                    "u1": round((x + cell_size) / atlas_w, 6),
                    "v1": round((y + cell_size) / atlas_h, 6),
                },
                "uv_content": {
                    "u0": round(content_u0, 6),
                    "v0": round(content_v0, 6),
                    "u1": round(content_u1, 6),
                    "v1": round(content_v1, 6),
                },
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output_path, "PNG")
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest = {
        "layout": layout,
        "columns": cols,
        "rows": rows,
        "cell_size": cell_size,
        "margin_px": margin_px,
        "bleed_px": bleed_px,
        "stride": stride,
        "atlas_path": str(output_path),
        "width": atlas_w,
        "height": atlas_h,
        "entries": manifest_entries,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "success": True,
        "atlas_path": str(output_path),
        "manifest_path": str(manifest_path),
        "cell_count": len(manifest_entries),
        "layout": layout,
        "width": atlas_w,
        "height": atlas_h,
        "margin_px": margin_px,
        "bleed_px": bleed_px,
    }


async def _stage_files(
    *,
    source_dir: Path,
    staging_subdir: str,
    staging_root: Path,
) -> dict[str, Any]:
    if not source_dir.is_dir():
        return {"success": False, "error": f"Source directory not found: {source_dir}"}

    dest = staging_root / staging_subdir
    dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for src in _iter_images(source_dir):
        target = dest / src.name
        shutil.copy2(src, target)
        copied.append(str(target))

    return {
        "success": bool(copied),
        "staging_dir": str(dest),
        "files": copied,
        "count": len(copied),
    }


async def gimp_sim_art(
    operation: SimArtOperation,
    *,
    input_dir: str | None = None,
    output_dir: str | None = None,
    output_path: str | None = None,
    icon_path: str | None = None,
    template_id: str = "gazebo_icon_256",
    layout: str = "4x4",
    cell_size: int = 256,
    margin_px: int = 0,
    bleed_px: int = 0,
    validate: bool = True,
    target_platform: str = "gazebo",
    staging_dir: str | None = None,
    robotics_url: str | None = None,
    avatar_url: str | None = None,
    model_dir: str | None = None,
    models_root: str | None = None,
    model_id: str | None = None,
    vrm_path: str | None = None,
    avatar_models_dir: str | None = None,
    auto_import: bool = False,
    recursive: bool = False,
) -> dict[str, Any]:
    """Robotics and sim-art batch portmanteau for Gazebo, VRChat, and fleet atlases."""
    start = time.time()
    stage_root = Path(staging_dir) if staging_dir else Path(DEFAULT_SIM_STAGING)

    try:
        if operation == "list_templates":
            payload = {
                "templates": list_template_catalog(),
                "atlas_layouts": list_atlas_layouts(),
                "default_staging": str(stage_root),
                "robotics_url": robotics_url or DEFAULT_ROBOTICS_URL,
                "avatar_url": avatar_url or DEFAULT_AVATAR_URL,
            }
            return SimArtResult(
                success=True,
                operation=operation,
                message="Sim-art template catalog",
                data=payload,
            ).model_dump()

        if operation == "gazebo_model_icons":
            if not input_dir:
                return SimArtResult(
                    success=False,
                    operation=operation,
                    message="input_dir required",
                    error="input_dir required",
                ).model_dump()
            out = Path(output_dir) if output_dir else stage_root / "gazebo_icons"
            batch = await _batch_template_icons(
                input_dir=Path(input_dir),
                output_dir=out,
                template_id=template_id if template_id.startswith("gazebo") else "gazebo_icon_256",
                validate=validate,
                target_platform=target_platform or "gazebo",
            )
            elapsed = (time.time() - start) * 1000
            return SimArtResult(
                success=bool(batch.get("success")),
                operation=operation,
                message=f"Processed {batch.get('count', 0)} Gazebo icon(s)",
                data=batch,
                files=list(batch.get("files") or []),
                execution_time_ms=round(elapsed, 2),
                error=None if batch.get("success") else str(batch.get("error") or batch.get("failures")),
            ).model_dump()

        if operation == "vrchat_icon_batch":
            if not input_dir:
                return SimArtResult(
                    success=False,
                    operation=operation,
                    message="input_dir required",
                    error="input_dir required",
                ).model_dump()
            tid = template_id if template_id.startswith("vrchat") else "vrchat_profile_256"
            out = Path(output_dir) if output_dir else stage_root / "vrchat_icons"
            batch = await _batch_template_icons(
                input_dir=Path(input_dir),
                output_dir=out,
                template_id=tid,
                validate=validate,
                target_platform="vrchat",
            )
            elapsed = (time.time() - start) * 1000
            return SimArtResult(
                success=bool(batch.get("success")),
                operation=operation,
                message=f"Processed {batch.get('count', 0)} VRChat icon(s)",
                data=batch,
                files=list(batch.get("files") or []),
                execution_time_ms=round(elapsed, 2),
            ).model_dump()

        if operation in ("build_atlas", "build_decal_sheet"):
            if not input_dir:
                return SimArtResult(
                    success=False,
                    operation=operation,
                    message="input_dir required",
                    error="input_dir required",
                ).model_dump()
            use_margin = margin_px
            use_bleed = bleed_px
            if operation == "build_decal_sheet":
                use_margin = margin_px if margin_px > 0 else 4
                use_bleed = bleed_px if bleed_px > 0 else 2
            atlas_out = Path(output_path) if output_path else stage_root / "atlases" / f"decal_{layout}.png"
            if operation == "build_atlas" and output_path is None and margin_px == 0 and bleed_px == 0:
                atlas_out = stage_root / "atlases" / f"atlas_{layout}.png"
            atlas = await _build_texture_atlas(
                input_dir=Path(input_dir),
                output_path=atlas_out,
                layout=layout,
                cell_size=cell_size,
                margin_px=use_margin,
                bleed_px=use_bleed,
            )
            elapsed = (time.time() - start) * 1000
            files = [str(atlas["atlas_path"]), str(atlas["manifest_path"])] if atlas.get("success") else []
            return SimArtResult(
                success=bool(atlas.get("success")),
                operation=operation,
                message=f"Decal sheet {layout} with {atlas.get('cell_count', 0)} cell(s)"
                if operation == "build_decal_sheet"
                else f"Atlas {layout} with {atlas.get('cell_count', 0)} cell(s)",
                data=atlas,
                files=files,
                execution_time_ms=round(elapsed, 2),
                error=atlas.get("error"),
            ).model_dump()

        if operation == "import_gazebo_model":
            if not icon_path or not model_dir:
                return SimArtResult(
                    success=False,
                    operation=operation,
                    message="icon_path and model_dir required",
                    error="icon_path and model_dir required",
                ).model_dump()
            imported = await import_icon_to_gazebo_model(icon_path=icon_path, model_dir=model_dir)
            elapsed = (time.time() - start) * 1000
            return SimArtResult(
                success=bool(imported.get("success")),
                operation=operation,
                message="Gazebo model thumbnail imported",
                data=imported,
                files=list(imported.get("import_paths") or []),
                execution_time_ms=round(elapsed, 2),
                error=imported.get("error"),
            ).model_dump()

        if operation == "import_avatar_model":
            if not icon_path:
                return SimArtResult(
                    success=False,
                    operation=operation,
                    message="icon_path required",
                    error="icon_path required",
                ).model_dump()
            imported = await import_icon_to_avatar_model(
                icon_path=icon_path,
                model_id=model_id,
                vrm_path=vrm_path,
                models_dir=avatar_models_dir,
                avatar_url=avatar_url or DEFAULT_AVATAR_URL,
            )
            elapsed = (time.time() - start) * 1000
            files = [str(imported["thumbnail_path"])] if imported.get("thumbnail_path") else []
            return SimArtResult(
                success=bool(imported.get("success")),
                operation=operation,
                message="Avatar thumbnail imported",
                data=imported,
                files=files,
                execution_time_ms=round(elapsed, 2),
                error=imported.get("error"),
            ).model_dump()

        if operation == "batch_import_gazebo":
            icons = input_dir or str(stage_root / "gazebo_icons")
            root = models_root
            if not root:
                return SimArtResult(
                    success=False,
                    operation=operation,
                    message="models_root required",
                    error="models_root required",
                ).model_dump()
            imported = await batch_import_gazebo_icons(
                icons_dir=icons,
                models_root=root,
                robotics_url=robotics_url or DEFAULT_ROBOTICS_URL,
            )
            elapsed = (time.time() - start) * 1000
            return SimArtResult(
                success=bool(imported.get("success")),
                operation=operation,
                message=f"Imported {imported.get('imported', 0)}/{imported.get('total', 0)} Gazebo thumbnails",
                data=imported,
                execution_time_ms=round(elapsed, 2),
                error=None if imported.get("success") else "Some imports failed",
            ).model_dump()

        if operation == "stage_for_robotics":
            src = Path(input_dir) if input_dir else stage_root / "gazebo_icons"
            staged = await _stage_files(
                source_dir=src,
                staging_subdir="robotics_staging",
                staging_root=stage_root,
            )
            r_url = robotics_url or DEFAULT_ROBOTICS_URL
            robotics_online = await check_http_health(r_url, health_path="/api/v1/health")
            if not robotics_online:
                robotics_online = await check_http_health(r_url, health_path="/health")
            staged["robotics_url"] = r_url
            staged["robotics_reachable"] = robotics_online
            import_result: dict[str, Any] | None = None
            if auto_import and models_root:
                import_result = await batch_import_gazebo_icons(
                    icons_dir=str(src),
                    models_root=models_root,
                    robotics_url=r_url,
                    notify_robotics=robotics_online,
                )
                staged["auto_import"] = import_result
            elif auto_import and model_dir and icon_path:
                import_result = await import_icon_to_gazebo_model(icon_path=icon_path, model_dir=model_dir)
                staged["auto_import"] = import_result
            else:
                staged["hint"] = "Set auto_import=true with models_root for automated Gazebo model thumbnail import."
            elapsed = (time.time() - start) * 1000
            success = bool(staged.get("success"))
            if import_result is not None:
                success = success and bool(import_result.get("success", True))
            return SimArtResult(
                success=success,
                operation=operation,
                message="Staged icons for robotics-mcp" + (" with auto-import" if import_result else ""),
                data=staged,
                files=list(staged.get("files") or []),
                execution_time_ms=round(elapsed, 2),
            ).model_dump()

        if operation == "push_avatar_handoff":
            src = Path(input_dir) if input_dir else stage_root / "vrchat_icons"
            staged = await _stage_files(
                source_dir=src,
                staging_subdir="avatar_staging",
                staging_root=stage_root,
            )
            a_url = avatar_url or DEFAULT_AVATAR_URL
            avatar_online = await check_http_health(a_url, health_path="/api/v1/health")
            if not avatar_online:
                avatar_online = await check_http_health(a_url, health_path="/health")
            staged["avatar_url"] = a_url
            staged["avatar_reachable"] = avatar_online
            import_result = None
            if auto_import:
                chosen_icon = icon_path
                if not chosen_icon:
                    icons = _iter_images(src)
                    chosen_icon = str(icons[0]) if icons else None
                if chosen_icon and (model_id or vrm_path):
                    import_result = await import_icon_to_avatar_model(
                        icon_path=chosen_icon,
                        model_id=model_id,
                        vrm_path=vrm_path,
                        models_dir=avatar_models_dir,
                        avatar_url=a_url,
                    )
                    staged["auto_import"] = import_result
                else:
                    staged["hint"] = "auto_import requires model_id or vrm_path plus icons in input_dir."
            else:
                staged["hint"] = "Set auto_import=true with model_id for automated avatar thumbnail import."
            elapsed = (time.time() - start) * 1000
            success = bool(staged.get("success"))
            if import_result is not None:
                success = success and bool(import_result.get("success"))
            return SimArtResult(
                success=success,
                operation=operation,
                message="Avatar handoff" + (" with auto-import" if import_result else ""),
                data=staged,
                files=list(staged.get("files") or []),
                execution_time_ms=round(elapsed, 2),
            ).model_dump()

        return SimArtResult(
            success=False,
            operation=operation,
            message="Unknown operation",
            error=f"Unsupported operation: {operation}",
        ).model_dump()
    except Exception as exc:
        logger.exception("gimp_sim_art failed operation=%s", operation)
        elapsed = (time.time() - start) * 1000
        return SimArtResult(
            success=False,
            operation=operation,
            message="Sim art operation failed",
            error=str(exc),
            execution_time_ms=round(elapsed, 2),
        ).model_dump()
