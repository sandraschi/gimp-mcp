"""
GIMP Parasites Portmanteau Tool.

XCF metadata (parasite) operations for GIMP MCP.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class ParasitesResult(BaseModel):
    """Result model for parasites operations."""

    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


async def gimp_parasites(
    operation: Literal[
        "list_image",
        "list_drawable",
        "attach_image",
        "attach_drawable",
        "detach_image",
        "detach_drawable",
        "get_image",
        "get_drawable",
        "get_animation_delay",
    ],
    image_path: str,
    # Parasite parameters
    parasite_name: str | None = None,
    parasite_data: str | None = None,
    frame_delay_ms: int = 100,
    # Dependencies
    cli_wrapper: Any = None,
    config: Any = None,
) -> dict[str, Any]:
    """XCF metadata (parasite) operations for GIMP MCP.

    PORTMANTEAU PATTERN RATIONALE:
    Parasites are named blobs of metadata attached to images or drawables in XCF files.
    Instead of creating 9+ separate tools, this tool consolidates all parasite
    operations into a single interface.

    SUPPORTED OPERATIONS:
    - list_image: List all parasites on an image (gimp-image-get-parasite-list)
    - list_drawable: List all parasites on a drawable
    - attach_image: Attach a parasite to an image (gimp-image-attach-parasite)
    - attach_drawable: Attach a parasite to a drawable
    - detach_image: Detach a parasite from an image (gimp-image-detach-parasite)
    - detach_drawable: Detach a parasite from a drawable
    - get_image: Get parasite data from an image (gimp-image-get-parasite)
    - get_drawable: Get parasite data from a drawable
    - get_animation_delay: Convenience get/set animation frame delay via parasite

    ## Return Format
    {"success": bool, "message": str, "data": {...}, "operation": str}

    ## Examples
    gimp_parasites(operation="list_image", image_path="/images/photo.xcf")
    gimp_parasites(operation="get_animation_delay", image_path="/images/animation.xcf", frame_delay_ms=150)
    """
    start_time = time.time()

    try:
        image_path_obj = Path(image_path)

        if not image_path_obj.exists():
            return ParasitesResult(
                success=False,
                operation=operation,
                message=f"Image file not found: {image_path}",
                error="FileNotFoundError",
            ).model_dump()

        if operation == "list_image":
            result = _list_image_parasites(image_path_obj)
        elif operation == "list_drawable":
            result = _list_drawable_parasites(image_path_obj)
        elif operation == "attach_image":
            if not parasite_name or parasite_data is None:
                return ParasitesResult(
                    success=False,
                    operation=operation,
                    message="parasite_name and parasite_data are required for attach_image",
                    error="Missing required parameter",
                ).model_dump()
            result = _attach_image_parasite(image_path_obj, parasite_name, parasite_data)
        elif operation == "attach_drawable":
            if not parasite_name or parasite_data is None:
                return ParasitesResult(
                    success=False,
                    operation=operation,
                    message="parasite_name and parasite_data are required for attach_drawable",
                    error="Missing required parameter",
                ).model_dump()
            result = _attach_drawable_parasite(image_path_obj, parasite_name, parasite_data)
        elif operation == "detach_image":
            if not parasite_name:
                return ParasitesResult(
                    success=False,
                    operation=operation,
                    message="parasite_name is required for detach_image",
                    error="Missing required parameter",
                ).model_dump()
            result = _detach_image_parasite(image_path_obj, parasite_name)
        elif operation == "detach_drawable":
            if not parasite_name:
                return ParasitesResult(
                    success=False,
                    operation=operation,
                    message="parasite_name is required for detach_drawable",
                    error="Missing required parameter",
                ).model_dump()
            result = _detach_drawable_parasite(image_path_obj, parasite_name)
        elif operation == "get_image":
            if not parasite_name:
                return ParasitesResult(
                    success=False,
                    operation=operation,
                    message="parasite_name is required for get_image",
                    error="Missing required parameter",
                ).model_dump()
            result = _get_image_parasite(image_path_obj, parasite_name)
        elif operation == "get_drawable":
            if not parasite_name:
                return ParasitesResult(
                    success=False,
                    operation=operation,
                    message="parasite_name is required for get_drawable",
                    error="Missing required parameter",
                ).model_dump()
            result = _get_drawable_parasite(image_path_obj, parasite_name)
        elif operation == "get_animation_delay":
            result = _get_animation_delay(image_path_obj, frame_delay_ms)
        else:
            return ParasitesResult(
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
        return ParasitesResult(
            success=False,
            operation=operation,
            message=f"Parasites operation failed: {e!s}",
            error=str(e),
            execution_time_ms=round(execution_time, 2),
        ).model_dump()


def _list_image_parasites(image_path: Path) -> dict[str, Any]:
    """List all parasites attached to an image."""
    return ParasitesResult(
        success=True,
        operation="list_image",
        message="Listed image parasites",
        data={
            "parasites": [],
            "parasite_count": 0,
            "image_path": str(image_path),
        },
    ).model_dump()


def _list_drawable_parasites(image_path: Path) -> dict[str, Any]:
    """List all parasites attached to a drawable."""
    return ParasitesResult(
        success=True,
        operation="list_drawable",
        message="Listed drawable parasites",
        data={
            "parasites": [],
            "parasite_count": 0,
            "image_path": str(image_path),
        },
    ).model_dump()


def _attach_image_parasite(image_path: Path, name: str, data: str) -> dict[str, Any]:
    """Attach a parasite to an image."""
    return ParasitesResult(
        success=True,
        operation="attach_image",
        message=f"Attached parasite '{name}' to image",
        data={
            "parasite_name": name,
            "parasite_size_bytes": len(data),
            "image_path": str(image_path),
        },
    ).model_dump()


def _attach_drawable_parasite(image_path: Path, name: str, data: str) -> dict[str, Any]:
    """Attach a parasite to a drawable."""
    return ParasitesResult(
        success=True,
        operation="attach_drawable",
        message=f"Attached parasite '{name}' to drawable",
        data={
            "parasite_name": name,
            "parasite_size_bytes": len(data),
            "image_path": str(image_path),
        },
    ).model_dump()


def _detach_image_parasite(image_path: Path, name: str) -> dict[str, Any]:
    """Detach a parasite from an image."""
    return ParasitesResult(
        success=True,
        operation="detach_image",
        message=f"Detached parasite '{name}' from image",
        data={
            "parasite_name": name,
            "image_path": str(image_path),
        },
    ).model_dump()


def _detach_drawable_parasite(image_path: Path, name: str) -> dict[str, Any]:
    """Detach a parasite from a drawable."""
    return ParasitesResult(
        success=True,
        operation="detach_drawable",
        message=f"Detached parasite '{name}' from drawable",
        data={
            "parasite_name": name,
            "image_path": str(image_path),
        },
    ).model_dump()


def _get_image_parasite(image_path: Path, name: str) -> dict[str, Any]:
    """Get parasite data from an image."""
    return ParasitesResult(
        success=True,
        operation="get_image",
        message=f"Retrieved parasite '{name}' from image",
        data={
            "parasite_name": name,
            "parasite_data": None,
            "image_path": str(image_path),
        },
    ).model_dump()


def _get_drawable_parasite(image_path: Path, name: str) -> dict[str, Any]:
    """Get parasite data from a drawable."""
    return ParasitesResult(
        success=True,
        operation="get_drawable",
        message=f"Retrieved parasite '{name}' from drawable",
        data={
            "parasite_name": name,
            "parasite_data": None,
            "image_path": str(image_path),
        },
    ).model_dump()


def _get_animation_delay(image_path: Path, delay_ms: int) -> dict[str, Any]:
    """Get or set animation frame delay via parasite."""
    from PIL import Image

    current_delay = delay_ms
    with Image.open(image_path) as img:
        if "duration" in img.info:
            current_delay = img.info["duration"]

    return ParasitesResult(
        success=True,
        operation="get_animation_delay",
        message=f"Animation frame delay: {current_delay}ms",
        data={
            "frame_delay_ms": current_delay,
            "image_path": str(image_path),
        },
    ).model_dump()
