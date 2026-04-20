"""
GIMP MCP — resource:// documentation surface (FastMCP 3.2+).
skill:// URIs are served via SkillsDirectoryProvider in sota_registration.
"""

from pathlib import Path

from fastmcp import FastMCP

from .logging_config import get_logger

logger = get_logger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def register_resources(mcp: FastMCP) -> None:
    """Register static documentation resources."""

    @mcp.resource("resource://gimp/documentation/llms")
    def get_llms_txt() -> str:
        """Concise LLM-facing capability summary."""
        docs_path = _REPO_ROOT / "llms.txt"
        try:
            return docs_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.warning("llms.txt missing: %s", e)
            return "gimp-mcp: llms.txt not found at repository root."

    @mcp.resource("resource://gimp/documentation/capabilities")
    def get_capabilities_json_hint() -> str:
        """High-level JSON-shaped hint listing portmanteau tools (text, not application/json)."""
        try:
            from .tools import PORTMANTEAU_TOOLS

            lines = ["gimp-mcp portmanteau tools (name → operations):"]
            for t in PORTMANTEAU_TOOLS:
                lines.append(f"- {t['name']}: {', '.join(t['operations'])}")
            return "\n".join(lines) + "\n"
        except Exception as e:
            return f"capabilities unavailable: {e}"

    @mcp.resource("resource://gimp/prefab/manifest")
    def get_prefab_manifest() -> str:
        """Lists prefab UI tools when prefab-ui is enabled."""
        return """Prefab (FastMCP app tools):
- gimp_capabilities_card: Rich card of GIMP MCP surface (portmanteau + SOTA features).
Set GIMP_PREFAB_TOOLS=0 to disable prefab registration.
"""

    logger.info("Resources registered: llms, capabilities, prefab manifest")


__all__ = ["register_resources"]
