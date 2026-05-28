"""Fleet sim-art pipeline: icons -> validate -> atlas -> robotics/avatar staging."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..tools.sim_art_tools import gimp_sim_art
from .sim_art_templates import DEFAULT_SIM_STAGING

logger = logging.getLogger(__name__)


@dataclass
class SimPipelineStep:
    name: str
    success: bool
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimPipelineReport:
    success: bool
    steps: list[SimPipelineStep] = field(default_factory=list)
    staging_dir: str | None = None
    output_dir: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "staging_dir": self.staging_dir,
            "output_dir": self.output_dir,
            "steps": [{"name": s.name, "success": s.success, "detail": s.detail} for s in self.steps],
        }


async def run_sim_art_pipeline(
    *,
    input_dir: str,
    staging_dir: Path | None = None,
    pipeline: str = "gazebo",
    template_id: str = "gazebo_icon_256",
    layout: str = "4x4",
    cell_size: int = 256,
    skip_atlas: bool = False,
    skip_robotics: bool = False,
    skip_avatar: bool = True,
    validate: bool = True,
    robotics_url: str | None = None,
    avatar_url: str | None = None,
) -> SimPipelineReport:
    """Run sim-art batch pipeline for Gazebo icons or VRChat social icons."""
    report = SimPipelineReport(success=False)
    stage = staging_dir or Path(DEFAULT_SIM_STAGING)
    report.staging_dir = str(stage)
    src = Path(input_dir)
    if not src.is_dir():
        report.steps.append(
            SimPipelineStep("precheck", False, {"error": f"Input directory not found: {input_dir}"}),
        )
        return report

    if pipeline == "vrchat":
        batch = await gimp_sim_art(
            "vrchat_icon_batch",
            input_dir=str(src),
            output_dir=str(stage / "vrchat_icons"),
            template_id=template_id if template_id.startswith("vrchat") else "vrchat_profile_256",
            validate=validate,
            staging_dir=str(stage),
        )
        report.output_dir = str(stage / "vrchat_icons")
        report.steps.append(SimPipelineStep("vrchat_icon_batch", bool(batch.get("success")), batch))
        if not batch.get("success"):
            return report
        if not skip_avatar:
            handoff = await gimp_sim_art(
                "push_avatar_handoff",
                input_dir=str(stage / "vrchat_icons"),
                staging_dir=str(stage),
                avatar_url=avatar_url,
            )
            report.steps.append(SimPipelineStep("avatar_handoff", bool(handoff.get("success")), handoff))
    else:
        batch = await gimp_sim_art(
            "gazebo_model_icons",
            input_dir=str(src),
            output_dir=str(stage / "gazebo_icons"),
            template_id=template_id,
            validate=validate,
            target_platform="gazebo",
            staging_dir=str(stage),
        )
        report.output_dir = str(stage / "gazebo_icons")
        report.steps.append(SimPipelineStep("gazebo_model_icons", bool(batch.get("success")), batch))
        if not batch.get("success"):
            return report

        if not skip_atlas:
            atlas = await gimp_sim_art(
                "build_atlas",
                input_dir=str(stage / "gazebo_icons"),
                output_path=str(stage / "atlases" / f"atlas_{layout}.png"),
                layout=layout,
                cell_size=cell_size,
                staging_dir=str(stage),
            )
            report.steps.append(SimPipelineStep("build_atlas", bool(atlas.get("success")), atlas))

        if not skip_robotics:
            robotics = await gimp_sim_art(
                "stage_for_robotics",
                input_dir=str(stage / "gazebo_icons"),
                staging_dir=str(stage),
                robotics_url=robotics_url,
            )
            report.steps.append(SimPipelineStep("robotics_staging", bool(robotics.get("success")), robotics))

    report.success = all(step.success for step in report.steps)
    return report
