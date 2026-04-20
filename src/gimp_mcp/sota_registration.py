"""
FastMCP 3.2 SOTA surface: prompts, resources, skills provider, optional prefab tools.
"""

from __future__ import annotations

import os
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from gimp_mcp.logging_config import get_logger

logger = get_logger(__name__)


def _fastmcp_version() -> str:
    try:
        return pkg_version("fastmcp")
    except Exception:
        return "unknown"


def get_sota_feature_manifest() -> dict[str, Any]:
    """JSON-serializable manifest for the web dashboard and health probes."""
    prompt_count = 4

    return {
        "package": "gimp-mcp",
        "fastmcp": _fastmcp_version(),
        "sota_target": "3.2",
        "features": {
            "sampling": True,
            "prompts_registered": prompt_count,
            "resources": [
                "resource://gimp/documentation/llms",
                "resource://gimp/documentation/capabilities",
                "resource://gimp/prefab/manifest",
            ],
            "skills_provider": True,
            "skills_uris": ["skill://gimp-expert/SKILL.md"],
            "prefab_tools": os.getenv("GIMP_PREFAB_TOOLS", "1") != "0",
            "mcpb_packaging": True,
        },
    }


def _register_skills_provider(mcp: FastMCP) -> None:
    skills_dir = Path(__file__).resolve().parent.parent.parent / "skills"
    try:
        from fastmcp.server.providers.skills import SkillsDirectoryProvider
    except ImportError:
        logger.warning("SkillsDirectoryProvider not available — skip skill:// provider")
        return

    if not skills_dir.is_dir():
        logger.warning("Skills directory missing at %s — skip", skills_dir)
        return

    try:
        mcp.add_provider(SkillsDirectoryProvider(roots=[skills_dir]))
        logger.info("Skills provider registered: %s", skills_dir)
    except Exception as e:
        logger.warning("Skills provider failed: %s", e)


def _register_prefab_tools(mcp: FastMCP) -> None:
    if os.getenv("GIMP_PREFAB_TOOLS", "1") == "0":
        logger.info("GIMP_PREFAB_TOOLS=0 — prefab tools skipped")
        return
    try:
        from gimp_mcp.tools.prefab import register_prefab_tools

        register_prefab_tools(mcp)
        logger.info("Prefab tools registered")
    except ImportError as e:
        logger.info("Prefab tools skipped (prefab-ui): %s", e)
    except Exception as e:
        logger.warning("Prefab registration failed: %s", e)


def register_fastmcp_32_surface(mcp: FastMCP) -> None:
    """
    Register prompts, resources, skills provider, and optional prefab tools.

    Call once per FastMCP instance before or after tool registration (idempotent enough
    for separate CLI vs http_app processes).
    """
    from gimp_mcp.prompts import register_all_prompts
    from gimp_mcp.resources import register_resources

    try:
        register_all_prompts(mcp)
        logger.info("Prompts registered")
    except Exception as e:
        logger.warning("Prompt registration failed: %s", e)

    try:
        register_resources(mcp)
        logger.info("Resources registered")
    except Exception as e:
        logger.warning("Resource registration failed: %s", e)

    _register_skills_provider(mcp)
    _register_prefab_tools(mcp)


__all__ = [
    "get_sota_feature_manifest",
    "register_fastmcp_32_surface",
]
