"""Image QA validation portmanteau for Agent Lab and fleet texture pipelines."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

ValidationOperation = Literal[
    "validate_image",
    "check_resolution",
    "check_alpha",
    "check_icc",
    "audit_texture",
]


class ValidationResult(BaseModel):
    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    error: str | None = None


def _is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


def _load_image_info(path: Path) -> dict[str, Any]:
    from PIL import Image

    with Image.open(path) as img:
        icc = img.info.get("icc_profile")
        return {
            "path": str(path),
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "has_alpha": img.mode in ("RGBA", "LA", "PA"),
            "has_icc": bool(icc),
            "icc_bytes": len(icc) if icc else 0,
        }


async def gimp_validation(
    operation: ValidationOperation,
    input_path: str,
    *,
    min_width: int = 1,
    min_height: int = 1,
    max_width: int = 8192,
    max_height: int = 8192,
    require_power_of_two: bool = False,
    require_alpha: bool = False,
    require_icc: bool = False,
    target_platform: str = "unity",
) -> dict[str, Any]:
    """Image QA validation for agents and fleet texture handoff.

    Operations:
        validate_image - run resolution, alpha, and ICC checks
        check_resolution - min/max dimensions, optional power-of-two
        check_alpha - verify alpha channel presence
        check_icc - verify embedded ICC profile
        audit_texture - platform-oriented texture readiness (Unity default)
    """
    start = time.time()
    path = Path(input_path)

    if not path.is_file():
        return ValidationResult(
            success=False,
            operation=operation,
            message=f"Input file not found: {input_path}",
            error="FileNotFoundError",
        ).model_dump()

    try:
        info = _load_image_info(path)
    except Exception as exc:
        logger.error("Validation failed to open image: %s", exc, exc_info=True)
        return ValidationResult(
            success=False,
            operation=operation,
            message=f"Cannot read image: {exc}",
            error=str(exc),
        ).model_dump()

    issues: list[str] = []

    if operation in ("validate_image", "check_resolution", "audit_texture"):
        if info["width"] < min_width or info["height"] < min_height:
            issues.append(
                f"Resolution {info['width']}x{info['height']} below minimum {min_width}x{min_height}"
            )
        if info["width"] > max_width or info["height"] > max_height:
            issues.append(
                f"Resolution {info['width']}x{info['height']} exceeds maximum {max_width}x{max_height}"
            )
        pot_required = require_power_of_two or operation == "audit_texture"
        if pot_required:
            if not _is_power_of_two(info["width"]) or not _is_power_of_two(info["height"]):
                issues.append(
                    f"Dimensions {info['width']}x{info['height']} are not power-of-two"
                )

    if operation in ("validate_image", "check_alpha", "audit_texture"):
        alpha_required = require_alpha or (
            operation == "audit_texture" and target_platform in ("vrchat",)
        )
        if alpha_required and not info["has_alpha"]:
            issues.append("Image has no alpha channel (expected RGBA/LA)")

    if operation in ("validate_image", "check_icc", "audit_texture"):
        icc_required = require_icc or (operation == "audit_texture" and target_platform == "print")
        if icc_required and not info["has_icc"]:
            issues.append("No embedded ICC profile")

    if operation == "audit_texture":
        max_dim = max(info["width"], info["height"])
        if target_platform == "unity" and max_dim > 4096:
            issues.append(f"Max dimension {max_dim} exceeds Unity-friendly 4096 limit")
        if info["format"] not in ("PNG", "TGA", "JPEG", "WEBP", None):
            issues.append(f"Format {info['format']} may need conversion for {target_platform}")

    elapsed = (time.time() - start) * 1000
    passed = len(issues) == 0

    return ValidationResult(
        success=True,
        operation=operation,
        message="Validation passed" if passed else f"Validation found {len(issues)} issue(s)",
        data={
            **info,
            "passed": passed,
            "target_platform": target_platform,
            "checks_run": operation,
        },
        issues=issues,
        execution_time_ms=round(elapsed, 2),
    ).model_dump()
