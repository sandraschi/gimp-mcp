"""
Comprehensive tests for new GIMP MCP tool categories.

Tests the newly implemented tools including layer management, image analysis,
and performance optimization tools following FastMCP 2.10 standards.
"""

import asyncio
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from gimp_mcp.tools.layer_management import LayerManagementTools
from gimp_mcp.tools.image_analysis import ImageAnalysisTools
from gimp_mcp.tools.performance_tools import PerformanceTools
from gimp_mcp.config import GimpConfig
from gimp_mcp.cli_wrapper import GimpCliWrapper

class TestLayerManagementTools:
    """Test layer management tools functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GimpConfig()
    
    @pytest.fixture
    def cli_wrapper(self, config):
        """Create mock CLI wrapper."""
        wrapper = Mock(spec=GimpCliWrapper)
        wrapper.execute_script_fu = AsyncMock(return_value="Success")
        return wrapper
    
    @pytest.fixture
    def layer_tools(self, cli_wrapper, config):
        """Create layer management tools instance."""
        return LayerManagementTools(cli_wrapper, config)
    
    def test_tool_initialization(self, layer_tools):
        """Test that layer tools initialize correctly."""
        assert layer_tools is not None
        assert hasattr(layer_tools, 'register_tools')
    
    @pytest.mark.asyncio
    async def test_create_layer_success(self, layer_tools, cli_wrapper):
        """Test successful layer creation."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        output_path = input_path.replace('.png', '_with_layer.png')
        
        # Mock file validation
        with patch.object(layer_tools, 'validate_file_path', return_value=True):
            result = await layer_tools.create_layer(
                input_path=input_path,
                output_path=output_path,
                layer_name="Test Layer",
                opacity=80.0,
                blend_mode="multiply"
            )
        
        assert result["success"] is True
        assert "Layer 'Test Layer' created successfully" in result["message"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_create_layer_invalid_opacity(self, layer_tools):
        """Test layer creation with invalid opacity."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        output_path = input_path.replace('.png', '_with_layer.png')
        
        with patch.object(layer_tools, 'validate_file_path', return_value=True):
            result = await layer_tools.create_layer(
                input_path=input_path,
                output_path=output_path,
                opacity=150.0  # Invalid opacity
            )
        
        assert result["success"] is False
        assert "Opacity must be between 0 and 100" in result["message"]
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_duplicate_layer_success(self, layer_tools, cli_wrapper):
        """Test successful layer duplication."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        output_path = input_path.replace('.png', '_duplicated.png')
        
        with patch.object(layer_tools, 'validate_file_path', return_value=True):
            result = await layer_tools.duplicate_layer(
                input_path=input_path,
                output_path=output_path,
                layer_index=0
            )
        
        assert result["success"] is True
        assert "Layer 0 duplicated successfully" in result["message"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_delete_layer_success(self, layer_tools, cli_wrapper):
        """Test successful layer deletion."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        output_path = input_path.replace('.png', '_deleted.png')
        
        with patch.object(layer_tools, 'validate_file_path', return_value=True):
            result = await layer_tools.delete_layer(
                input_path=input_path,
                output_path=output_path,
                layer_index=0
            )
        
        assert result["success"] is True
        assert "Layer 0 deleted successfully" in result["message"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path)

class TestImageAnalysisTools:
    """Test image analysis tools functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GimpConfig()
    
    @pytest.fixture
    def cli_wrapper(self, config):
        """Create mock CLI wrapper."""
        wrapper = Mock(spec=GimpCliWrapper)
        wrapper.execute_script_fu = AsyncMock(return_value="Image Quality Analysis:\nDimensions: 1920x1080\nTotal Pixels: 2073600")
        return wrapper
    
    @pytest.fixture
    def analysis_tools(self, cli_wrapper, config):
        """Create image analysis tools instance."""
        return ImageAnalysisTools(cli_wrapper, config)
    
    def test_tool_initialization(self, analysis_tools):
        """Test that analysis tools initialize correctly."""
        assert analysis_tools is not None
        assert hasattr(analysis_tools, 'register_tools')
    
    @pytest.mark.asyncio
    async def test_analyze_image_quality_success(self, analysis_tools, cli_wrapper):
        """Test successful image quality analysis."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        with patch.object(analysis_tools, 'validate_file_path', return_value=True):
            result = await analysis_tools.analyze_image_quality(
                input_path=input_path,
                analysis_type="comprehensive"
            )
        
        assert result["success"] is True
        assert "Image quality analysis completed successfully" in result["message"]
        assert "quality_metrics" in result["details"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_analyze_image_quality_invalid_type(self, analysis_tools):
        """Test image quality analysis with invalid type."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        with patch.object(analysis_tools, 'validate_file_path', return_value=True):
            result = await analysis_tools.analyze_image_quality(
                input_path=input_path,
                analysis_type="invalid_type"
            )
        
        assert result["success"] is False
        assert "Invalid analysis type" in result["message"]
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_extract_image_statistics_success(self, analysis_tools, cli_wrapper):
        """Test successful image statistics extraction."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        with patch.object(analysis_tools, 'validate_file_path', return_value=True):
            result = await analysis_tools.extract_image_statistics(
                input_path=input_path,
                include_histogram=True,
                include_color_info=True
            )
        
        assert result["success"] is True
        assert "Image statistics extracted successfully" in result["message"]
        assert "statistics" in result["details"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_detect_image_issues_success(self, analysis_tools, cli_wrapper):
        """Test successful image issue detection."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        with patch.object(analysis_tools, 'validate_file_path', return_value=True):
            result = await analysis_tools.detect_image_issues(
                input_path=input_path,
                check_types=["resolution", "compression"]
            )
        
        assert result["success"] is True
        assert "Image issue detection completed" in result["message"]
        assert "detected_issues" in result["details"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_compare_images_success(self, analysis_tools, cli_wrapper):
        """Test successful image comparison."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file1:
            input_path1 = tmp_file1.name
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file2:
            input_path2 = tmp_file2.name
        
        with patch.object(analysis_tools, 'validate_file_path', return_value=True):
            result = await analysis_tools.compare_images(
                image1_path=input_path1,
                image2_path=input_path2,
                comparison_type="visual"
            )
        
        assert result["success"] is True
        assert "Image comparison completed successfully" in result["message"]
        assert "comparison_results" in result["details"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path1)
        os.unlink(input_path2)

class TestPerformanceTools:
    """Test performance optimization tools functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = GimpConfig()
        config.temp_directory = tempfile.mkdtemp()
        return config
    
    @pytest.fixture
    def cli_wrapper(self, config):
        """Create mock CLI wrapper."""
        wrapper = Mock(spec=GimpCliWrapper)
        wrapper.execute_script_fu = AsyncMock(return_value="Success")
        return wrapper
    
    @pytest.fixture
    def performance_tools(self, cli_wrapper, config):
        """Create performance tools instance."""
        return PerformanceTools(cli_wrapper, config)
    
    def test_tool_initialization(self, performance_tools):
        """Test that performance tools initialize correctly."""
        assert performance_tools is not None
        assert hasattr(performance_tools, 'register_tools')
        assert hasattr(performance_tools, '_cache')
        assert hasattr(performance_tools, '_performance_metrics')
    
    @pytest.mark.asyncio
    async def test_optimize_image_processing_success(self, performance_tools, cli_wrapper):
        """Test successful image processing optimization."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        output_path = input_path.replace('.png', '_optimized.png')
        
        with patch.object(performance_tools, 'validate_file_path', return_value=True):
            result = await performance_tools.optimize_image_processing(
                input_path=input_path,
                output_path=output_path,
                optimization_level="balanced",
                enable_caching=True
            )
        
        assert result["success"] is True
        assert "Image processing optimized with balanced settings" in result["message"]
        assert "performance_metrics" in result["details"]
        cli_wrapper.execute_script_fu.assert_called_once()
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_optimize_image_processing_invalid_level(self, performance_tools):
        """Test image processing optimization with invalid level."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            input_path = tmp_file.name
        
        output_path = input_path.replace('.png', '_optimized.png')
        
        with patch.object(performance_tools, 'validate_file_path', return_value=True):
            result = await performance_tools.optimize_image_processing(
                input_path=input_path,
                output_path=output_path,
                optimization_level="invalid_level"
            )
        
        assert result["success"] is False
        assert "Invalid optimization level" in result["message"]
        
        # Cleanup
        os.unlink(input_path)
    
    @pytest.mark.asyncio
    async def test_clear_cache_success(self, performance_tools):
        """Test successful cache clearing."""
        # Add some test data to cache
        performance_tools._cache["test_key"] = "test_value"
        performance_tools._performance_metrics["test_op"] = {"time": 1.0}
        
        result = await performance_tools.clear_cache(cache_type="all")
        
        assert result["success"] is True
        assert "Cache cleared successfully" in result["message"]
        assert result["details"]["cleared_items"] >= 2
        assert len(performance_tools._cache) == 0
        assert len(performance_tools._performance_metrics) == 0
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_success(self, performance_tools):
        """Test successful performance metrics retrieval."""
        # Add test metrics
        performance_tools._performance_metrics["test_op"] = {
            "processing_time": 1.5,
            "memory_delta": 10.0,
            "timestamp": 1234567890.0
        }
        
        result = await performance_tools.get_performance_metrics()
        
        assert result["success"] is True
        assert "Performance metrics retrieved successfully" in result["message"]
        assert "performance_statistics" in result["details"]
        assert result["details"]["performance_statistics"]["total_operations"] == 1
    
    @pytest.mark.asyncio
    async def test_optimize_batch_processing_success(self, performance_tools, cli_wrapper):
        """Test successful batch processing optimization."""
        # Create test directories
        input_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        
        # Create test image files
        test_files = []
        for i in range(3):
            test_file = os.path.join(input_dir, f"test_{i}.png")
            with open(test_file, 'w') as f:
                f.write("test image data")
            test_files.append(test_file)
        
        try:
            result = await performance_tools.optimize_batch_processing(
                input_directory=input_dir,
                output_directory=output_dir,
                optimization_settings={"compression_quality": 90},
                enable_parallel=True,
                max_workers=2
            )
            
            assert result["success"] is True
            assert "Batch processing optimization completed" in result["message"]
            assert "processing_results" in result["details"]
            assert result["details"]["processing_results"]["total_files"] == 3
            
        finally:
            # Cleanup
            for test_file in test_files:
                if os.path.exists(test_file):
                    os.unlink(test_file)
            os.rmdir(input_dir)
            os.rmdir(output_dir)
    
    @pytest.mark.asyncio
    async def test_get_system_performance_info_success(self, performance_tools):
        """Test successful system performance info retrieval."""
        with patch('psutil.cpu_percent', return_value=25.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk, \
             patch('psutil.Process') as mock_process:
            
            # Mock memory info
            mock_memory.return_value.percent = 60.0
            mock_memory.return_value.available = 4 * 1024**3  # 4GB
            
            # Mock disk info
            mock_disk.return_value.percent = 45.0
            mock_disk.return_value.free = 100 * 1024**3  # 100GB
            
            # Mock process info
            mock_process_instance = Mock()
            mock_process_instance.memory_info.return_value.rss = 100 * 1024 * 1024  # 100MB
            mock_process_instance.cpu_percent.return_value = 5.0
            mock_process.return_value = mock_process_instance
            
            # Mock process iteration
            with patch('psutil.process_iter', return_value=[]):
                result = await performance_tools.get_system_performance_info()
            
            assert result["success"] is True
            assert "System performance information retrieved successfully" in result["message"]
            assert "system_performance" in result["details"]
            assert "process_performance" in result["details"]
    
    def test_cache_key_generation(self, performance_tools):
        """Test cache key generation functionality."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(b"test image data")
            tmp_file.flush()
            
            cache_key = performance_tools._generate_cache_key(tmp_file.name, "balanced")
            
            assert cache_key is not None
            assert "balanced" in cache_key
            assert len(cache_key) > 0
            
            # Cleanup
            os.unlink(tmp_file.name)
    
    def test_cache_operations(self, performance_tools):
        """Test cache operations functionality."""
        # Test caching
        performance_tools._cache_result("test_key", "test_value")
        assert "test_key" in performance_tools._cache
        assert performance_tools._cache["test_key"] == "test_value"
        
        # Test retrieval
        cached_value = performance_tools._get_cached_result("test_key")
        assert cached_value == "test_value"
        
        # Test cache size limiting
        for i in range(110):  # Exceed cache limit
            performance_tools._cache_result(f"key_{i}", f"value_{i}")
        
        assert len(performance_tools._cache) <= 100  # Cache size limited

if __name__ == "__main__":
    pytest.main([__file__])
