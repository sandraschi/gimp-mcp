"""
GIMP Color Management Portmanteau Tool.

ICC color profile management for GIMP MCP, covering profile
assignment, conversion, soft proofing, and system profile discovery.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class ColorMgmtResult(BaseModel):
    """Result model for color management operations."""

    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


def _make_profile_info_fu() -> str:
    """Generate Python-Fu code to get image ICC profile info."""
    return """
import json as _json
import traceback as _tb
try:
    try:
        _pdb
    except NameError:
        try:
            from gi.repository import Gimp
            _images = Gimp.get_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({"success": False, "error": "No image open in GIMP"}))
            else:
                _image = _images[0]
                _profile = _image.get_color_profile()
                if _profile is None:
                    print('PDB_RESULT:' + _json.dumps({"success": True, "profile": None, "message": "No color profile assigned"}))
                else:
                    _label = _profile.get_label() or "unknown"
                    _description = _profile.get_description() or "unknown"
                    _icc_size = _profile.get_icc_size() or 0
                    print('PDB_RESULT:' + _json.dumps({
                        "success": True,
                        "profile": {
                            "label": _label,
                            "description": _description,
                            "icc_size_bytes": _icc_size,
                        }
                    }))
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _images = pdb.gimp_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({"success": False, "error": "No image open in GIMP"}))
            else:
                _image = _images[0]
                _profile = pdb.gimp_image_get_color_profile(_image)
                if _profile is None:
                    print('PDB_RESULT:' + _json.dumps({"success": True, "profile": None}))
                else:
                    print('PDB_RESULT:' + _json.dumps({"success": True, "profile": {"id": _profile, "repr": str(_profile)}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({"success": False, "error": _tb.format_exc()}))
"""


def _make_assign_profile_fu(profile_path: str) -> str:
    """Generate Python-Fu code to assign a color profile."""
    return f"""
import json as _json
import traceback as _tb
try:
    try:
        _pdb
    except NameError:
        try:
            from gi.repository import Gimp, Gio
            _images = Gimp.get_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _file = Gio.File.new_for_path({json.dumps(profile_path)})
                _bytes = _file.load_contents()[1]
                _profile = Gimp.ColorProfile.new_from_icc_data(_bytes)
                _images[0].set_color_profile(_profile)
                print('PDB_RESULT:' + _json.dumps({{"success": True, "result": "Profile assigned"}}))
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _images = pdb.gimp_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _image = _images[0]
                with open({json.dumps(profile_path)}, 'rb') as _f:
                    _profile_data = _f.read()
                pdb.gimp_image_set_color_profile(_image, _profile_data)
                print('PDB_RESULT:' + _json.dumps({{"success": True, "result": "Profile assigned"}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
"""


def _make_convert_profile_fu(profile_path: str) -> str:
    """Generate Python-Fu code to convert image to a different color profile."""
    return f"""
import json as _json
import traceback as _tb
try:
    try:
        _pdb
    except NameError:
        try:
            from gi.repository import Gimp, Gio
            _images = Gimp.get_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _file = Gio.File.new_for_path({json.dumps(profile_path)})
                _bytes = _file.load_contents()[1]
                _profile = Gimp.ColorProfile.new_from_icc_data(_bytes)
                _images[0].convert_color_profile(_profile)
                print('PDB_RESULT:' + _json.dumps({{"success": True, "result": "Profile converted"}}))
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _images = pdb.gimp_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _image = _images[0]
                with open({json.dumps(profile_path)}, 'rb') as _f:
                    _profile_data = _f.read()
                pdb.gimp_image_convert_color_profile(_image, _profile_data)
                print('PDB_RESULT:' + _json.dumps({{"success": True, "result": "Profile converted"}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
"""


def _make_soft_proofing_fu(enabled: bool | None = None) -> str:
    """Generate Python-Fu code to get/set soft proofing state."""
    set_part = ""
    if enabled is not None:
        val = "True" if enabled else "False"
        set_part = f"""
    _images[0].set_proof_state({val})
"""
    return f"""
import json as _json
import traceback as _tb
try:
    try:
        _pdb
    except NameError:
        try:
            from gi.repository import Gimp
            _images = Gimp.get_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _state = _images[0].get_proof_state(){set_part}
                print('PDB_RESULT:' + _json.dumps({{"success": True, "soft_proofing_enabled": bool(_state)}}))
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _images = pdb.gimp_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _image = _images[0]{'''
                pdb.gimp_image_set_proof_state(_image, 1)
                ''' if enabled else '''
                pdb.gimp_image_set_proof_state(_image, 0)
                ''' if enabled is not None else ''}
                _state = pdb.gimp_image_get_proof_state(_image)
                print('PDB_RESULT:' + _json.dumps({{"success": True, "soft_proofing_enabled": bool(_state)}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
"""


def _make_simulation_profile_fu(profile_path: str | None = None) -> str:
    """Generate Python-Fu code to get/set simulation profile."""
    set_part = ""
    if profile_path:
        set_part = f"""
            _file = Gio.File.new_for_path({json.dumps(profile_path)})
            _bytes = _file.load_contents()[1]
            _profile = Gimp.ColorProfile.new_from_icc_data(_bytes)
            _images[0].set_simulation_profile(_profile)
"""
    return f"""
import json as _json
import traceback as _tb
try:
    try:
        _pdb
    except NameError:
        try:
            from gi.repository import Gimp, Gio
            _images = Gimp.get_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:{set_part}
                _sim_profile = _images[0].get_simulation_profile()
                if _sim_profile:
                    _label = _sim_profile.get_label() or "unknown"
                    print('PDB_RESULT:' + _json.dumps({{"success": True, "simulation_profile": {{"label": _label}}}}))
                else:
                    print('PDB_RESULT:' + _json.dumps({{"success": True, "simulation_profile": None}}))
        except (ImportError, AttributeError, TypeError):
            from gimpfu import pdb
            _images = pdb.gimp_image_list()
            if not _images:
                print('PDB_RESULT:' + _json.dumps({{"success": False, "error": "No image open in GIMP"}}))
            else:
                _image = _images[0]{'''
                with open(''' + json.dumps(profile_path) + ''', 'rb') as _f:
                    pdb.gimp_image_set_simulation_profile(_image, _f.read())
                ''' if profile_path else ''}
                _sim = pdb.gimp_image_get_simulation_profile(_image)
                print('PDB_RESULT:' + _json.dumps({{"success": True, "simulation_profile": str(_sim) if _sim else None}}))
except Exception as _e:
    print('PDB_RESULT:' + _json.dumps({{"success": False, "error": _tb.format_exc()}}))
"""


SYSTEM_PROFILE_DIRS = {
    "win32": ["C:\\Windows\\System32\\spool\\drivers\\color\\"],
    "darwin": ["/Library/ColorSync/Profiles/", "/System/Library/ColorSync/Profiles/"],
    "linux": [
        "/usr/share/color/icc/",
        "/usr/local/share/color/icc/",
        "~/.local/share/color/icc/",
    ],
}


def _list_system_profiles() -> dict[str, Any]:
    """Scan system directories for ICC profiles."""
    import platform as _platform

    system = _platform.system().lower()
    dirs = SYSTEM_PROFILE_DIRS.get(system if system in SYSTEM_PROFILE_DIRS else "linux", SYSTEM_PROFILE_DIRS["linux"])

    profiles: list[dict[str, Any]] = []
    errors: list[str] = []

    for d in dirs:
        d_path = Path(d).expanduser()
        if d_path.is_dir():
            try:
                for f in sorted(d_path.glob("*.icc")) + sorted(d_path.glob("*.icm")):
                    profiles.append({
                        "path": str(f),
                        "filename": f.name,
                        "size_bytes": f.stat().st_size,
                    })
            except PermissionError:
                errors.append(f"Permission denied: {d}")

    return ColorMgmtResult(
        success=True,
        operation="list_profiles",
        message=f"Found {len(profiles)} ICC profiles",
        data={"profiles": profiles, "total": len(profiles), "directories_scanned": dirs, "errors": errors},
    ).model_dump()


async def gimp_color_management(
    operation: Literal[
        "profile_info",
        "assign_profile",
        "convert_profile",
        "get_effective_profile",
        "soft_proofing",
        "simulation_profile",
        "list_profiles",
    ],
    profile_path: str | None = None,
    soft_proofing_enabled: bool | None = None,
    cli_wrapper: Any = None,
    config: Any = None,
) -> dict[str, Any]:
    """ICC color management portmanteau for GIMP MCP.

    [RATIONALE] Color management operations (profile info, assignment, conversion,
    soft proofing) are consolidated into one tool to prevent tool explosion while
    keeping all ICC profile workflows under a single namespace.

    ## Return Format
    {"success": bool, "message": str, "data": {...}, "operation": str}

    ## Examples
    gimp_color_management(operation="profile_info")
    gimp_color_management(operation="assign_profile", profile_path="/path/to/sRGB.icc")
    gimp_color_management(operation="convert_profile", profile_path="/path/to/AdobeRGB.icc")
    gimp_color_management(operation="soft_proofing", soft_proofing_enabled=True)
    gimp_color_management(operation="list_profiles")
    """
    start_time = time.time()

    try:
        if operation == "list_profiles":
            result = _list_system_profiles()
        elif operation == "profile_info":
            result = await _exec_color_fu(_make_profile_info_fu(), "profile_info", cli_wrapper)
        elif operation == "assign_profile":
            if not profile_path:
                result = ColorMgmtResult(
                    success=False, operation=operation, message="profile_path is required", error="Missing parameter"
                ).model_dump()
            else:
                result = await _exec_color_fu(_make_assign_profile_fu(profile_path), "assign_profile", cli_wrapper)
                if result.get("success"):
                    result["message"] = f"Profile assigned: {profile_path}"
        elif operation == "convert_profile":
            if not profile_path:
                result = ColorMgmtResult(
                    success=False, operation=operation, message="profile_path is required", error="Missing parameter"
                ).model_dump()
            else:
                result = await _exec_color_fu(_make_convert_profile_fu(profile_path), "convert_profile", cli_wrapper)
                if result.get("success"):
                    result["message"] = f"Profile converted: {profile_path}"
        elif operation == "get_effective_profile":
            result = await _exec_color_fu(_make_profile_info_fu(), "get_effective_profile", cli_wrapper)
        elif operation == "soft_proofing":
            result = await _exec_color_fu(_make_soft_proofing_fu(soft_proofing_enabled), "soft_proofing", cli_wrapper)
        elif operation == "simulation_profile":
            result = await _exec_color_fu(_make_simulation_profile_fu(profile_path), "simulation_profile", cli_wrapper)
        else:
            result = ColorMgmtResult(
                success=False,
                operation=operation,
                message=f"Unknown operation: {operation}",
                error="Invalid operation",
            ).model_dump()

        execution_time = (time.time() - start_time) * 1000
        result["execution_time_ms"] = round(execution_time, 2)
        return result

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return ColorMgmtResult(
            success=False,
            operation=operation,
            message=f"Color management operation failed: {e!s}",
            error=str(e),
            execution_time_ms=round(execution_time, 2),
        ).model_dump()


async def _exec_color_fu(code: str, operation: str, cli_wrapper: Any) -> dict[str, Any]:
    """Execute Python-Fu code and parse the PDB_RESULT response."""
    exec_layer = cli_wrapper
    if exec_layer is None:
        return ColorMgmtResult(
            success=False, operation=operation, message="No GIMP execution layer available", error="GIMP offline"
        ).model_dump()

    try:
        if hasattr(exec_layer, "execute_python_fu"):
            output = await exec_layer.execute_python_fu(code)
        else:
            return ColorMgmtResult(
                success=False, operation=operation, message="No execute_python_fu method", error="Missing method"
            ).model_dump()
    except Exception as e:
        return ColorMgmtResult(
            success=False, operation=operation, message=f"GIMP execution failed: {e!s}", error=str(e)
        ).model_dump()

    try:
        marker = "PDB_RESULT:"
        idx = output.find(marker)
        if idx >= 0:
            payload = json.loads(output[idx + len(marker) :])
            if payload.get("success"):
                data = {k: v for k, v in payload.items() if k != "success"}
                return ColorMgmtResult(
                    success=True, operation=operation, message=f"{operation} completed", data=data
                ).model_dump()
            return ColorMgmtResult(
                success=False,
                operation=operation,
                message=f"Operation failed: {payload.get('error', 'unknown error')}",
                error=payload.get("error"),
            ).model_dump()
        return ColorMgmtResult(
            success=True, operation=operation, message=f"{operation} completed", data={"raw_output": output}
        ).model_dump()
    except Exception as e:
        return ColorMgmtResult(
            success=False,
            operation=operation,
            message=f"Failed to parse response: {e!s}",
            error=str(e),
            data={"raw": output},
        ).model_dump()
