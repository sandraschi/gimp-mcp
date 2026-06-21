"""
Prefab UI tools — FastMCP 3.2 app=True surfaces for capable MCP hosts.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Text

from ...logging_config import get_logger
from .. import PORTMANTEAU_TOOLS

logger = get_logger(__name__)


async def gimp_capabilities_card(ctx: Context | None = None) -> Any:
    """
    Rich card summarizing GIMP MCP portmanteau tools and SOTA features.
    Returns structured Prefab UI in capable clients; plain summary text otherwise.
    """
    if ctx:
        await ctx.info("Building GIMP MCP capabilities card")

    total_ops = sum(len(t["operations"]) for t in PORTMANTEAU_TOOLS)
    [f"{t['name']}: {len(t['operations'])} ops" for t in PORTMANTEAU_TOOLS]
    summary = (
        f"GIMP MCP — {len(PORTMANTEAU_TOOLS)} portmanteau tools, {total_ops} operations. "
        "FastMCP 3.2: sampling, prompts, resources, skill://gimp-expert, MCPB."
    )

    with Card(css_class="max-w-xl") as view:
        with CardHeader():
            CardTitle("GIMP MCP — Capabilities")
        with CardContent():
            Text("Portmanteau tools (operation parameter):")
            for t in PORTMANTEAU_TOOLS:
                Text(f"• {t['name']} — {', '.join(t['operations'][:6])}{'…' if len(t['operations']) > 6 else ''}")
            Text("SOTA: ctx.sample workflows, resource://gimp/*, skill://gimp-expert/SKILL.md")

    return ToolResult(
        content=summary,
        structured_content=PrefabApp(view=view, title="GIMP MCP"),
    )


__all__ = ["gimp_capabilities_card"]
