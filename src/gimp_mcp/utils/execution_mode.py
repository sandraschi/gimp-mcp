"""Dual-mode execution helpers (Hands-In live GUI vs Hands-Off headless CLI)."""

from __future__ import annotations

from typing import Any

from ..config import GimpConfig
from ..interaction_manager import GimpInteractionManager
from .gimp_runtime import bridge_available, get_bridge_wrapper


async def describe_execution_mode(
    *,
    interaction_manager: GimpInteractionManager | None = None,
    config: GimpConfig | None = None,
) -> dict[str, Any]:
    """Return current Hands-In vs Hands-Off mode for agents and webapp."""
    cfg = config or (interaction_manager.config if interaction_manager else GimpConfig())
    bridge = get_bridge_wrapper(cfg)
    alive = await bridge_available(bridge, cfg)

    if alive:
        return {
            "success": True,
            "mode": "hands_in",
            "label": "Hands-In (Live GUI)",
            "bridge_connected": True,
            "bridge_port": cfg.bridge_port,
            "bridge_host": cfg.bridge_host,
            "live_capabilities": [
                "Real-time PDB/Python-Fu in open GIMP documents",
                "gimp_render capture_active for agent vision loops",
                "gimp_workspace list_images / undo on live canvas",
                "Interactive filter preview before batch export",
            ],
            "headless_note": "Batch folder jobs still route through gimp-console when bridge is offline.",
        }

    headless_ok = bool(
        interaction_manager
        and interaction_manager.cli
        and interaction_manager.cli.is_available()
    )

    return {
        "success": True,
        "mode": "hands_off",
        "label": "Hands-Off (Headless CLI)",
        "bridge_connected": False,
        "bridge_port": cfg.bridge_port,
        "bridge_host": cfg.bridge_host,
        "headless_available": headless_ok,
        "available_capabilities": [
            "gimp_file / gimp_batch disk pipelines via gimp-console",
            "PIL-backed save/convert when GIMP GUI is closed",
            "Script-Fu batch through CLI wrapper",
            "Fleet HTTP webapp on :10773",
        ],
        "live_gui_hint": (
            "Open GIMP, run Filters > Development > MCP > Start MCP Bridge, "
            "then gimp_bridge operation=execution_mode should report hands_in."
        ),
    }
