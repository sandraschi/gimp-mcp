"""Agent vision refinement for GIMP texture review loops."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal

from .validation import gimp_validation

logger = logging.getLogger(__name__)

VisionOperation = Literal["review_bundle", "texture_review", "validate_folder"]


async def build_texture_review_bundle(
    *,
    input_dir: str,
    goal: str = "",
    target_platform: str = "unity",
    include_validation: bool = True,
) -> dict[str, Any]:
    """Build a review bundle manifest for agent vision over a texture folder."""
    root = Path(input_dir)
    if not root.is_dir():
        return {"success": False, "error": f"Input directory not found: {input_dir}"}

    images = sorted(
        p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".tga"}
    )
    if not images:
        return {"success": False, "error": f"No images found under {input_dir}"}

    entries: list[dict[str, Any]] = []
    issue_count = 0
    for image in images:
        entry: dict[str, Any] = {"path": str(image), "name": image.name}
        if include_validation:
            audit = await gimp_validation(
                "audit_texture",
                str(image),
                target_platform=target_platform,
            )
            entry["validation"] = audit
            if audit.get("issues"):
                issue_count += len(audit["issues"])
        entries.append(entry)

    prompt = (
        f"Review {len(entries)} texture(s) for fleet handoff to {target_platform}. "
        f"Goal: {goal or 'Ensure textures are power-of-two, within size limits, and ready for Unity import.'} "
        f"Found {issue_count} validation issue(s). "
        "Suggest GIMP batch fixes (resize, convert PNG, alpha) then re-run gimp_vision_refine."
    )

    return {
        "success": True,
        "operation": "review_bundle",
        "input_dir": str(root),
        "image_count": len(entries),
        "issue_count": issue_count,
        "target_platform": target_platform,
        "entries": entries,
        "agent_prompt": prompt,
    }


async def gimp_vision_refine(
    operation: VisionOperation,
    *,
    input_dir: str | None = None,
    input_path: str | None = None,
    goal: str = "",
    target_platform: str = "unity",
) -> dict[str, Any]:
    """Multi-angle / multi-file texture review for agent loops."""
    if operation == "review_bundle":
        if not input_dir:
            return {"success": False, "error": "input_dir required for review_bundle"}
        return await build_texture_review_bundle(
            input_dir=input_dir,
            goal=goal,
            target_platform=target_platform,
        )

    if operation == "texture_review":
        if not input_path:
            return {"success": False, "error": "input_path required for texture_review"}
        audit = await gimp_validation("audit_texture", input_path, target_platform=target_platform)
        return {
            "success": True,
            "operation": operation,
            "input_path": input_path,
            "validation": audit,
            "agent_prompt": (
                f"Texture audit for {input_path}. "
                f"Passed={audit.get('data', {}).get('passed', False)}. "
                f"Issues: {audit.get('issues', [])}. "
                "Apply gimp_batch resize/convert if needed, then push via gimp_import push_unity."
            ),
        }

    if operation == "validate_folder":
        if not input_dir:
            return {"success": False, "error": "input_dir required for validate_folder"}
        bundle = await build_texture_review_bundle(
            input_dir=input_dir,
            goal=goal,
            target_platform=target_platform,
            include_validation=True,
        )
        if not bundle.get("success"):
            return bundle
        passed = bundle.get("issue_count", 0) == 0
        return {
            **bundle,
            "operation": operation,
            "passed": passed,
            "message": "Folder validation passed" if passed else f"{bundle['issue_count']} issue(s) found",
        }

    return {
        "success": False,
        "error": f"Unknown operation: {operation}",
        "available_operations": ["review_bundle", "texture_review", "validate_folder"],
    }
