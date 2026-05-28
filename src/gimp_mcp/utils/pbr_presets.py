"""PBR texture map presets and pack detection for fleet pipelines."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, TypedDict


class PbrMapSpec(TypedDict):
    slot: str
    label: str
    suffixes: tuple[str, ...]
    require_alpha: bool


PBR_MAP_SLOTS: tuple[PbrMapSpec, ...] = (
    {
        "slot": "albedo",
        "label": "Albedo / Base Color",
        "suffixes": ("albedo", "basecolor", "base_color", "diffuse", "color"),
        "require_alpha": False,
    },
    {
        "slot": "normal",
        "label": "Normal Map",
        "suffixes": ("normal", "norm", "nrm"),
        "require_alpha": False,
    },
    {
        "slot": "roughness",
        "label": "Roughness",
        "suffixes": ("roughness", "rough", "rgh"),
        "require_alpha": False,
    },
    {
        "slot": "metallic",
        "label": "Metallic",
        "suffixes": ("metallic", "metal", "mtl"),
        "require_alpha": False,
    },
    {
        "slot": "ao",
        "label": "Ambient Occlusion",
        "suffixes": ("ao", "ambient_occlusion", "occlusion"),
        "require_alpha": False,
    },
)

PBR_TARGET_SIZES: tuple[int, ...] = (512, 1024, 2048, 4096)

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tga", ".tif", ".tiff"}


def _stem_tokens(stem: str) -> list[str]:
    return [part.lower() for part in re.split(r"[_\-.]+", stem) if part]


def match_pbr_slot(stem: str) -> str | None:
    """Return PBR slot id if filename stem matches a known map suffix."""
    tokens = _stem_tokens(stem)
    if not tokens:
        return None
    for spec in PBR_MAP_SLOTS:
        for suffix in spec["suffixes"]:
            if suffix in tokens or tokens[-1] == suffix:
                return spec["slot"]
    return None


def detect_pbr_maps(input_dir: Path) -> dict[str, Path]:
    """Detect PBR maps in a directory by filename suffix tokens."""
    found: dict[str, Path] = {}
    if not input_dir.is_dir():
        return found
    for path in sorted(input_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in _IMAGE_SUFFIXES:
            continue
        slot = match_pbr_slot(path.stem)
        if slot and slot not in found:
            found[slot] = path
    return found


def list_pbr_presets() -> dict[str, Any]:
    """Catalog for agents and validation."""
    return {
        "map_slots": [
            {"slot": spec["slot"], "label": spec["label"], "suffixes": list(spec["suffixes"])}
            for spec in PBR_MAP_SLOTS
        ],
        "required_slots": ["albedo", "normal", "roughness"],
        "optional_slots": ["metallic", "ao"],
        "target_sizes": list(PBR_TARGET_SIZES),
        "naming_hint": "Use stem tokens like material_albedo.png, material_normal.png",
    }


def validate_pbr_pack_layout(
    maps: dict[str, Path],
    *,
    required_slots: tuple[str, ...] = ("albedo", "normal", "roughness"),
) -> list[str]:
    """Return validation issues for a detected PBR map set."""
    issues: list[str] = []
    missing = [slot for slot in required_slots if slot not in maps]
    if missing:
        issues.append(f"Missing required PBR slot(s): {', '.join(missing)}")

    sizes: set[tuple[int, int]] = set()
    try:
        from PIL import Image

        for slot, path in maps.items():
            with Image.open(path) as img:
                sizes.add((img.width, img.height))
                if img.width != img.height:
                    issues.append(f"{slot} map {path.name} is not square ({img.width}x{img.height})")
                if img.width & (img.width - 1):
                    issues.append(f"{slot} map {path.name} width {img.width} is not power-of-two")
                if img.height & (img.height - 1):
                    issues.append(f"{slot} map {path.name} height {img.height} is not power-of-two")
    except ImportError as exc:
        issues.append(f"Pillow required for PBR validation: {exc}")
    except Exception as exc:
        issues.append(f"Failed to read PBR maps: {exc}")

    if len(sizes) > 1:
        issues.append(f"PBR maps have mismatched dimensions: {sorted(sizes)}")
    return issues
