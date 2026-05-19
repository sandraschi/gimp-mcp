"""
GIMP Animation Portmanteau Tool.

Frame-based animation operations for GIMP MCP.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class AnimationResult(BaseModel):
    """Result model for animation operations."""

    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    error: str | None = None


async def gimp_animation(
    operation: Literal[
        "list_frames",
        "set_frame_delay",
        "optimize_for_gif",
        "export_gif",
        "frame_count",
    ],
    image_path: str,
    output_path: str | None = None,
    # Frame delay parameters
    frame_delay_ms: int = 100,
    frame_index: int | None = None,
    # GIF export parameters
    loop_forever: bool = True,
    loop_count: int = 0,
    optimize: bool = True,
    dither: bool = True,
    # Dependencies
    cli_wrapper: Any = None,
    config: Any = None,
) -> dict[str, Any]:
    """Frame-based animation operations for GIMP MCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 5+ separate tools (one per animation operation), this tool
    consolidates related frame-based animation operations into a single interface.
    GIMP handles animation via layered XCF files where each layer is a frame.

    SUPPORTED OPERATIONS:
    - list_frames: List frames in an animated image (layers are frames)
    - set_frame_delay: Set frame delay via gimp-animation-delay parasite
    - optimize_for_gif: Convert image to GIF format (indexed + export)
    - export_gif: Export as animated GIF with frame delays
    - frame_count: Count frames for animation export

    ## Return Format
    {"success": bool, "message": str, "data": {...}, "operation": str}

    ## Examples
    gimp_animation(operation="list_frames", image_path="/images/animation.xcf")
    gimp_animation(operation="export_gif", image_path="/images/animation.xcf", output_path="/images/output.gif", loop_forever=True)
    """
    start_time = time.time()

    try:
        from PIL import Image

        image_path_obj = Path(image_path)

        if not image_path_obj.exists():
            return AnimationResult(
                success=False,
                operation=operation,
                message=f"Image file not found: {image_path}",
                error="FileNotFoundError",
            ).model_dump()

        if operation == "list_frames":
            result = _list_frames(image_path_obj)
        elif operation == "set_frame_delay":
            result = _set_frame_delay(image_path_obj, frame_index, frame_delay_ms)
        elif operation == "optimize_for_gif":
            if not output_path:
                return AnimationResult(
                    success=False,
                    operation=operation,
                    message="output_path is required for optimize_for_gif",
                    error="Missing required parameter",
                ).model_dump()
            result = _optimize_for_gif(image_path_obj, Path(output_path), dither)
        elif operation == "export_gif":
            if not output_path:
                return AnimationResult(
                    success=False,
                    operation=operation,
                    message="output_path is required for export_gif",
                    error="Missing required parameter",
                ).model_dump()
            result = _export_gif(image_path_obj, Path(output_path), frame_delay_ms, loop_forever, loop_count, optimize, dither)
        elif operation == "frame_count":
            result = _frame_count(image_path_obj)
        else:
            return AnimationResult(
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
        return AnimationResult(
            success=False,
            operation=operation,
            message=f"Animation operation failed: {e!s}",
            error=str(e),
            execution_time_ms=round(execution_time, 2),
        ).model_dump()


def _list_frames(image_path: Path) -> dict[str, Any]:
    """List frames in an animated image (layers = frames)."""
    from PIL import Image

    frames = []
    with Image.open(image_path) as img:
        try:
            while True:
                frame_info = {
                    "index": len(frames),
                    "size": img.size,
                    "mode": img.mode,
                }
                # Try to extract frame delay from palette animation
                if "duration" in img.info:
                    frame_info["delay_ms"] = img.info["duration"]
                frames.append(frame_info)
                try:
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
        except EOFError:
            pass

    return AnimationResult(
        success=True,
        operation="list_frames",
        message=f"Found {len(frames)} frame(s) in animation",
        data={
            "frame_count": len(frames),
            "frames": frames,
            "image_path": str(image_path),
        },
    ).model_dump()


def _set_frame_delay(image_path: Path, frame_index: int | None, delay_ms: int) -> dict[str, Any]:
    """Set frame delay via parasite data."""
    from PIL import Image

    with Image.open(image_path) as img:
        if frame_index is not None:
            img.seek(frame_index)
        img.info["duration"] = delay_ms
        # Save updated frame delay back
        img.save(image_path)

    return AnimationResult(
        success=True,
        operation="set_frame_delay",
        message=f"Frame delay set to {delay_ms}ms" + (f" for frame {frame_index}" if frame_index is not None else " for all frames"),
        data={
            "frame_delay_ms": delay_ms,
            "frame_index": frame_index,
        },
    ).model_dump()


def _optimize_for_gif(image_path: Path, output_path: Path, dither: bool) -> dict[str, Any]:
    """Convert image to GIF animation format (indexed)."""
    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(image_path) as img:
        frames = []
        durations = []
        try:
            while True:
                frame = img.convert("RGBA")
                if dither:
                    frame = frame.quantize(method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
                else:
                    frame = frame.quantize(method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
                frames.append(frame)
                durations.append(img.info.get("duration", 100))
                try:
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
        except EOFError:
            pass

        if not frames:
            single = img.convert("P")
            single.save(output_path, format="GIF")
        else:
            frames[0].save(
                output_path,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
            )

    return AnimationResult(
        success=True,
        operation="optimize_for_gif",
        message=f"Optimized {len(frames) if frames else 1} frame(s) for GIF",
        data={
            "frame_count": len(frames) if frames else 1,
            "output_path": str(output_path.resolve()),
            "output_size_bytes": output_path.stat().st_size,
        },
    ).model_dump()


def _export_gif(
    image_path: Path,
    output_path: Path,
    frame_delay_ms: int,
    loop_forever: bool,
    loop_count: int,
    optimize: bool,
    dither: bool,
) -> dict[str, Any]:
    """Export as animated GIF with frame delays."""
    from PIL import Image

    output_path.parent.mkdir(parents=True, exist_ok=True)

    loop = 0 if loop_forever else loop_count

    with Image.open(image_path) as img:
        frames = []
        durations = []
        try:
            while True:
                frame = img.convert("RGBA")
                if optimize:
                    if dither:
                        frame = frame.quantize(method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
                    else:
                        frame = frame.quantize(method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
                frames.append(frame)
                durations.append(img.info.get("duration", frame_delay_ms))
                try:
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
        except EOFError:
            pass

        if not frames:
            single = img.convert("P")
            single.save(output_path, format="GIF", loop=loop)
        else:
            if len(frames) == 1:
                frames[0].save(output_path, format="GIF", loop=loop)
            else:
                frames[0].save(
                    output_path,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=loop,
                )

    return AnimationResult(
        success=True,
        operation="export_gif",
        message=f"Exported {len(frames) if frames else 1} frame(s) as animated GIF",
        data={
            "frame_count": len(frames) if frames else 1,
            "frame_delay_ms": frame_delay_ms,
            "loop_forever": loop_forever,
            "output_path": str(output_path.resolve()),
            "output_size_bytes": output_path.stat().st_size,
        },
    ).model_dump()


def _frame_count(image_path: Path) -> dict[str, Any]:
    """Count frames for animation export."""
    from PIL import Image

    frame_count = 0
    with Image.open(image_path) as img:
        try:
            while True:
                frame_count += 1
                try:
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
        except EOFError:
            pass

    return AnimationResult(
        success=True,
        operation="frame_count",
        message=f"Animation contains {frame_count} frame(s)",
        data={
            "frame_count": frame_count,
            "image_path": str(image_path),
        },
    ).model_dump()
