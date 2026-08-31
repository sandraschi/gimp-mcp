"""GIMP live bridge and agent vision portmanteau tools."""

from __future__ import annotations

import base64
import json
import logging
import tempfile
from pathlib import Path
from typing import Any, Literal

from ..config import GimpConfig
from ..interaction_manager import GimpInteractionManager
from ..utils.execution_mode import describe_execution_mode
from ..utils.gimp_runtime import bridge_available, execute_bridge_python, get_bridge_wrapper
from ..utils.telemetry import set_bridge_connected, set_execution_mode

logger = logging.getLogger(__name__)

BridgeOperation = Literal["status", "execution_mode", "ping", "list_open_images"]
RenderOperation = Literal["bridge_status", "capture_active", "get_image_summary"]


def _snapshot_python(max_size: int | None = None, region: dict | None = None) -> str:
    """Generate bridge Python that returns a base64 PNG of the active image.

    Optionally crops to a region and/or scales to fit within max_size.
    """
    escaped = "/tmp/_gimp_snap.png"  # noqa: S108
    lines = [
        "import base64 as _b64, traceback as _tb",
        "from gi.repository import Gimp, Gio",
        "try:",
        "  images = Gimp.get_images()",
        "  if not images: raise RuntimeError('No open images')",
        "  img = images[0]",
    ]
    if region:
        x = region.get("x", 0)
        y = region.get("y", 0)
        w = region.get("width", 100)
        h = region.get("height", 100)
        lines.append(f"  img = img.crop({x}, {y}, {w}, {h})")
    if max_size:
        lines.append(f"  scale = min({max_size} / img.get_width(), {max_size} / img.get_height(), 1.0)")
        lines.append("  if scale < 1.0:")
        lines.append("    img = img.scale(int(img.get_width() * scale), int(img.get_height() * scale))")
    lines += [
        f"  _file = Gio.File.new_for_path('{escaped}')",
        "  _pdb = Gimp.get_pdb()",
        "  _proc = _pdb.lookup_procedure('file-png-export')",
        "  if _proc is None: raise RuntimeError('file-png-export not found')",
        "  _cfg = _proc.create_config()",
        "  _cfg.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)",
        "  _cfg.set_property('image', img)",
        "  _cfg.set_property('file', _file)",
        "  _proc.run(_cfg)",
        f"  with open('{escaped}', 'rb') as _fh: _raw = _fh.read()",
        "  _b64 = _b64.b64encode(_raw).decode('ascii')",
        "  print('SNAPSHOT:' + _b64)",
        "except Exception:",
        "  print('ERROR:' + _tb.format_exc())",
    ]
    return "\n".join(lines)


def _capture_active_python(output_path: str) -> str:
    """Generate GIMP 3 Python-Fu that exports the active image to a PNG path."""
    escaped = output_path.replace("\\", "\\\\").replace('"', '\\"')
    return f'''
import traceback as _tb
try:
    from gi.repository import Gimp, Gio
    _images = Gimp.get_images()
    if not _images:
        raise RuntimeError("No open images in GIMP")
    _img = _images[0]
    _drawables = _img.list_layers()
    if not _drawables:
        raise RuntimeError("Active image has no layers")
    _layer = _drawables[0]
    _file = Gio.File.new_for_path("{escaped}")
    _pdb = Gimp.get_pdb()
    _proc = _pdb.lookup_procedure("file-png-export")
    if _proc is None:
        raise RuntimeError("file-png-export procedure not found")
    _config = _proc.create_config()
    _config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    _config.set_property("image", _img)
    _config.set_property("file", _file)
    _config.set_property("options", None)
    _proc.run(_config)
except Exception:
    raise RuntimeError(_tb.format_exc())
'''


def _image_summary_python(summary_path: str) -> str:
    """Generate live-bridge Python that writes open-image summary JSON to disk."""
    escaped = summary_path.replace("\\", "\\\\").replace('"', '\\"')
    return f'''
import json as _json, traceback as _tb
_out = "{escaped}"
try:
    from gi.repository import Gimp
    _images = Gimp.get_images()
    _result = []
    for _img in _images:
        _layers = _img.list_layers()
        _result.append({{
            "id": _img.get_id(),
            "width": _img.get_width(),
            "height": _img.get_height(),
            "layer_count": len(_layers),
        }})
    _payload = {{"images": _result, "count": len(_result)}}
except Exception:
    _payload = {{"error": _tb.format_exc(), "images": [], "count": 0}}
with open(_out, "w", encoding="utf-8") as _fh:
    _json.dump(_payload, _fh)
'''


async def gimp_bridge(
    operation: BridgeOperation,
    *,
    interaction_manager: GimpInteractionManager | None = None,
    config: GimpConfig | None = None,
) -> dict[str, Any]:
    """Live GIMP bridge portmanteau (TCP plugin on :10824).

    Operations:
        status - bridge connectivity and mode
        execution_mode - Hands-In vs Hands-Off guidance for agents
        ping - trivial live bridge round-trip
        list_open_images - summarize open documents (live or headless)
    """
    cfg = config or (interaction_manager.config if interaction_manager else GimpConfig())
    bridge = get_bridge_wrapper(cfg)

    if operation == "execution_mode":
        result = await describe_execution_mode(interaction_manager=interaction_manager, config=cfg)
        if result.get("success"):
            set_bridge_connected(bool(result.get("bridge_connected")))
            set_execution_mode(result.get("mode") == "hands_in")
        return result

    if operation == "status":
        alive = await bridge_available(bridge, cfg)
        mode = "hands_in" if alive else "hands_off"
        set_bridge_connected(alive)
        set_execution_mode(alive)
        return {
            "success": True,
            "status": "connected" if alive else "disconnected",
            "mode": mode,
            "bridge_port": cfg.bridge_port,
            "bridge_host": cfg.bridge_host,
            "bridge_plugin": "Filters > Development > MCP > Start MCP Bridge",
            "message": f"GIMP bridge is {'connected' if alive else 'offline'} ({mode})",
        }

    if operation == "ping":
        alive = await bridge_available(bridge, cfg)
        if not alive:
            return {
                "success": False,
                "error": "GIMP Live Bridge offline",
                "hint": "Start MCP Bridge inside GIMP or use hands_off batch tools",
            }
        result = await execute_bridge_python("pass  # gimp_bridge ping", bridge=bridge, config=cfg)
        if result.get("error"):
            return {"success": False, "error": result["error"]}
        return {"success": True, "message": "GIMP bridge ping OK", "bridge_result": result.get("result")}

    if operation == "list_open_images":
        if not await bridge_available(bridge, cfg):
            return {
                "success": False,
                "error": "GIMP Live Bridge required for list_open_images",
                "hint": "Start MCP Bridge in GIMP or use gimp_file on disk paths",
            }

        summary_path = Path(tempfile.gettempdir()) / "gimp_mcp_open_images.json"
        try:
            if summary_path.is_file():
                summary_path.unlink()
        except OSError as exc:
            logger.warning("Could not clear prior summary file: %s", exc)

        code = _image_summary_python(str(summary_path))
        result = await execute_bridge_python(code, bridge=bridge, config=cfg)
        if result.get("error"):
            return {"success": False, "error": result["error"], "mode": "live"}

        if not summary_path.is_file():
            return {
                "success": False,
                "error": "Bridge ran but open-image summary file was not written",
                "mode": "live",
            }

        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"success": False, "error": f"Failed to read image summary: {exc}", "mode": "live"}

        if payload.get("error"):
            return {"success": False, "error": payload["error"], "mode": "live"}

        return {"success": True, "mode": "live", "data": payload}

    return {
        "success": False,
        "error": f"Unknown operation: {operation}",
        "available_operations": ["status", "execution_mode", "ping", "list_open_images"],
    }


async def get_state_snapshot(
    *,
    max_size: int = 1024,
    region: dict[str, int] | None = None,
    interaction_manager: GimpInteractionManager | None = None,
    config: GimpConfig | None = None,
) -> dict[str, Any]:
    """Return a live base64 PNG of the current GIMP image state.

    Ported from the maorcc/gimp-mcp pattern - enables the AI to "see"
    the current image mid-workflow without saving to disk.
    Optional region crops to (x, y, width, height) for detail inspection.

    ## Return Format
    {"success": true, "image_base64": "...", "mime_type": "image/png"}

    ## Examples
    get_state_snapshot(max_size=512)
    get_state_snapshot(region={"x": 140, "y": 80, "width": 240, "height": 300})
    """
    cfg = config or (interaction_manager.config if interaction_manager else GimpConfig())
    bridge = get_bridge_wrapper(cfg)
    alive = await bridge_available(bridge, cfg)
    if not alive:
        return {
            "success": False,
            "error": "GIMP Live Bridge required for snapshot",
            "hint": "Start MCP Bridge in GIMP: Filters > Development > MCP > Start MCP Bridge",
        }
    code = _snapshot_python(max_size=max_size, region=region)
    result = await execute_bridge_python(code, bridge=bridge, config=cfg, timeout=cfg.process_timeout)
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    stdout = result.get("result", {}).get("stdout", "")
    for line in stdout.split("\n"):
        line = line.strip()
        if line.startswith("SNAPSHOT:"):
            return {"success": True, "image_base64": line[9:], "mime_type": "image/png", "max_size": max_size, "region": region}
        if line.startswith("ERROR:"):
            return {"success": False, "error": line[6:]}
    return {"success": False, "error": "Bridge did not return a snapshot"}


async def gimp_render(
    operation: RenderOperation,
    *,
    output_path: str | None = None,
    include_base64: bool = False,
    width: int | None = None,
    height: int | None = None,
    interaction_manager: GimpInteractionManager | None = None,
    config: GimpConfig | None = None,
) -> dict[str, Any]:
    """Agent vision capture from GIMP (live bridge first).

    Operations:
        bridge_status - quick connectivity check
        capture_active - export active image to PNG (output_path required)
        get_image_summary - open document dimensions/count
    """
    cfg = config or (interaction_manager.config if interaction_manager else GimpConfig())
    bridge = get_bridge_wrapper(cfg)

    if operation == "bridge_status":
        alive = await bridge_available(bridge, cfg)
        return {
            "success": True,
            "bridge_connected": alive,
            "bridge_port": cfg.bridge_port,
            "mode": "hands_in" if alive else "hands_off",
        }

    if operation == "get_image_summary":
        return await gimp_bridge(
            "list_open_images",
            interaction_manager=interaction_manager,
            config=cfg,
        )

    if operation != "capture_active":
        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "available_operations": ["bridge_status", "capture_active", "get_image_summary"],
        }

    if not output_path:
        return {"success": False, "error": "output_path required for capture_active"}

    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return {"success": False, "error": f"Cannot create output directory: {exc}"}

    alive = await bridge_available(bridge, cfg)
    if not alive:
        return {
            "success": False,
            "error": "GIMP Live Bridge required for capture_active",
            "hint": "Start MCP Bridge in GIMP or export via gimp_file on disk paths",
        }

    code = _capture_active_python(str(path))
    result = await execute_bridge_python(code, bridge=bridge, config=cfg, timeout=cfg.process_timeout)
    if result.get("error"):
        return {"success": False, "error": result["error"], "mode": "live"}

    if not path.is_file():
        return {
            "success": False,
            "error": "Bridge reported success but capture file was not written",
            "output_path": str(path),
        }

    payload: dict[str, Any] = {
        "success": True,
        "mode": "live",
        "operation": operation,
        "output_path": str(path),
        "width": width,
        "height": height,
    }

    if include_base64:
        try:
            payload["image_base64"] = base64.b64encode(path.read_bytes()).decode("ascii")
            payload["mime_type"] = "image/png"
        except OSError as exc:
            logger.warning("Failed to read capture for base64: %s", exc)
            payload["base64_error"] = str(exc)

    return payload
