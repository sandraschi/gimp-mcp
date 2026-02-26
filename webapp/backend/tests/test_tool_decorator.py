"""
Test script to verify the tool decorator functionality.
"""
import asyncio
import logging
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import the tool decorator
sys.path.insert(0, str('.'))
from src.gimp_mcp.tool_utils import tool

# Test class with tool methods
class TestTools:
    def __init__(self):
        self.name = "TestTools"
    
    @tool(
        name="test_tool",
        description="A simple test tool to verify tool registration.",
        parameters={"name": {"type": "string", "default": "World"}}
    )
    async def test_tool(self, name: str = "World") -> Dict[str, Any]:
        """Test tool that returns a greeting.
        
        Args:
            name: Name to include in the greeting
            
        Returns:
            Dictionary containing the greeting
        """
        return {"greeting": f"Hello, {name}!", "tool": "test_tool"}

async def test_decorator():
    """Test the tool decorator functionality."""
    try:
        logger.info("Testing tool decorator...")
        
        # Create instance of test tools
        test_tools = TestTools()
        
        # Get the test_tool method
        test_method = getattr(test_tools, 'test_tool', None)
        
        if not test_method:
            logger.error("test_tool method not found")
            return False
            
        # Check if it has the _mcp_tool attribute
        if not hasattr(test_method, '_mcp_tool'):
            logger.error("test_tool method is not decorated with @tool")
            return False
            
        # Get the tool metadata
        tool_meta = getattr(test_method, '_mcp_tool', {})
        logger.info(f"Tool metadata: {tool_meta}")
        
        # Call the method
        logger.info("Calling test_tool...")
        result = await test_method("Test User")
        logger.info(f"test_tool result: {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test_decorator: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_decorator())
    if success:
        logger.info("Tool decorator test completed successfully")
        sys.exit(0)
    else:
        logger.error("Tool decorator test failed")
        sys.exit(1)
