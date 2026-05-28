"""Bridge-first runtime helpers for GIMP live vs headless execution."""

from __future__ import annotations

import logging
from typing import Any

from ..bridge_wrapper import GimpBridgeWrapper
from ..config import GimpConfig
from ..interaction_manager import GimpInteractionManager

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = GimpConfig()
_DEFAULT_BRIDGE = GimpBridgeWrapper(_DEFAULT_CONFIG)


def get_bridge_wrapper(config: GimpConfig | None = None) -> GimpBridgeWrapper:
    """Return a bridge client (uses server config when provided)."""
    if config is not None:
        return GimpBridgeWrapper(config)
    return _DEFAULT_BRIDGE


async def bridge_available(
    bridge: GimpBridgeWrapper | None = None,
    config: GimpConfig | None = None,
) -> bool:
    """True when GIMP Live Bridge TCP socket is reachable."""
    client = bridge or get_bridge_wrapper(config)
    try:
        return await client.is_alive()
    except Exception as exc:
        logger.warning("Bridge availability check failed: %s", exc)
        return False


async def execute_bridge_python(
    code: str,
    *,
    bridge: GimpBridgeWrapper | None = None,
    config: GimpConfig | None = None,
    timeout: int | None = None,
) -> dict[str, Any]:
    """Execute Python inside live GIMP via TCP bridge."""
    client = bridge or get_bridge_wrapper(config)
    try:
        result = await client.execute_live_python(code, timeout=timeout)
        if isinstance(result, dict):
            return result
        return {"error": f"Unexpected bridge response type: {type(result).__name__}"}
    except Exception as exc:
        logger.error("Bridge Python execution failed: %s", exc, exc_info=True)
        return {"error": str(exc)}


async def execute_via_manager(
    interaction_manager: GimpInteractionManager | None,
    code: str,
    *,
    timeout: int | None = None,
) -> dict[str, Any]:
    """Run Python-Fu through interaction manager (live first, headless fallback)."""
    if interaction_manager is None:
        return {"success": False, "error": "GIMP interaction manager not initialized"}

    try:
        raw = await interaction_manager.execute_python_fu(code, timeout=timeout)
    except Exception as exc:
        logger.error("Interaction manager execution failed: %s", exc, exc_info=True)
        return {"success": False, "error": str(exc)}

    if raw.startswith("LIVE_SUCCESS|"):
        return {"success": True, "mode": "live", "result": raw.split("|", 1)[1]}
    if raw.startswith("CLI_SUCCESS|"):
        return {"success": True, "mode": "headless", "result": raw.split("|", 1)[1]}
    if raw.startswith("ERROR:"):
        return {"success": False, "error": raw.removeprefix("ERROR:").strip()}

    return {"success": True, "mode": interaction_manager.last_mode, "result": raw}
