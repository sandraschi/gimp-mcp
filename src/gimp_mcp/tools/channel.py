"""
GIMP Channel Management Portmanteau Tool.

Comprehensive channel operations for GIMP MCP including
create, delete, list, color, opacity, and duplication.
"""

from __future__ import annotations

import json
import time
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChannelResult(BaseModel):
    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


def _make_channel_fu(operation: str, image_id: int, **kw: Any) -> str:
    """Generate Python-Fu code for a channel operation.

    Handles both GIMP 3 (gi.repository.Gimp) and GIMP 2.x (gimpfu).
    """
    if operation == "create":
        name = kw.get("channel_name", "New Channel")
        width = kw.get("width", 0)
        height = kw.get("height", 0)
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
_name = {json.dumps(name)}
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _img = Gimp.Image.get_by_id(_img_id)
        if _img is None:
            raise ValueError("Image not found")
        _channel = Gimp.Channel.new(_img, _name, {width or 0}, {height or 0})
        _img.insert_channel(_channel, None, -1)
        _result = {{"channel_id": _channel.get_id(), "name": _name}}
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _ch = pdb.gimp_channel_new(_img_id, _name, {width or 0}, {height or 0})
        pdb.gimp_image_insert_channel(_img_id, _ch, None, -1)
        _result = {{"channel_id": _ch, "name": _name}}
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": _result}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "delete":
        channel_id = kw.get("channel_id")
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
_ch_id = {channel_id}
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-image-remove-channel")
        _config = _proc.create_config()
        _args = _proc.get_arguments()
        _config.set_property(_args[0].get_name(), _img_id)
        _config.set_property(_args[1].get_name(), _ch_id)
        _proc.run(_config)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_image_remove_channel(_img_id, _ch_id)
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": {{"channel_id": _ch_id}}}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "list":
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
try:
    try:
        from gi.repository import Gimp
        _img = Gimp.Image.get_by_id(_img_id)
        _channels = _img.get_channels()
        _result = []
        for _ch in _channels:
            _result.append({{
                "id": _ch.get_id(),
                "name": _ch.get_name(),
                "opacity": _ch.get_opacity(),
                "visible": _ch.get_visible(),
                "color": str(_ch.get_color()),
            }})
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _ch_list = pdb.gimp_image_get_channels(_img_id)
        _result = []
        if _ch_list:
            for _ch_id in _ch_list:
                _result.append({{
                    "id": _ch_id,
                    "name": pdb.gimp_channel_get_name(_ch_id) if hasattr(pdb, "gimp_channel_get_name") else str(_ch_id),
                    "opacity": float(pdb.gimp_channel_get_opacity(_ch_id)),
                    "visible": bool(pdb.gimp_item_get_visible(_ch_id)),
                }})
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": _result}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "set_color":
        channel_id = kw.get("channel_id")
        color_str = kw.get("color", "red")
        return f'''
import json as _json, traceback as _tb
_ch_id = {channel_id}
try:
    try:
        from gi.repository import Gimp, GObject
        _ch = Gimp.Channel.get_by_id(_ch_id)
        if _ch is None:
            raise ValueError("Channel not found")
        _color = Gimp.RGB()
        _color.parse({json.dumps(color_str)})
        _ch.set_color(_color)
    except (ImportError, AttributeError):
        from gimpfu import pdb, gimpcolor
        _col = gimpcolor.RGB()
        _col.parse({json.dumps(color_str)})
        pdb.gimp_channel_set_color(_ch_id, _col)
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": {{"channel_id": _ch_id, "color": {json.dumps(color_str)}}}}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "set_opacity":
        channel_id = kw.get("channel_id")
        opacity = kw.get("opacity", 100.0)
        return f'''
import json as _json, traceback as _tb
_ch_id = {channel_id}
_opacity = float({opacity})
try:
    try:
        from gi.repository import Gimp
        _ch = Gimp.Channel.get_by_id(_ch_id)
        if _ch is None:
            raise ValueError("Channel not found")
        _ch.set_opacity(_opacity / 100.0)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_channel_set_opacity(_ch_id, _opacity / 100.0)
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": {{"channel_id": _ch_id, "opacity": _opacity}}}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "set_show_masked":
        channel_id = kw.get("channel_id")
        show_masked = kw.get("show_masked", False)
        return f'''
import json as _json, traceback as _tb
_ch_id = {channel_id}
_show = {json.dumps(show_masked)}
try:
    try:
        from gi.repository import Gimp
        _ch = Gimp.Channel.get_by_id(_ch_id)
        if _ch is None:
            raise ValueError("Channel not found")
        _ch.set_show_masked(_show)
    except (ImportError, AttributeError):
        from gimpfu import pdb
        pdb.gimp_channel_set_show_masked(_ch_id, int(_show))
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": {{"channel_id": _ch_id, "show_masked": _show}}}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "duplicate":
        channel_id = kw.get("channel_id")
        return f'''
import json as _json, traceback as _tb
_img_id = {image_id}
_ch_id = {channel_id}
try:
    try:
        from gi.repository import Gimp
        _pdb = Gimp.get_pdb()
        _proc = _pdb.lookup_procedure("gimp-channel-new")
        _img = Gimp.Image.get_by_id(_img_id)
        _src = Gimp.Channel.get_by_id(_ch_id)
        if _src is None:
            raise ValueError("Source channel not found")
        _dup = _src.duplicate()
        _img.insert_channel(_dup, None, -1)
        _result = {{"channel_id": _dup.get_id(), "name": _dup.get_name()}}
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _dup = pdb.gimp_channel_duplicate(_ch_id)
        pdb.gimp_image_insert_channel(_img_id, _dup, None, -1)
        _result = {{"channel_id": _dup, "name": str(_dup)}}
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": _result}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    if operation == "info":
        channel_id = kw.get("channel_id")
        return f'''
import json as _json, traceback as _tb
_ch_id = {channel_id}
try:
    try:
        from gi.repository import Gimp
        _ch = Gimp.Channel.get_by_id(_ch_id)
        if _ch is None:
            raise ValueError("Channel not found")
        _result = {{
            "id": _ch.get_id(),
            "name": _ch.get_name(),
            "width": _ch.get_width(),
            "height": _ch.get_height(),
            "opacity": float(_ch.get_opacity()),
            "visible": bool(_ch.get_visible()),
            "linked": bool(_ch.get_linked()),
            "color": str(_ch.get_color()),
            "show_masked": bool(_ch.get_show_masked()),
        }}
    except (ImportError, AttributeError):
        from gimpfu import pdb
        _result = {{
            "id": _ch_id,
            "name": pdb.gimp_channel_get_name(_ch_id) if hasattr(pdb, "gimp_channel_get_name") else str(_ch_id),
            "opacity": float(pdb.gimp_channel_get_opacity(_ch_id)),
            "visible": bool(pdb.gimp_item_get_visible(_ch_id)),
            "show_masked": bool(pdb.gimp_channel_get_show_masked(_ch_id)),
        }}
    print('CH_RESULT:' + _json.dumps({{"success": True, "result": _result}}))
except Exception as _e:
    print('CH_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
'''

    return None


async def gimp_channel(
    operation: Literal[
        "create",
        "delete",
        "list",
        "set_color",
        "set_opacity",
        "set_show_masked",
        "duplicate",
        "info",
    ],
    image_id: int,
    channel_id: int | None = None,
    channel_name: str = "New Channel",
    width: int = 0,
    height: int = 0,
    color: str = "red",
    opacity: float = 100.0,
    show_masked: bool = False,
    *,
    interaction_manager=None,
    cli_wrapper=None,
    config=None,
) -> dict[str, Any]:
    """Comprehensive channel management portmanteau for GIMP MCP.

    [RATIONALE] All channel operations are consolidated into one portmanteau
    to prevent tool explosion while keeping create, delete, list, color, opacity,
    and duplication operations discoverable under a single namespace.

    SUPPORTED OPERATIONS:
    - create: Create a new channel in the image
    - delete: Delete a channel by ID
    - list: List all channels for an image
    - set_color: Set channel color (CSS color name or hex)
    - set_opacity: Set channel opacity (0-100)
    - set_show_masked: Toggle masked area visibility
    - duplicate: Duplicate an existing channel
    - info: Get channel properties

    ## Return Format
    {"success": bool, "message": str, "data": {...}, "operation": str, "execution_time_ms": float}

    ## Examples
    gimp_channel("list", image_id=42)
    gimp_channel("create", image_id=42, channel_name="My Mask")
    gimp_channel("set_color", image_id=42, channel_id=7, color="blue")
    gimp_channel("set_opacity", image_id=42, channel_id=7, opacity=50.0)
    gimp_channel("duplicate", image_id=42, channel_id=7)

    Errors:
    - GIMP execution layer unavailable: No GIMP found
    - image_id required for all operations
    - channel_id required for operations that modify a channel
    - Channel not found for the given ID
    """
    start_time = time.time()

    try:
        exec_layer = interaction_manager or cli_wrapper
        if exec_layer is None:
            return ChannelResult(
                success=False,
                operation=operation,
                message="No GIMP execution layer available",
                error="GIMP not available",
            ).model_dump()

        requires_channel = operation in ("delete", "set_color", "set_opacity", "set_show_masked", "duplicate", "info")
        if requires_channel and channel_id is None:
            return ChannelResult(
                success=False,
                operation=operation,
                message=f"{operation} requires channel_id",
                error="Missing required parameter: channel_id",
            ).model_dump()

        code = _make_channel_fu(
            operation, image_id,
            channel_id=channel_id,
            channel_name=channel_name,
            width=width,
            height=height,
            color=color,
            opacity=opacity,
            show_masked=show_masked,
        )
        if code is None:
            return ChannelResult(
                success=False,
                operation=operation,
                message=f"Unknown operation: {operation}",
                error="Invalid operation",
            ).model_dump()

        output = await exec_layer.execute_python_fu(code)
        mode = getattr(exec_layer, "last_mode", "headless") if hasattr(exec_layer, "last_mode") else "headless"

        marker = "CH_RESULT:"
        idx = output.find(marker)
        if idx >= 0:
            payload = json.loads(output[idx + len(marker):])
            execution_time = (time.time() - start_time) * 1000
            return ChannelResult(
                success=payload.get("success", False),
                operation=operation,
                message=f"Channel {operation} completed" if payload.get("success") else f"Channel {operation} failed",
                data=payload.get("result", payload.get("data", {})),
                execution_time_ms=round(execution_time, 2),
                error=payload.get("error"),
            ).model_dump()

        execution_time = (time.time() - start_time) * 1000
        return ChannelResult(
            success=True,
            operation=operation,
            message=f"Channel {operation} completed",
            data={"mode": mode, "output": output},
            execution_time_ms=round(execution_time, 2),
        ).model_dump()

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return ChannelResult(
            success=False,
            operation=operation,
            message=f"Channel operation failed: {e!s}",
            error=str(e),
            execution_time_ms=round(execution_time, 2),
        ).model_dump()
