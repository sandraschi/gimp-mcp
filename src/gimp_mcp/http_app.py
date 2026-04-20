"""
ASGI app for uvicorn (webapp/start.ps1).

Use: uvicorn gimp_mcp.http_app:app --host 127.0.0.1 --port <BackendPort>

Registers FastMCP 3.2 surface (prompts, resources, skills, prefab) via
:class:`~gimp_mcp.server.GimpMcpServer`, then exposes custom /api/* routes.
"""

from __future__ import annotations

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .config import GimpConfig
from .server import GimpMcpServer
from .sota_registration import get_sota_feature_manifest

_config = GimpConfig()
_mcp = FastMCP(
    name="gimp-mcp",
    version="4.0.0",
    instructions=(
        "GIMP MCP — FastMCP 3.2 SOTA. Portmanteau tools + sampling + prompts + resources + "
        "skill://gimp-expert/SKILL.md. Prefer allowed_directories-safe paths."
    ),
    strict_input_validation=True,
    mask_error_details=True,
    client_log_level="info",
)
_gimp_server = GimpMcpServer(_config)
_gimp_server.register_tools(_mcp)


@_mcp.custom_route("/api/health", methods=["GET"])
async def _api_health(_request: Request) -> Response:
    return JSONResponse(
        {
            "status": "healthy",
            "server_name": "gimp-mcp",
            "version": "4.0.0",
            "fastmcp": "3.2",
            "sota": get_sota_feature_manifest(),
            "stack": "GimpMcpServer (plugin tools); use `gimp-mcp` CLI for portmanteau + agentic",
        }
    )


@_mcp.custom_route("/api/status", methods=["GET"])
async def _api_status(request: Request) -> Response:
    return await _api_health(request)


@_mcp.custom_route("/api/sota", methods=["GET"])
async def _api_sota(_request: Request) -> Response:
    return JSONResponse(get_sota_feature_manifest())


app = _mcp.http_app()
