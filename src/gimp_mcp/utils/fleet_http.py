"""HTTP helpers for cross-fleet MCP tool calls."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BLENDER_URL = "http://127.0.0.1:10849"
DEFAULT_UNITY_URL = "http://127.0.0.1:10831"
DEFAULT_GIMP_URL = "http://127.0.0.1:10773"
DEFAULT_ROBOTICS_URL = "http://127.0.0.1:10892"
DEFAULT_AVATAR_URL = "http://127.0.0.1:10793"


async def check_http_health(base_url: str, *, health_path: str = "/api/health") -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(base_url.rstrip("/") + health_path)
            return response.status_code == 200
    except httpx.HTTPError:
        return False


async def call_http_tool(
    base_url: str,
    tool: str,
    params: dict[str, Any],
    *,
    tool_path: str = "/api/v1/tool",
    timeout: float = 300.0,
) -> dict[str, Any]:
    """Call a fleet MCP POST tool endpoint."""
    url = base_url.rstrip("/") + tool_path
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json={"tool": tool, "params": params})
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.exception("HTTP tool call failed tool=%s url=%s", tool, url)
        return {"success": False, "error": str(exc), "tool": tool}

    if isinstance(body, dict) and body.get("data") is not None:
        data = body["data"]
        if isinstance(data, dict):
            if body.get("success") is False and "success" not in data:
                data = {**data, "success": False}
            elif "success" not in data:
                data = {**data, "success": bool(body.get("success", True))}
            return data
    return body if isinstance(body, dict) else {"success": False, "error": "Invalid tool response"}


async def call_avatar_execute(
    base_url: str,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Call avatar-mcp POST /api/v1/tools/execute."""
    url = base_url.rstrip("/") + "/api/v1/tools/execute"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                json={"tool_name": tool_name, "arguments": arguments},
            )
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Avatar execute failed tool=%s url=%s", tool_name, url)
        return {"success": False, "error": str(exc), "tool": tool_name}

    if isinstance(body, dict) and body.get("status") == "success":
        result = body.get("result")
        if isinstance(result, dict):
            ok = result.get("status") == "success" or result.get("success", True)
            return {**result, "success": ok}
        return {"success": True, "result": result}
    return body if isinstance(body, dict) else {"success": False, "error": "Invalid avatar response"}


async def set_avatar_thumbnail_http(
    base_url: str,
    avatar_id: str,
    icon_path: str,
) -> dict[str, Any]:
    """Call avatar-mcp REST thumbnail endpoint."""
    url = f"{base_url.rstrip('/')}/api/v1/avatars/{avatar_id}/thumbnail"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json={"icon_path": icon_path})
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPError as exc:
        logger.exception("Avatar thumbnail HTTP failed avatar_id=%s", avatar_id)
        return {"success": False, "error": str(exc)}

    if isinstance(body, dict):
        return {**body, "success": body.get("status") == "success" or body.get("success", True)}
    return {"success": False, "error": "Invalid avatar thumbnail response"}


def parse_tool_payload(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        if "data" in result and isinstance(result["data"], dict):
            return result["data"]
        return result
    content = getattr(result, "content", None)
    if content:
        text = getattr(content[0], "text", str(content[0]))
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"output": text}
    return {"raw": str(result)}
