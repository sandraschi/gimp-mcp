"""
ASGI app for uvicorn (webapp/start.ps1).

Use: uvicorn gimp_mcp.http_app:app --host 127.0.0.1 --port <BackendPort>

Builds FastMCP, GimpMcpServer with default config, registers tools, exposes http_app().
"""

from fastmcp import FastMCP

from .config import GimpConfig
from .server import GimpMcpServer

_config = GimpConfig()
_gimp_server = GimpMcpServer(_config)
_mcp = FastMCP("GIMP MCP")
_gimp_server.register_tools(_mcp)

app = _mcp.http_app()
