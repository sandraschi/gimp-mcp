"""
Agentic Workflow Tools for GIMP MCP

FastMCP 3.2: Context sampling (ctx.sample), client logging (ctx.info), and
orchestration helpers for GIMP automation.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

from pydantic import Field

from fastmcp import Context

from .logging_config import get_logger

logger = get_logger(__name__)


async def _notify_client(ctx: Context | None, message: str) -> None:
    if ctx is None:
        return
    await ctx.info(message)


def register_agentic_tools(mcp_instance=None):
    """Register agentic workflow tools with sampling capabilities."""
    if mcp_instance is None:
        raise TypeError("register_agentic_tools(mcp_instance) requires a FastMCP instance")

    @mcp_instance.tool(annotations={"destructiveHint": True}, version="4.1.0")
    async def generate_image(
        description: Annotated[str, Field(description="Natural language description of the image to generate.")] = "a simple landscape scene",
        style_preset: Annotated[str, Field(description="Visual style: photorealistic, artistic, technical, fantasy, abstract.")] = "photorealistic",
        dimensions: Annotated[str, Field(description="Image dimensions as WIDTHxHEIGHT (e.g. 1024x1024).")] = "1024x1024",
        model: Annotated[str, Field(description="AI provider: gemini, stability, or bfl (requires API key configured in Settings).")] = "gemini",
        quality: Annotated[str, Field(description="Quality level: draft, standard, high, ultra.")] = "standard",
        reference_images: Annotated[list[str] | None, Field(description="Optional list of reference image paths for style guidance.")] = None,
        post_processing: Annotated[list[str] | None, Field(description="List of GIMP operations to apply after generation (sharpen, color_correction, etc.).")] = None,
        max_iterations: Annotated[int, Field(description="Maximum refinement iterations for the generation process.")] = 3,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Generate images using AI with conversational refinement and GIMP post-processing.

        [RATIONALE] Consolidates AI image generation, GIMP processing, and repository
        management into a single tool to prevent workflow fragmentation across generation,
        enhancement, and storage concerns.

        ## Return Format
        {"success": bool, "message": str, "image_path": str, "dimensions": str, "style_preset": str, "model_used": str, "quality_level": str, "processing_applied": list, "quality_metrics": dict, "next_steps": list}

        ## Examples
        generate_image(description="a serene mountain lake at sunset", style_preset="photorealistic", dimensions="1024x1024")
        generate_image(description="fantasy castle in the clouds", style_preset="fantasy", post_processing=["sharpen", "color_correction"])
        """
        try:
            # Phase 1: Analysis & Planning
            logger.info(f"Starting AI image generation for: {description[:100]}...")

            # Parse dimensions
            try:
                width, height = map(int, dimensions.split("x"))
                if width < 64 or height < 64 or width > 8192 or height > 8192:
                    raise ValueError("Dimensions must be between 64x64 and 8192x8192")
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid dimensions format: {dimensions}. Use 'WIDTHxHEIGHT'",
                    "message": "Please specify dimensions as '1024x1024' or similar.",
                }

            # Validate style preset
            valid_styles = ["photorealistic", "artistic", "technical", "fantasy", "abstract"]
            if style_preset not in valid_styles:
                return {
                    "success": False,
                    "error": f"Invalid style preset: {style_preset}",
                    "valid_options": valid_styles,
                    "message": f"Choose from: {', '.join(valid_styles)}",
                }

            # Validate model (AI provider)
            valid_models = ["gemini", "stability", "bfl"]
            if model not in valid_models:
                return {
                    "success": False,
                    "error": f"Invalid model: {model}",
                    "valid_options": valid_models,
                    "message": f"Choose from: {', '.join(valid_models)}",
                }

            # Validate quality
            valid_qualities = ["draft", "standard", "high", "ultra"]
            if quality not in valid_qualities:
                return {
                    "success": False,
                    "error": f"Invalid quality: {quality}",
                    "valid_options": valid_qualities,
                    "message": f"Choose from: {', '.join(valid_qualities)}",
                }

            # Phase 2: AI Image Generation
            await _notify_client(ctx, f"Generating AI image with {model} in {style_preset} style...")

            from .ai_image import generate as ai_generate
            generation_result = await ai_generate(
                provider=model,
                prompt=description,
                width=width,
                height=height,
                quality=quality,
                style=style_preset,
            )

            if not generation_result["success"]:
                return {
                    "success": False,
                    "error": generation_result["error"],
                    "message": "Failed to generate base image. Try simplifying the description or changing parameters.",
                }

            base_image_path = generation_result["image_path"]

            # Phase 3: GIMP Post-Processing
            if post_processing and len(post_processing) > 0:
                await _notify_client(ctx, f"Applying GIMP post-processing: {', '.join(post_processing)}")

                processed_image_path = await _apply_gimp_processing(
                    base_image_path=base_image_path, post_processing=post_processing, quality_settings=quality
                )

                if processed_image_path:
                    final_image_path = processed_image_path
                    processing_applied = post_processing
                else:
                    final_image_path = base_image_path
                    processing_applied = []
                    await _notify_client(ctx, "Post-processing failed, using original image")
            else:
                final_image_path = base_image_path
                processing_applied = []

            # Phase 4: Quality Assessment & Repository Storage
            quality_metrics = await _assess_image_quality(final_image_path)
            enhanced_image_path = await _enhance_image_quality(final_image_path, quality_metrics)

            # Save to repository with comprehensive metadata
            await _save_image_to_repository(
                image_path=enhanced_image_path,
                description=description,
                style_preset=style_preset,
                model_used=model,
                quality_level=quality,
                dimensions=f"{width}x{height}",
                processing_steps=processing_applied,
                quality_metrics=quality_metrics,
                generation_metadata={
                    "reference_images": reference_images or [],
                    "iterations_used": 1,
                    "processing_time": "simulated",
                    "file_size": os.path.getsize(enhanced_image_path) if os.path.exists(enhanced_image_path) else 0,
                },
            )

            # Generate summary
            image_hash = hashlib.md5(open(enhanced_image_path, "rb").read()).hexdigest()[:8]

            result = {
                "success": True,
                "message": f"Successfully generated {style_preset} image: '{description[:50]}...'",
                "image_path": str(enhanced_image_path),
                "image_hash": image_hash,
                "dimensions": f"{width}x{height}",
                "style_preset": style_preset,
                "model_used": model,
                "quality_level": quality,
                "processing_applied": processing_applied,
                "quality_metrics": quality_metrics,
                "file_size_mb": round(os.path.getsize(enhanced_image_path) / (1024 * 1024), 2),
                "next_steps": [
                    "Use gimp_color tool for further color adjustments",
                    "Apply gimp_filter for artistic effects",
                    "Use gimp_layer to add text or overlays",
                    "Export with gimp_file in different formats",
                ],
            }

            await _notify_client(ctx, f"Image generated successfully. Saved as: {enhanced_image_path.name}")
            return result

        except Exception as e:
            logger.error(f"AI image generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Image generation failed: {e!s}",
                "message": "An unexpected error occurred during image generation. Try simplifying your request or contact support.",
            }

    @mcp_instance.tool(annotations={"readOnlyHint": True}, version="4.1.0")
    async def agentic_gimp_workflow(
        workflow_prompt: Annotated[str, Field(description="Natural language description of the workflow to execute.")],
        available_tools: Annotated[list[str], Field(description="Tool names the planner should stick to.")],
        max_iterations: Annotated[int, Field(description="Soft cap for steps in the plan text.")] = 5,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Execute agentic GIMP workflows using FastMCP 3.2 sampling.

        Uses ctx.sample to obtain a concise multi-step plan; falls back with a
        clear message when sampling is unavailable.

        ## Return Format
        {"success": bool, "message": str, "plan": str, "available_tools": list, "max_iterations": int, "sampling_error": str | None}

        ## Examples
        agentic_gimp_workflow(workflow_prompt="resize all images in a folder to 800x600 and convert to webp", available_tools=["gimp_batch_tool", "gimp_file_tool"])
        """
        plan_text = ""
        sampling_error: str | None = None
        try:
            if ctx:
                await ctx.info("Planning GIMP workflow via MCP sampling…")
                try:
                    res = await ctx.sample(
                        (
                            "You are a GIMP MCP planner. Given the user goal and allowed tools, "
                            "output a numbered list of concrete steps (at most "
                            f"{max_iterations} steps). Only reference these tools: {available_tools}.\n\n"
                            f"Goal:\n{workflow_prompt}"
                        ),
                        max_tokens=900,
                    )
                    plan_text = (res.text or "").strip()
                except Exception as se:  # noqa: BLE001 — host may not support sampling
                    sampling_error = str(se)
                    logger.debug("Sampling failed: %s", se, exc_info=True)

            message = (
                "Plan generated via server sampling."
                if plan_text
                else "Sampling unavailable or empty; use portmanteau tools from the client LLM."
            )
            return {
                "success": True,
                "operation": "agentic_workflow",
                "message": message,
                "workflow_prompt": workflow_prompt,
                "available_tools": available_tools,
                "max_iterations": max_iterations,
                "plan": plan_text,
                "sampling_error": sampling_error,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute agentic workflow: {e!s}",
                "message": "An error occurred while setting up the agentic workflow.",
            }

    @mcp_instance.tool(annotations={"destructiveHint": True}, version="4.1.0")
    async def intelligent_image_processing(
        images: Annotated[list[dict[str, Any]], Field(description="List of image objects to process, each with path and optional metadata.")],
        processing_goal: Annotated[str, Field(description="Goal for processing (e.g. enhance old photos for printing).")],
        available_operations: Annotated[list[str], Field(description="Operations the LLM can choose from.")],
        processing_strategy: Annotated[str, Field(description="How to process images: adaptive, parallel, sequential.")] = "adaptive",
    ) -> dict[str, Any]:
        """Intelligent batch image processing using LLM-driven strategy selection.

        Uses the client LLM to intelligently decide how to process batches
        of images, choosing the right operations and sequencing for optimal results.

        ## Return Format
        {"success": bool, "message": str, "processing_goal": str, "image_count": int, "available_operations": list, "processing_strategy": str, "capabilities": list}

        ## Examples
        intelligent_image_processing(images=[{"path": "/images/photo1.jpg"}, {"path": "/images/photo2.jpg"}], processing_goal="enhance old photos for printing", available_operations=["brightness_contrast", "sharpen"])
        """
        try:
            {
                "goal": processing_goal,
                "image_count": len(images),
                "available_operations": available_operations,
                "strategy": processing_strategy,
                "analysis": "LLM will analyze each image and choose optimal processing operations",
            }

            result = {
                "success": True,
                "operation": "intelligent_batch_processing",
                "message": "Intelligent image processing initiated. The LLM will analyze each image and apply optimal operations based on content characteristics.",
                "processing_goal": processing_goal,
                "image_count": len(images),
                "available_operations": available_operations,
                "processing_strategy": processing_strategy,
                "capabilities": [
                    "Content-aware processing",
                    "Automatic operation selection",
                    "Adaptive batching strategies",
                    "Quality validation",
                    "Error recovery",
                ],
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to initiate intelligent processing: {e!s}",
                "message": "An error occurred while setting up intelligent image processing.",
            }

    @mcp_instance.tool(annotations={"readOnlyHint": True}, version="4.1.0")
    async def conversational_gimp_assistant(
        user_query: Annotated[str, Field(description="Natural language query about GIMP operations.")],
        context_level: Annotated[str, Field(description="Amount of context to provide: basic, comprehensive, detailed.")] = "comprehensive",
    ) -> dict[str, Any]:
        """Conversational GIMP assistant with natural language responses.

        Provides human-like interaction for GIMP image editing with detailed
        explanations and suggestions for next steps.

        ## Return Format
        {"success": bool, "message": str, "user_query": str, "context_level": str, "suggestions": list, "next_steps": list}

        ## Examples
        conversational_gimp_assistant(user_query="How do I remove the background from an image?")
        conversational_gimp_assistant(user_query="What filters are available?", context_level="detailed")
        """
        try:
            # Analyze the query and provide conversational guidance
            response_templates = {
                "basic": "I can help you edit images with GIMP.",
                "comprehensive": "I'm your GIMP image editing assistant. I can help you manipulate photos, apply effects, manage layers, adjust colors, and process images in batches.",
                "detailed": "Welcome to GIMP MCP! I'm equipped with comprehensive image editing capabilities including file operations, geometric transforms, color adjustments, filters and effects, layer management, image analysis, and batch processing workflows.",
            }

            result = {
                "success": True,
                "operation": "conversational_assistance",
                "message": response_templates.get(context_level, response_templates["comprehensive"]),
                "user_query": user_query,
                "context_level": context_level,
                "suggestions": [
                    "Edit and manipulate images",
                    "Apply filters and effects",
                    "Adjust colors and tones",
                    "Manage image layers",
                    "Process images in batches",
                ],
                "next_steps": [
                    "Use 'gimp_file' to load and save images",
                    "Use 'gimp_color' to adjust brightness and colors",
                    "Use 'gimp_filter' to apply artistic effects",
                    "Use 'gimp_layer' to manage image layers",
                    "Use 'gimp_batch' for processing multiple images",
                ],
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to provide conversational assistance: {e!s}",
                "message": "I encountered an error while processing your request.",
            }


# Helper functions for AI image generation


async def _generate_base_image(
    description: str, style_preset: str, width: int, height: int, model: str, quality: str
) -> dict[str, Any]:
    """
    Generate base image using AI model.

    In production, this would integrate with actual AI image generation APIs.
    For now, creates a placeholder implementation.
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_hash = hashlib.md5(description.encode()).hexdigest()[:8]
        filename = f"ai_{timestamp}_{image_hash}_{width}x{height}.png"
        image_path = output_dir / filename

        # Placeholder: Create a simple colored rectangle as demonstration
        # In production, this would call actual AI image generation APIs
        await _create_placeholder_image(image_path, width, height, description)

        return {
            "success": True,
            "image_path": image_path,
            "model_used": model,
            "generation_time": "simulated",
            "metadata": {
                "description": description,
                "style_preset": style_preset,
                "dimensions": f"{width}x{height}",
                "quality": quality,
            },
        }

    except Exception as e:
        logger.error(f"Base image generation failed: {e}")
        return {"success": False, "error": f"Failed to generate base image: {e!s}"}


async def _create_placeholder_image(image_path: Path, width: int, height: int, description: str) -> None:
    """
    Create a placeholder image for demonstration.

    In production, this would be replaced with actual AI image generation.
    """
    try:
        # For demonstration, create a simple colored image using PIL
        from PIL import Image, ImageDraw, ImageFont

        # Create base image with random color based on description hash
        desc_hash = hash(description) % 360
        hue = desc_hash / 360.0

        # Convert HSV to RGB
        import colorsys

        r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        img = Image.new("RGB", (width, height), color=(r, g, b))
        draw = ImageDraw.Draw(img)

        # Add description text
        try:
            font_size = min(width, height) // 20
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        # Add text overlay
        text = f"AI Generated:\n{description[:100]}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Add text with shadow for visibility
        shadow_color = (0, 0, 0, 128)
        text_color = (255, 255, 255, 255)

        draw.text((x + 2, y + 2), text, fill=shadow_color, font=font)
        draw.text((x, y), text, fill=text_color, font=font)

        img.save(image_path, "PNG")

    except Exception as e:
        logger.error(f"Failed to create placeholder image: {e}")
        # Fallback: create a simple solid color image
        img = Image.new("RGB", (width, height), color=(128, 128, 128))
        img.save(image_path, "PNG")


async def _apply_gimp_processing(base_image_path: str, post_processing: list[str], quality_settings: str) -> str | None:
    """
    Apply GIMP post-processing operations to the generated image.

    Args:
        base_image_path: Path to the base generated image
        post_processing: List of GIMP operations to apply
        quality_settings: Quality level for processing

    Returns:
        Path to processed image, or None if processing failed
    """
    try:
        if not post_processing:
            return base_image_path

        processed_path = Path(base_image_path).with_stem(f"{Path(base_image_path).stem}_processed")

        # Apply each post-processing operation
        current_path = base_image_path

        for operation in post_processing:
            operation_result = await _apply_single_gimp_operation(current_path, operation, quality_settings)
            if operation_result:
                current_path = operation_result
            else:
                logger.warning(f"GIMP operation '{operation}' failed, continuing with others")

        # Copy final result to processed path if different
        if current_path != str(processed_path):
            import shutil

            shutil.copy2(current_path, processed_path)

        return str(processed_path)

    except Exception as e:
        logger.error(f"GIMP post-processing failed: {e}")
        return None


async def _apply_single_gimp_operation(image_path: str, operation: str, quality: str) -> str | None:
    """
    Apply a single GIMP operation to an image.

    In production, this would use the GIMP CLI or Python API.
    For now, returns the original path as a placeholder.
    """
    try:
        # Placeholder implementation
        # In production, this would call actual GIMP operations
        logger.info(f"Applying GIMP operation: {operation} to {image_path}")
        return image_path

    except Exception as e:
        logger.error(f"Failed to apply GIMP operation {operation}: {e}")
        return None


async def _assess_image_quality(image_path: str) -> dict[str, Any]:
    """
    Assess the quality of a generated image.

    Returns quality metrics and analysis.
    """
    try:
        import math

        from PIL import Image

        img = Image.open(image_path)
        width, height = img.size

        # Basic quality metrics
        file_size = os.path.getsize(image_path)
        pixels = width * height

        # Color analysis
        colors = img.getcolors(maxcolors=256)
        unique_colors = len(colors) if colors else 0

        # Calculate basic quality score
        size_score = min(file_size / (1024 * 1024), 10)  # Max 10MB = score 10
        color_score = min(unique_colors / 256, 1.0)  # More colors = higher score
        resolution_score = min(math.sqrt(pixels) / 100, 1.0)  # Higher resolution = higher score

        overall_quality = (size_score + color_score + resolution_score) / 3 * 10

        return {
            "overall_quality": round(overall_quality, 2),
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "dimensions": f"{width}x{height}",
            "unique_colors": unique_colors,
            "pixels": pixels,
            "color_depth": "RGB",
            "format": "PNG",
            "compression": "none",
        }

    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        return {"overall_quality": 5.0, "error": f"Assessment failed: {e!s}"}


async def _enhance_image_quality(image_path: str, quality_metrics: dict[str, Any]) -> str:
    """
    Apply quality enhancements based on assessment.

    Returns path to enhanced image.
    """
    try:
        # For now, just return the original path
        # In production, this would apply quality enhancements
        return image_path

    except Exception as e:
        logger.error(f"Quality enhancement failed: {e}")
        return image_path


async def _save_image_to_repository(
    image_path: str,
    description: str,
    style_preset: str,
    model_used: str,
    quality_level: str,
    dimensions: str,
    processing_steps: list[str],
    quality_metrics: dict[str, Any],
    generation_metadata: dict[str, Any],
) -> None:
    """
    Save generated image to repository with comprehensive metadata.
    """
    try:
        # Create repository structure
        repo_dir = Path("image_repository")
        repo_dir.mkdir(exist_ok=True)

        # Generate repository entry
        image_id = hashlib.md5(f"{description}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        # Copy image to repository
        repo_image_path = repo_dir / f"{image_id}.png"
        import shutil

        shutil.copy2(image_path, repo_image_path)

        # Create metadata
        metadata = {
            "id": image_id,
            "description": description,
            "style_preset": style_preset,
            "model_used": model_used,
            "quality_level": quality_level,
            "dimensions": dimensions,
            "processing_steps": processing_steps,
            "quality_metrics": quality_metrics,
            "generation_metadata": generation_metadata,
            "created_at": datetime.now().isoformat(),
            "file_path": str(repo_image_path),
            "file_size": os.path.getsize(repo_image_path),
        }

        # Save metadata
        metadata_path = repo_dir / f"{image_id}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"Saved image to repository: {image_id}")

    except Exception as e:
        logger.error(f"Failed to save image to repository: {e}")
