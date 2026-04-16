from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ResponseStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class GimpToolOutput[T](BaseModel):
    """Standardized output wrapper for all GIMP MCP tools (SOTA v13.1)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: ResponseStatus = Field(..., description="Operation status: success, error, or warning")
    message: str = Field(..., description="Human-readable summary of the operation result")
    result: T | None = Field(None, description="The primary data payload of the tool response")
    error_code: str | None = Field(None, description="Industrial error code for automated handling")
    execution_time_ms: float | None = Field(None, description="Server-side processing time in milliseconds")
    recommendations: list[str] = Field(default_factory=list, description="Follow-up actions or parameter adjustments")


class ImageMetadata(BaseModel):
    """Refined image metadata schema with type-safe fields."""

    width: int = Field(..., ge=1, description="Image width in pixels")
    height: int = Field(..., ge=1, description="Image height in pixels")
    format: str = Field(..., description="Image file format (e.g., 'PNG', 'JPEG')")
    color_space: str = Field(..., description="GIMP color space (e.g., 'RGB', 'Grayscale')")
    layers: int = Field(..., ge=1, description="Number of layers in the image")
    file_size_bytes: int = Field(..., description="Size of the image file on disk")
    last_modified: datetime = Field(..., description="Timestamp of the last filesystem modification")
    has_alpha: bool = Field(..., description="Whether the image contains an alpha (transparency) channel")


# --- Input Models ---


class LoadImageRequest(BaseModel):
    """Request to load an image and retrieve its metadata."""

    file_path: str = Field(
        ..., description="Absolute filesystem path to the image file. Must be within allowed directories."
    )
    load_metadata: bool = Field(True, description="Whether to perform deep metadata extraction (Exif, XMP, etc.)")
    max_dimension: int = Field(
        0, ge=0, description="Optional: Maximum dimension for thumbnail generation. 0 disables thumbnails."
    )


class SaveImageRequest(BaseModel):
    """Request to save the current image buffer to disk."""

    output_path: str = Field(..., description="Absolute path for the output file.")
    format: str | None = Field(
        None, description="Target format (e.g., 'png', 'jpg'). Derived from extension if omitted."
    )
    quality: int = Field(90, ge=1, le=100, description="Compression quality for lossy formats (1-100).")
    overwrite: bool = Field(False, description="Whether to overwrite an existing file at the output path.")


class ResizeImageRequest(BaseModel):
    """Request to resize the image while maintaining quality/aspect ratio."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the resized image will be saved.")
    width: int | None = Field(None, ge=1, description="Target width in pixels.")
    height: int | None = Field(None, ge=1, description="Target height in pixels.")
    maintain_aspect: bool = Field(True, description="Whether to maintain the original aspect ratio.")
    interpolation: Literal["none", "linear", "cubic", "nohalo", "lohalo"] = Field(
        "cubic", description="Resampling algorithm for quality preservation."
    )


class CropImageRequest(BaseModel):
    """Request to crop the image to a specific rectangular region."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the cropped image will be saved.")
    x: int = Field(..., ge=0, description="Horizontal offset of the top-left corner.")
    y: int = Field(..., ge=0, description="Vertical offset of the top-left corner.")
    width: int = Field(..., ge=1, description="Width of the cropped area.")
    height: int = Field(..., ge=1, description="Height of the cropped area.")


class RotateImageRequest(BaseModel):
    """Request to rotate the image by a specific angle."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the rotated image will be saved.")
    degrees: float = Field(..., description="Rotation angle in degrees (clockwise).")
    interpolation: Literal["none", "linear", "cubic"] = Field("linear", description="Rotation resampling method.")
    auto_crop: bool = Field(True, description="Whether to crop the resulting image to remove transparency gaps.")


class ColorAdjustmentRequest(BaseModel):
    """Request for basic color corrections (brightness/contrast)."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the adjusted image will be saved.")
    brightness: int = Field(0, ge=-100, le=100, description="Brightness adjustment level (-100 to 100).")
    contrast: int = Field(0, ge=-100, le=100, description="Contrast adjustment level (-100 to 100).")


class HueSaturationRequest(BaseModel):
    """Request to adjust hue, saturation, and lightness."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the adjusted image will be saved.")
    hue: float = Field(0.0, ge=-180, le=180, description="Hue shift in degrees (-180 to 180).")
    saturation: float = Field(0.0, ge=-100, le=100, description="Saturation adjustment (-100 to 100).")
    lightness: float = Field(0.0, ge=-100, le=100, description="Lightness adjustment (-100 to 100).")


class LevelAdjustmentRequest(BaseModel):
    """Request to adjust image levels (tonal range)."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the adjusted image will be saved.")
    channel: Literal["value", "red", "green", "blue", "alpha"] = Field("value", description="Channel to adjust.")
    in_min: float = Field(0.0, ge=0.0, le=1.0, description="Input black point.")
    in_max: float = Field(1.0, ge=0.0, le=1.0, description="Input white point.")
    gamma: float = Field(1.0, ge=0.1, le=10.0, description="Gamma correction.")
    out_min: float = Field(0.0, ge=0.0, le=1.0, description="Output black point.")
    out_max: float = Field(1.0, ge=0.0, le=1.0, description="Output white point.")


class FilterRequest(BaseModel):
    """Generic request for applying GIMP filters."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the filtered image will be saved.")
    filter_name: str = Field(..., description="Internal GIMP filter identifier or common name.")
    params: dict[str, Any] = Field(default_factory=dict, description="Filter-specific parameters.")


class BlurRequest(BaseModel):
    """Request to apply blur effects."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the blurred image will be saved.")
    radius: float = Field(1.0, ge=0.1, le=100.0, description="Blur radius in pixels.")
    method: Literal["gaussian", "motion", "radial", "pixelize", "zoom", "lens", "selective_gaussian"] = Field(
        "gaussian", description="Blur algorithm."
    )
    angle: float = Field(0.0, description="Angle for motion/zoom blur.")


class SharpenRequest(BaseModel):
    """Request to sharpen the image."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the sharpened image will be saved.")
    radius: float = Field(1.0, ge=0.1, le=100.0, description="Sharpening radius.")
    amount: float = Field(0.5, ge=0.0, le=5.0, description="Strength of the effect.")
    threshold: float = Field(0.0, ge=0.0, le=1.0, description="Edge detection threshold.")


class ArtisticEffectRequest(BaseModel):
    """Request to apply artistic filters."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    effect: str = Field(..., description="Name of the artistic effect (oilify, cartoon, etc.).")
    intensity: float = Field(0.5, ge=0.0, le=1.0, description="Overall intensity of the effect.")


class HelpRequest(BaseModel):
    """Request for tool or category help."""

    query: str | None = Field(None, description="Specific tool or category name.")
    level: Literal["beginner", "intermediate", "advanced", "expert"] = Field("beginner", description="Detail level.")


class BatchResizeRequest(BaseModel):
    """Request for bulk image resizing."""

    input_paths: list[str] = Field(..., min_length=1, description="List of source image paths.")
    output_directory: str = Field(..., description="Target directory for resized images.")
    width: int = Field(..., ge=1, description="Common target width.")
    height: int = Field(..., ge=1, description="Common target height.")
    parallel_jobs: int = Field(4, ge=1, le=16, description="Maximum number of concurrent GIMP processes.")


class BatchConvertRequest(BaseModel):
    """Request for bulk format conversion."""

    input_paths: list[str] = Field(..., min_length=1, description="List of source image paths.")
    output_directory: str = Field(..., description="Directory for converted files.")
    target_format: str = Field(..., description="Target format (png, jpg, webp, etc.).")
    quality: int = Field(85, ge=1, le=100, description="Quality setting (1-100).")


# Layer Management Requests
class CreateLayerRequest(BaseModel):
    """Request to create a new layer."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    layer_name: str = Field("New Layer", description="Name for the new layer.")
    layer_type: str = Field("normal", description="Type of layer (normal, text, mask, etc.).")
    opacity: float = Field(100.0, ge=0.0, le=100.0, description="Layer opacity (0-100).")
    blend_mode: str = Field("normal", description="Blending mode for the layer.")


class DuplicateLayerRequest(BaseModel):
    """Request to duplicate a layer."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    layer_index: int = Field(0, ge=0, description="Index of the layer to duplicate.")
    new_name: str | None = Field(None, description="Optional name for the duplicate.")


class DeleteLayerRequest(BaseModel):
    """Request to delete a layer."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    layer_index: int = Field(0, ge=0, description="Index of the layer to delete.")


class ReorderLayerRequest(BaseModel):
    """Request to move a layer in the stack."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    layer_index: int = Field(..., description="Current index of the layer.")
    new_position: int = Field(..., description="Target position in the stack.")


class SetLayerPropertiesRequest(BaseModel):
    """Request to modify layer properties."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    layer_index: int = Field(0, ge=0, description="Index of the layer.")
    opacity: float | None = Field(None, ge=0.0, le=100.0, description="New opacity.")
    blend_mode: str | None = Field(None, description="New blend mode.")
    visible: bool | None = Field(None, description="Visibility status.")
    locked: bool | None = Field(None, description="Lock status.")


class MergeLayersRequest(BaseModel):
    """Request to merge multiple layers."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    layer_indices: list[int] = Field(..., description="List of layer indices to merge.")
    merge_mode: str = Field("merge_down", description="Merge strategy (merge_down, merge_visible, flatten).")


class GetLayerInfoRequest(BaseModel):
    """Request for layer metadata."""

    input_path: str = Field(..., description="Path to the source image file.")
    layer_index: int | None = Field(None, description="Specific layer index or None for all.")


# Image Analysis Requests
class AnalyzeImageQualityRequest(BaseModel):
    """Request for image quality assessment."""

    input_path: str = Field(..., description="Path to the source image file.")
    analysis_type: str = Field("comprehensive", description="Analysis detail level.")


class ExtractImageStatisticsRequest(BaseModel):
    """Request for detailed image statistics."""

    input_path: str = Field(..., description="Path to the source image file.")
    include_histogram: bool = Field(True, description="Whether to include histogram data.")
    include_color_info: bool = Field(True, description="Whether to include color stats.")


class DetectImageIssuesRequest(BaseModel):
    """Request to scan for image defects."""

    input_path: str = Field(..., description="Path to the source image file.")
    check_types: list[str] = Field(["all"], description="Types of issues to check.")


class CompareImagesRequest(BaseModel):
    """Request to compare two images."""

    image1_path: str = Field(..., description="Path to first image.")
    image2_path: str = Field(..., description="Path to second image.")
    comparison_type: str = Field("visual", description="Comparison strategy.")


class GenerateImageReportRequest(BaseModel):
    """Request for comprehensive image report."""

    input_path: str = Field(..., description="Path to the source image file.")
    report_format: str = Field("detailed", description="Report detail level.")


# Performance Requests
class OptimizePerformanceRequest(BaseModel):
    """Request to optimize processing performance."""

    input_path: str = Field(..., description="Path to the source image file.")
    output_path: str = Field(..., description="Path where the transformed image will be saved.")
    optimization_level: str = Field("balanced", description="Optimization level.")
    enable_caching: bool = Field(True, description="Enable result caching.")
    memory_limit_mb: int | None = Field(None, description="Explicit memory limit.")
    parallel_jobs: int = Field(4, ge=1, le=16, description="Maximum number of concurrent GIMP processes.")
