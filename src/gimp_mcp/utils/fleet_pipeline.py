"""Fleet E2E pipeline: blender-mcp renders -> gimp process/validate -> unity3d-mcp textures."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .fleet_handoff import push_texture_to_unity
from .fleet_http import DEFAULT_BLENDER_URL, DEFAULT_UNITY_URL, check_http_health
from .fleet_import import DEFAULT_STAGING_DIR, import_file_to_staging, import_from_blender_render
from ..tools.import_tools import normalize_texture_png
from ..tools.validation import gimp_validation
from ..tools.vision_refine_tools import build_texture_review_bundle

logger = logging.getLogger(__name__)


@dataclass
class PipelineStep:
    name: str
    success: bool
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineReport:
    success: bool
    steps: list[PipelineStep] = field(default_factory=list)
    texture_path: str | None = None
    project_path: str | None = None
    staging_dir: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "texture_path": self.texture_path,
            "project_path": self.project_path,
            "staging_dir": self.staging_dir,
            "steps": [{"name": s.name, "success": s.success, "detail": s.detail} for s in self.steps],
        }


async def run_fleet_pipeline(
    *,
    project_path: str,
    texture_path: str | None = None,
    blender_url: str = DEFAULT_BLENDER_URL,
    unity_url: str = DEFAULT_UNITY_URL,
    staging_dir: Path | None = None,
    skip_blender: bool = False,
    blender_operation: str = "screenshot_viewport",
    blender_angles: int = 4,
    skip_validate: bool = False,
    skip_review: bool = False,
    skip_unity: bool = False,
    texture_type: str = "diffuse",
    target_platform: str = "unity",
    normalize_size: int = 1024,
    goal: str = "",
) -> PipelineReport:
    """Run blender render (optional) -> gimp normalize/validate -> unity texture push."""
    report = PipelineReport(success=False, project_path=project_path)
    stage = staging_dir or DEFAULT_STAGING_DIR
    report.staging_dir = str(stage)

    project = Path(project_path)
    if not project.is_dir():
        report.steps.append(PipelineStep("precheck", False, {"error": f"Unity project not found: {project_path}"}))
        return report

    resolved_texture: Path | None = Path(texture_path) if texture_path else None

    if not skip_blender and resolved_texture is None:
        if not await check_http_health(blender_url, health_path="/api/v1/health"):
            if not await check_http_health(blender_url, health_path="/health"):
                report.steps.append(
                    PipelineStep(
                        "blender_render",
                        False,
                        {"error": f"blender-mcp not reachable at {blender_url}", "hint": "Pass --texture-path to skip"},
                    )
                )
                return report

        render_result = await import_from_blender_render(
            blender_url=blender_url,
            output_dir=stage / "blender_renders",
            operation=blender_operation,
            angles=blender_angles,
            output_path=str(stage / "blender_renders" / "viewport.png")
            if blender_operation == "screenshot_viewport"
            else None,
        )
        report.steps.append(PipelineStep("blender_render", bool(render_result.get("success")), render_result))
        if not render_result.get("success"):
            return report
        files = render_result.get("files") or []
        if not files:
            return report
        resolved_texture = Path(str(files[0]))

    if resolved_texture is None or not resolved_texture.is_file():
        report.steps.append(
            PipelineStep(
                "precheck",
                False,
                {"error": "No texture: provide --texture-path or enable blender render"},
            )
        )
        return report

    report.texture_path = str(resolved_texture)

    stage_result = await import_file_to_staging(
        source_path=str(resolved_texture),
        staging_dir=stage,
        subdir="incoming",
    )
    report.steps.append(PipelineStep("gimp_staging", bool(stage_result.get("success")), stage_result))

    processed_dir = stage / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed = processed_dir / f"{resolved_texture.stem}_pot.png"
    norm_result = await normalize_texture_png(str(resolved_texture), str(processed), size=normalize_size)
    report.steps.append(PipelineStep("gimp_normalize", bool(norm_result.get("success")), norm_result))
    if not norm_result.get("success"):
        return report
    report.texture_path = str(processed)

    if not skip_validate:
        val_result = await gimp_validation(
            "audit_texture",
            str(processed),
            target_platform=target_platform,
        )
        passed = bool(val_result.get("data", {}).get("passed", not val_result.get("issues")))
        report.steps.append(PipelineStep("gimp_validate", passed, val_result))
        if not passed:
            return report

    if not skip_review:
        review = await build_texture_review_bundle(
            input_dir=str(processed_dir),
            goal=goal,
            target_platform=target_platform,
        )
        report.steps.append(
            PipelineStep(
                "gimp_vision_review",
                bool(review.get("success")),
                {k: review[k] for k in review if k != "entries"} if review.get("success") else review,
            )
        )

    if skip_unity:
        report.success = all(s.success for s in report.steps)
        return report

    if not await check_http_health(unity_url, health_path="/api/v1/health"):
        report.steps.append(
            PipelineStep(
                "unity_push",
                False,
                {"error": f"unity3d-mcp not reachable at {unity_url}"},
            )
        )
        return report

    push_result = await push_texture_to_unity(
        texture_path=str(processed),
        project_path=project_path,
        texture_type=texture_type,
        unity_url=unity_url,
    )
    report.steps.append(PipelineStep("unity_texture_push", bool(push_result.get("success")), push_result))

    report.success = all(s.success for s in report.steps)
    return report
