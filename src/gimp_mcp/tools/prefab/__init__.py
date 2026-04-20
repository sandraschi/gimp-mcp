"""Prefab UI registration for GIMP MCP."""

from gimp_mcp.logging_config import get_logger

from .gimp_cards import gimp_capabilities_card

logger = get_logger(__name__)


def register_prefab_tools(mcp) -> None:
    """Register Prefab UI tools (requires prefab-ui)."""
    mcp.tool(app=True)(gimp_capabilities_card)
    logger.info("Prefab tool registered: gimp_capabilities_card")


__all__ = ["register_prefab_tools", "gimp_capabilities_card"]
