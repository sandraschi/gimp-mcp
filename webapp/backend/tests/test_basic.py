"""
Basic tests for GIMP MCP Server.

Tests core functionality including GIMP detection, configuration,
and basic tool operations.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path

from gimp_mcp.config import GimpConfig
from gimp_mcp.gimp_detector import GimpDetector
from gimp_mcp.cli_wrapper import GimpCliWrapper

class TestGimpDetection:
    """Test GIMP detection functionality."""
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly."""
        detector = GimpDetector()
        assert detector.system in ["windows", "darwin", "linux"]
    
    def test_get_default_paths(self):
        """Test that default paths are returned for current platform."""
        detector = GimpDetector()
        paths = detector.get_default_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0

class TestConfiguration:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = GimpConfig()
        assert config.max_concurrent_processes > 0
        assert config.process_timeout > 0
        assert len(config.supported_formats) > 0
        assert config.default_quality >= 1 and config.default_quality <= 100
    
    def test_temp_directory_validation(self):
        """Test temp directory validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = GimpConfig(temp_directory=temp_dir)
            assert Path(config.temp_directory).exists()
    
    def test_format_support_check(self):
        """Test format support checking."""
        config = GimpConfig()
        assert config.is_format_supported("jpeg")
        assert config.is_format_supported("png")
        assert not config.is_format_supported("unsupported_format")

class TestCliWrapper:
    """Test GIMP CLI wrapper functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return GimpConfig()
    
    def test_wrapper_initialization_without_gimp(self, config):
        """Test wrapper initialization (may fail if GIMP not installed)."""
        try:
            wrapper = GimpCliWrapper(config)
            # If we get here, GIMP was found
            assert wrapper.config == config
        except Exception:
            # GIMP not installed, which is fine for basic testing
            pytest.skip("GIMP not installed")

if __name__ == "__main__":
    pytest.main([__file__])
