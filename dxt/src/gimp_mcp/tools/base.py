"""
Base class for GIMP MCP tool categories.

Provides common functionality and patterns for all tool implementations.
This module defines the base class that all GIMP MCP tools inherit from,
ensuring consistent behavior and interface across all tool categories.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable, Union
from functools import wraps
from pathlib import Path

from fastmcp import FastMCP

from ..cli_wrapper import GimpCliWrapper
from ..config import GimpConfig

logger = logging.getLogger(__name__)

# Type variable for tool methods
T = TypeVar('T', bound=Callable[..., Any])

def tool(
    name: Optional[str] = None,
    description: str = "",
    parameters: Optional[Dict[str, Dict[str, Any]]] = None,
    returns: Optional[Dict[str, Any]] = None,
    examples: Optional[List[Dict[str, str]]] = None
) -> Callable[[T], T]:
    """
    Decorator for GIMP MCP tool methods.
    
    This decorator enhances tool methods with metadata and documentation
    that can be used for API documentation, validation, and help systems.
    
    Args:
        name: Tool name (defaults to function name)
        description: Detailed description of the tool
        parameters: Parameter specifications
        returns: Return value specification
        examples: List of usage examples
        
    Returns:
        Decorated function with added metadata
    """
    def decorator(func: T) -> T:
        # Set or update function metadata
        if not hasattr(func, '_tool_metadata'):
            func._tool_metadata = {}
            
        func._tool_metadata.update({
            'name': name or func.__name__,
            'description': description or func.__doc__ or "",
            'parameters': parameters or {},
            'returns': returns or {},
            'examples': examples or []
        })
        
        # Preserve the original function's docstring and metadata
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
            
        return wrapper  # type: ignore
    return decorator

class BaseToolCategory(ABC):
    """
    Base class for all GIMP MCP tool categories.
    
    This class provides common functionality like error handling, validation,
    and consistent patterns across all tool implementations. All tool categories
    should inherit from this class and implement the required abstract methods.
    
    Attributes:
        cli_wrapper: Instance of GimpCliWrapper for executing GIMP commands
        config: Server configuration
        logger: Logger instance for the tool category
    """
    
    def __init__(self, cli_wrapper: GimpCliWrapper, config: GimpConfig):
        """
        Initialize base tool category with dependencies.
        
        Args:
            cli_wrapper: GIMP CLI wrapper instance for executing commands
            config: Server configuration with settings and allowed directories
            
        Example:
            ```python
            config = GimpConfig()
            cli_wrapper = GimpCliWrapper(config)
            tool = MyToolCategory(cli_wrapper, config)
            ```
        """
        self.cli_wrapper = cli_wrapper
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def register_tools(self, app: FastMCP) -> None:
        """
        Register all tools in this category with the FastMCP application.
        
        This method is responsible for setting up all the tool endpoints
        and their corresponding handlers. Each tool method should be decorated
        with @app.tool() and the appropriate metadata.
        
        Args:
            app: FastMCP application instance to register tools with
            
        Example:
            ```python
            @app.tool()
            async def my_tool(self, param1: str, param2: int) -> Dict[str, Any]:
                # Tool implementation
                pass
            ```
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
