"""
Base class for GIMP MCP tool categories.

Provides common functionality and patterns for all tool implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ..cli_wrapper import GimpCliWrapper
from ..config import GimpConfig

logger = logging.getLogger(__name__)

class BaseToolCategory(ABC):
    """
    Base class for all GIMP MCP tool categories.
    
    Provides common functionality like error handling, validation,
    and consistent patterns across all tool implementations.
    """
    
    def __init__(self, cli_wrapper: GimpCliWrapper, config: GimpConfig):
        """
        Initialize base tool category.
        
        Args:
            cli_wrapper: GIMP CLI wrapper instance
            config: Server configuration
        """
        self.cli_wrapper = cli_wrapper
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def register_tools(self, app: FastMCP) -> None:
        """
        Register tools with FastMCP app.
        
        Args:
            app: FastMCP application instance
        """
        pass
    
    def validate_file_path(self, file_path: str, must_exist: bool = True) -> bool:
        """
        Validate file path for security and accessibility.
        
        Args:
            file_path: Path to validate
            must_exist: Whether file must exist
            
        Returns:
            bool: True if path is valid
        """
        try:
            from pathlib import Path
            
            path = Path(file_path).resolve()
            
            # Check if file exists (if required)
            if must_exist and not path.exists():
                return False
            
            # Check if parent directory exists (for output files)
            if not must_exist and not path.parent.exists():
                return False
            
            # Security: Check if path is within allowed directories
            if self.config.allowed_directories:
                allowed = any(
                    str(path).startswith(str(Path(allowed_dir).resolve()))
                    for allowed_dir in self.config.allowed_directories
                )
                if not allowed:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Path validation failed for {file_path}: {e}")
            return False
    
    def create_error_response(self, error_msg: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create standardized error response.
        
        Args:
            error_msg: Error message
            details: Optional error details
            
        Returns:
            Dict[str, Any]: Error response
        """
        response = {
            "success": False,
            "error": error_msg
        }
        
        if details:
            response["details"] = details
        
        return response
    
    def create_success_response(self, data: Any = None, message: str = "Operation completed successfully") -> Dict[str, Any]:
        """
        Create standardized success response.
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Dict[str, Any]: Success response
        """
        response = {
            "success": True,
            "message": message
        }
        
        if data is not None:
            response["data"] = data
        
        return response
