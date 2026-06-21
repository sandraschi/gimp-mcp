"""Fleet sim-art template presets (Gazebo, VRChat, texture atlases)."""

from __future__ import annotations

from typing import Any, TypedDict


class SimArtTemplate(TypedDict):
    id: str
    label: str
    width: int
    height: int
    format: str
    require_alpha: bool
    target: str


SIM_ART_TEMPLATES: dict[str, SimArtTemplate] = {
    "gazebo_icon_256": {
        "id": "gazebo_icon_256",
        "label": "Gazebo model thumbnail (256)",
        "width": 256,
        "height": 256,
        "format": "png",
        "require_alpha": True,
        "target": "gazebo",
    },
    "gazebo_icon_512": {
        "id": "gazebo_icon_512",
        "label": "Gazebo model thumbnail (512)",
        "width": 512,
        "height": 512,
        "format": "png",
        "require_alpha": True,
        "target": "gazebo",
    },
    "gazebo_decal_512": {
        "id": "gazebo_decal_512",
        "label": "Gazebo sim decal (512 POT)",
        "width": 512,
        "height": 512,
        "format": "png",
        "require_alpha": True,
        "target": "gazebo",
    },
    "vrchat_profile_256": {
        "id": "vrchat_profile_256",
        "label": "VRChat profile icon",
        "width": 256,
        "height": 256,
        "format": "png",
        "require_alpha": True,
        "target": "vrchat",
    },
    "vrchat_world_512": {
        "id": "vrchat_world_512",
        "label": "VRChat world thumbnail",
        "width": 512,
        "height": 512,
        "format": "png",
        "require_alpha": False,
        "target": "vrchat",
    },
    "sim_atlas_cell_256": {
        "id": "sim_atlas_cell_256",
        "label": "Sim texture atlas cell",
        "width": 256,
        "height": 256,
        "format": "png",
        "require_alpha": True,
        "target": "unity",
    },
}

ATLAS_LAYOUTS: dict[str, tuple[int, int]] = {
    "2x2": (2, 2),
    "3x3": (3, 3),
    "4x4": (4, 4),
    "4x2": (4, 2),
    "8x8": (8, 8),
}

DEFAULT_SIM_STAGING = "D:/Temp/fleet_pipeline/sim_art"


def list_template_catalog() -> list[dict[str, Any]]:
    return [
        {**template, "layout": None}
        for template in SIM_ART_TEMPLATES.values()
    ]


def list_atlas_layouts() -> list[dict[str, Any]]:
    return [{"id": key, "columns": cols, "rows": rows, "cells": cols * rows} for key, (cols, rows) in ATLAS_LAYOUTS.items()]


def resolve_template(template_id: str) -> SimArtTemplate | None:
    return SIM_ART_TEMPLATES.get(template_id)
