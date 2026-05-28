"""Register Agent Lab tools on any FastMCP app (CLI + webapp http_app)."""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..config import GimpConfig
from ..interaction_manager import GimpInteractionManager
from .bridge_tools import gimp_bridge, gimp_render
from .import_tools import gimp_import
from .validation import gimp_validation
from .sim_art_tools import gimp_sim_art
from .vision_refine_tools import gimp_vision_refine


def register_agent_lab_tools(
    app: FastMCP,
    interaction_manager: GimpInteractionManager | None,
    config: GimpConfig,
) -> None:
    """Register Agent Lab tools on any FastMCP app (CLI + webapp http_app)."""

    @app.tool(annotations={"readOnlyHint": True}, version="4.2.0")
    async def gimp_bridge_tool(
        operation: Annotated[
            str,
            Field(description="Operation: status, execution_mode, ping, list_open_images."),
        ],
    ) -> dict[str, Any]:
        """Live GIMP bridge portmanteau (TCP plugin on :10824)."""
        return await gimp_bridge(
            operation=operation,  # type: ignore[arg-type]
            interaction_manager=interaction_manager,
            config=config,
        )

    @app.tool(annotations={"readOnlyHint": True}, version="4.2.0")
    async def gimp_render_tool(
        operation: Annotated[
            str,
            Field(description="Operation: bridge_status, capture_active, get_image_summary."),
        ],
        output_path: Annotated[str | None, Field(description="PNG path for capture_active.")] = None,
        include_base64: Annotated[bool, Field(description="Include base64 PNG for LLM vision.")] = False,
    ) -> dict[str, Any]:
        """Agent vision capture from the open GIMP canvas (live bridge)."""
        return await gimp_render(
            operation=operation,  # type: ignore[arg-type]
            output_path=output_path,
            include_base64=include_base64,
            interaction_manager=interaction_manager,
            config=config,
        )

    @app.tool(annotations={"readOnlyHint": True}, version="4.2.0")
    async def gimp_validation_tool(
        operation: Annotated[
            str,
            Field(
                description=(
                    "Operation: validate_image, check_resolution, check_alpha, check_icc, audit_texture."
                ),
            ),
        ],
        input_path: Annotated[str, Field(description="Image file path to validate.")],
        min_width: Annotated[int, Field(description="Minimum width in pixels.")] = 1,
        min_height: Annotated[int, Field(description="Minimum height in pixels.")] = 1,
        max_width: Annotated[int, Field(description="Maximum width in pixels.")] = 8192,
        max_height: Annotated[int, Field(description="Maximum height in pixels.")] = 8192,
        require_power_of_two: Annotated[bool, Field(description="Require power-of-two dimensions.")] = False,
        require_alpha: Annotated[bool, Field(description="Require alpha channel.")] = False,
        require_icc: Annotated[bool, Field(description="Require embedded ICC profile.")] = False,
        target_platform: Annotated[str, Field(description="Target platform for audit_texture.")] = "unity",
    ) -> dict[str, Any]:
        """Image QA validation for agents and fleet texture pipelines."""
        return await gimp_validation(
            operation=operation,  # type: ignore[arg-type]
            input_path=input_path,
            min_width=min_width,
            min_height=min_height,
            max_width=max_width,
            max_height=max_height,
            require_power_of_two=require_power_of_two,
            require_alpha=require_alpha,
            require_icc=require_icc,
            target_platform=target_platform,
        )

    @app.tool(annotations={"readOnlyHint": True}, version="4.3.0")
    async def gimp_import_tool(
        operation: Annotated[
            str,
            Field(description="Operation: import_file, from_blender_render, list_staging, push_unity."),
        ],
        source_path: Annotated[str | None, Field(description="Source image path.")] = None,
        staging_dir: Annotated[str | None, Field(description="Fleet staging directory.")] = None,
        blender_url: Annotated[str | None, Field(description="blender-mcp HTTP base URL.")] = None,
        blender_operation: Annotated[str, Field(description="blender_render operation.")] = "render_multi_angle",
        angles: Annotated[int, Field(description="Angles for render_multi_angle.")] = 4,
        output_path: Annotated[str | None, Field(description="Output path for screenshot_viewport.")] = None,
        project_path: Annotated[str | None, Field(description="Unity project path for push_unity.")] = None,
        texture_type: Annotated[str, Field(description="Unity texture type.")] = "diffuse",
        unity_url: Annotated[str | None, Field(description="unity3d-mcp HTTP base URL.")] = None,
        normalize_size: Annotated[int, Field(description="Power-of-two normalize size.")] = 1024,
    ) -> dict[str, Any]:
        """Fleet handoff: Blender renders -> GIMP staging -> Unity texture push."""
        return await gimp_import(
            operation=operation,  # type: ignore[arg-type]
            source_path=source_path,
            staging_dir=staging_dir,
            blender_url=blender_url,
            blender_operation=blender_operation,
            angles=angles,
            output_path=output_path,
            project_path=project_path,
            texture_type=texture_type,
            unity_url=unity_url,
            normalize_size=normalize_size,
        )

    @app.tool(annotations={"readOnlyHint": True}, version="4.3.0")
    async def gimp_vision_refine_tool(
        operation: Annotated[
            str,
            Field(description="Operation: review_bundle, texture_review, validate_folder."),
        ],
        input_dir: Annotated[str | None, Field(description="Folder of textures to review.")] = None,
        input_path: Annotated[str | None, Field(description="Single texture path.")] = None,
        goal: Annotated[str, Field(description="Agent review goal.")] = "",
        target_platform: Annotated[str, Field(description="Target platform audit.")] = "unity",
    ) -> dict[str, Any]:
        """Texture review bundle for agent vision loops."""
        return await gimp_vision_refine(
            operation=operation,  # type: ignore[arg-type]
            input_dir=input_dir,
            input_path=input_path,
            goal=goal,
            target_platform=target_platform,
        )

    @app.tool(annotations={"readOnlyHint": True}, version="4.5.0")
    async def gimp_sim_art_tool(
        operation: Annotated[
            str,
            Field(
                description=(
                    "Operation: list_templates, gazebo_model_icons, build_atlas, "
                    "vrchat_icon_batch, stage_for_robotics, push_avatar_handoff."
                ),
            ),
        ],
        input_dir: Annotated[str | None, Field(description="Folder of source images.")] = None,
        output_dir: Annotated[str | None, Field(description="Output folder for batch icons.")] = None,
        output_path: Annotated[str | None, Field(description="Atlas PNG output path.")] = None,
        template_id: Annotated[str, Field(description="Sim-art template id.")] = "gazebo_icon_256",
        layout: Annotated[str, Field(description="Atlas layout (2x2, 4x4, etc.).")] = "4x4",
        cell_size: Annotated[int, Field(description="Atlas cell size in pixels.")] = 256,
        validate: Annotated[bool, Field(description="Run audit_texture on outputs.")] = True,
        target_platform: Annotated[str, Field(description="Validation target platform.")] = "gazebo",
        staging_dir: Annotated[str | None, Field(description="Sim-art staging root.")] = None,
        robotics_url: Annotated[str | None, Field(description="robotics-mcp HTTP base URL.")] = None,
        avatar_url: Annotated[str | None, Field(description="avatar-mcp HTTP base URL.")] = None,
    ) -> dict[str, Any]:
        """Robotics and sim-art batch: Gazebo icons, texture atlases, VRChat handoff."""
        return await gimp_sim_art(
            operation=operation,  # type: ignore[arg-type]
            input_dir=input_dir,
            output_dir=output_dir,
            output_path=output_path,
            template_id=template_id,
            layout=layout,
            cell_size=cell_size,
            validate=validate,
            target_platform=target_platform,
            staging_dir=staging_dir,
            robotics_url=robotics_url,
            avatar_url=avatar_url,
        )

    @app.tool(annotations={"readOnlyHint": True}, version="4.2.0")
    async def gimp_live_status() -> dict[str, Any]:
        """Legacy bridge status (prefer gimp_bridge_tool operation=status)."""
        result = await gimp_bridge(
            operation="status",
            interaction_manager=interaction_manager,
            config=config,
        )
        if not result.get("success"):
            return result
        return {
            "success": True,
            "mode": result.get("mode", "headless"),
            "message": result.get("message", "GIMP bridge status"),
            "data": {
                "status": result.get("status"),
                "bridge_port": result.get("bridge_port"),
                "bridge_host": result.get("bridge_host"),
            },
        }
