"""
Tests for GIMP MCP Portmanteau Tools.

FastMCP 2.13+ portmanteau architecture tests.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import os

# Import portmanteau tools
from src.gimp_mcp.tools import (
    gimp_file,
    gimp_transform,
    gimp_color,
    gimp_filter,
    gimp_layer,
    gimp_analysis,
    gimp_batch,
    gimp_system,
    PORTMANTEAU_TOOLS,
)


class TestPortmanteauImports:
    """Test that all portmanteau tools can be imported."""
    
    def test_all_tools_imported(self):
        """Verify all 8 portmanteau tools are available."""
        assert len(PORTMANTEAU_TOOLS) == 8
        
    def test_tool_names(self):
        """Verify tool names are correct."""
        tool_names = [t["name"] for t in PORTMANTEAU_TOOLS]
        expected = [
            "gimp_file", "gimp_transform", "gimp_color", "gimp_filter",
            "gimp_layer", "gimp_analysis", "gimp_batch", "gimp_system"
        ]
        assert tool_names == expected
    
    def test_all_tools_have_operations(self):
        """Verify all tools have at least one operation."""
        for tool in PORTMANTEAU_TOOLS:
            assert len(tool["operations"]) > 0, f"{tool['name']} has no operations"
    
    def test_total_operations(self):
        """Verify total operation count."""
        total = sum(len(t["operations"]) for t in PORTMANTEAU_TOOLS)
        assert total >= 50, f"Expected at least 50 operations, got {total}"


class TestGimpFileOperations:
    """Test gimp_file portmanteau tool."""
    
    @pytest.fixture
    def temp_image(self, tmp_path):
        """Create a temporary test image."""
        from PIL import Image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(img_path)
        return img_path
    
    @pytest.mark.asyncio
    async def test_file_info(self, temp_image):
        """Test getting file info."""
        result = await gimp_file(
            operation="info",
            input_path=str(temp_image)
        )
        assert result["success"] is True
        assert result["operation"] == "info"
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_file_load(self, temp_image):
        """Test loading a file."""
        result = await gimp_file(
            operation="load",
            input_path=str(temp_image)
        )
        assert result["success"] is True
        assert result["operation"] == "load"
    
    @pytest.mark.asyncio
    async def test_file_validate(self, temp_image):
        """Test validating a file."""
        result = await gimp_file(
            operation="validate",
            input_path=str(temp_image)
        )
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_file_not_found(self):
        """Test handling of missing file."""
        result = await gimp_file(
            operation="info",
            input_path="/nonexistent/path/image.jpg"
        )
        assert result["success"] is False
        assert "error" in result


class TestGimpTransformOperations:
    """Test gimp_transform portmanteau tool."""
    
    @pytest.fixture
    def temp_image(self, tmp_path):
        """Create a temporary test image."""
        from PIL import Image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (200, 100), color="blue")
        img.save(img_path)
        return img_path
    
    @pytest.mark.asyncio
    async def test_resize(self, temp_image, tmp_path):
        """Test resizing an image."""
        output_path = tmp_path / "resized.png"
        result = await gimp_transform(
            operation="resize",
            input_path=str(temp_image),
            output_path=str(output_path),
            width=100,
            height=50
        )
        assert result["success"] is True
        assert output_path.exists()
    
    @pytest.mark.asyncio
    async def test_rotate(self, temp_image, tmp_path):
        """Test rotating an image."""
        output_path = tmp_path / "rotated.png"
        result = await gimp_transform(
            operation="rotate",
            input_path=str(temp_image),
            output_path=str(output_path),
            degrees=90
        )
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_flip(self, temp_image, tmp_path):
        """Test flipping an image."""
        output_path = tmp_path / "flipped.png"
        result = await gimp_transform(
            operation="flip",
            input_path=str(temp_image),
            output_path=str(output_path),
            direction="horizontal"
        )
        assert result["success"] is True


class TestGimpColorOperations:
    """Test gimp_color portmanteau tool."""
    
    @pytest.fixture
    def temp_image(self, tmp_path):
        """Create a temporary test image."""
        from PIL import Image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="gray")
        img.save(img_path)
        return img_path
    
    @pytest.mark.asyncio
    async def test_brightness_contrast(self, temp_image, tmp_path):
        """Test brightness/contrast adjustment."""
        output_path = tmp_path / "adjusted.png"
        result = await gimp_color(
            operation="brightness_contrast",
            input_path=str(temp_image),
            output_path=str(output_path),
            brightness=20,
            contrast=10
        )
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_desaturate(self, temp_image, tmp_path):
        """Test desaturation."""
        output_path = tmp_path / "grayscale.png"
        result = await gimp_color(
            operation="desaturate",
            input_path=str(temp_image),
            output_path=str(output_path)
        )
        assert result["success"] is True


class TestGimpFilterOperations:
    """Test gimp_filter portmanteau tool."""
    
    @pytest.fixture
    def temp_image(self, tmp_path):
        """Create a temporary test image."""
        from PIL import Image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="white")
        img.save(img_path)
        return img_path
    
    @pytest.mark.asyncio
    async def test_blur(self, temp_image, tmp_path):
        """Test blur filter."""
        output_path = tmp_path / "blurred.png"
        result = await gimp_filter(
            operation="blur",
            input_path=str(temp_image),
            output_path=str(output_path),
            radius=5
        )
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_sharpen(self, temp_image, tmp_path):
        """Test sharpen filter."""
        output_path = tmp_path / "sharpened.png"
        result = await gimp_filter(
            operation="sharpen",
            input_path=str(temp_image),
            output_path=str(output_path)
        )
        assert result["success"] is True


class TestGimpAnalysisOperations:
    """Test gimp_analysis portmanteau tool."""
    
    @pytest.fixture
    def temp_image(self, tmp_path):
        """Create a temporary test image."""
        from PIL import Image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(img_path)
        return img_path
    
    @pytest.mark.asyncio
    async def test_quality_analysis(self, temp_image):
        """Test quality analysis."""
        result = await gimp_analysis(
            operation="quality",
            input_path=str(temp_image)
        )
        assert result["success"] is True
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_statistics(self, temp_image):
        """Test statistics extraction."""
        result = await gimp_analysis(
            operation="statistics",
            input_path=str(temp_image)
        )
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_histogram(self, temp_image):
        """Test histogram extraction."""
        result = await gimp_analysis(
            operation="histogram",
            input_path=str(temp_image)
        )
        assert result["success"] is True


class TestGimpBatchOperations:
    """Test gimp_batch portmanteau tool."""
    
    @pytest.fixture
    def temp_images(self, tmp_path):
        """Create temporary test images."""
        from PIL import Image
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        
        for i in range(3):
            img = Image.new("RGB", (100, 100), color=f"#{i*50:02x}{i*50:02x}{i*50:02x}")
            img.save(input_dir / f"test_{i}.png")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        return input_dir, output_dir
    
    @pytest.mark.asyncio
    async def test_batch_resize(self, temp_images):
        """Test batch resize."""
        input_dir, output_dir = temp_images
        result = await gimp_batch(
            operation="resize",
            input_directory=str(input_dir),
            output_directory=str(output_dir),
            width=50,
            file_pattern="*.png"
        )
        assert result["success"] is True
        assert result["data"]["processed"] > 0


class TestGimpSystemOperations:
    """Test gimp_system portmanteau tool."""
    
    @pytest.mark.asyncio
    async def test_status(self):
        """Test status check."""
        result = await gimp_system(operation="status")
        assert result["success"] is True
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_help(self):
        """Test help system."""
        result = await gimp_system(operation="help", topic="overview")
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_tools_list(self):
        """Test tools listing."""
        result = await gimp_system(operation="tools")
        assert result["success"] is True
        assert result["data"]["total_tools"] == 8
    
    @pytest.mark.asyncio
    async def test_version(self):
        """Test version info."""
        result = await gimp_system(operation="version")
        assert result["success"] is True
        assert "3.0.0" in result["data"]["server_version"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

