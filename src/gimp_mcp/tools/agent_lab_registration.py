"""Register Agent Lab tools on any FastMCP app (CLI + webapp http_app)."""

from __future__ import annotations

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..config import GimpConfig
from ..interaction_manager import GimpInteractionManager
from .bridge_tools import gimp_bridge, gimp_render
from .validation import gimp_validation


def register_agent_lab_tools(
    app: FastMCP,
    interaction_manager: GimpInteractionManager | None,
    config: GimpConfig,
) -> None:
    """Register gimp_bridge_tool, gimp_render_tool, gimp_validation_tool, gimp_live_status."""

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
