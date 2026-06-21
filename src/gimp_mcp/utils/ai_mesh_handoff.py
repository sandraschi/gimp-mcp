"""Tripo / Rodin handoff hints for GIMP texture refine loops (blender-mcp owns generation)."""

from __future__ import annotations

import os
from typing import Any


def _env_flag(name: str) -> bool:
    value = os.getenv(name, "").strip()
    return bool(value)


def build_ai_mesh_handoff(*, goal: str = "", texture_issues: list[str] | None = None) -> dict[str, Any]:
    """Return agent-facing handoff manifest for AI mesh + texture pipelines."""
    tripo_key = _env_flag("TRIPO_API_KEY")
    rodin_key = _env_flag("RODIN_API_KEY") or _env_flag("HYPER3D_API_KEY")
    hunyuan_key = _env_flag("HUNYUAN_API_KEY")

    backends: list[dict[str, Any]] = []
    if rodin_key:
        backends.append(
            {
                "backend": "rodin",
                "mcp_tool": "blender_ai_generate",
                "repo": "blender-mcp",
                "env": ["RODIN_API_KEY", "HYPER3D_API_KEY"],
                "hint": "Generate mesh via Rodin/Hyper3D, bake PBR in Blender, export to GIMP for QA.",
            }
        )
    if tripo_key:
        backends.append(
            {
                "backend": "tripo",
                "mcp_tool": "blender_ai_generate",
                "repo": "blender-mcp",
                "env": ["TRIPO_API_KEY"],
                "hint": "Tripo mesh generation then blender_materials_baking bake_toon_to_pbr.",
            }
        )
    if hunyuan_key:
        backends.append(
            {
                "backend": "hunyuan",
                "mcp_tool": "blender_ai_generate",
                "repo": "blender-mcp",
                "env": ["HUNYUAN_API_KEY"],
            }
        )

    refine_steps = [
        "Run gimp_validation audit_texture (or audit_pbr_pack) on exported maps.",
        "Fix with gimp_batch pbr_pack to normalize size and rename slots.",
        "Re-run gimp_vision_refine validate_folder until issue_count is 0.",
        "Push via gimp_import push_unity or stage for fleet pipeline.",
    ]
    if backends:
        refine_steps.insert(
            0,
            "Generate or refine mesh in blender-mcp (blender_ai_generate), bake PBR textures, export PNG set.",
        )
    else:
        refine_steps.insert(
            0,
            "Set TRIPO_API_KEY or RODIN_API_KEY for blender-mcp AI mesh generation; local GIMP refine still works.",
        )

    return {
        "goal": goal or "Fleet-ready PBR texture pack",
        "texture_issues": texture_issues or [],
        "available_backends": backends,
        "backends_configured": bool(backends),
        "refine_loop": refine_steps,
        "blender_mcp_url": os.getenv("BLENDER_MCP_URL", "http://127.0.0.1:10849"),
        "gimp_batch_operation": "pbr_pack",
        "gimp_validation_operation": "audit_pbr_pack",
    }
