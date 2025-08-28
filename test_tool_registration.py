"""
Test script to verify tool registration in GIMP MCP Server.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.gimp_mcp.main import GimpMCPServer
from src.gimp_mcp.cli_wrapper import GimpCliWrapper
from src.gimp_mcp.config import GimpConfig

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def test_tool_registration():
    """Test tool registration in GIMP MCP Server."""
    try:
        logger.info("Starting tool registration test...")
        
        # Initialize config and server
        config = GimpConfig()
        server = GimpMCPServer()
        
        # Initialize the server
        logger.info("Initializing server...")
        if not await server.initialize():
            logger.error("Failed to initialize server")
            return False
            
        # Manually register tools for testing
        logger.info("Registering tools...")
        server._register_tools()
        
        # Check if tools were registered
        if not server.tools:
            logger.error("No tools were registered")
            return False
            
        # Log registered tools
        logger.info(f"Registered {len(server.tools)} tool categories")
        for category, tool_instance in server.tools.items():
            logger.info(f"Category: {category}")
            
            # Find and log methods with _mcp_tool attribute
            tool_methods = []
            for attr_name in dir(tool_instance):
                if attr_name.startswith('_'):
                    continue
                    
                attr = getattr(tool_instance, attr_name)
                if hasattr(attr, '_mcp_tool'):
                    tool_meta = getattr(attr, '_mcp_tool', {})
                    tool_methods.append({
                        'name': tool_meta.get('name', attr_name),
                        'description': tool_meta.get('description', 'No description')
                    })
            
            if tool_methods:
                logger.info(f"  Tools in {category}:")
                for tool_info in tool_methods:
                    logger.info(f"    - {tool_info['name']}: {tool_info['description']}")
            else:
                logger.warning(f"  No tools found in {category}")
        
        # Test the test_tool if available
        if 'file_operations' in server.tools and hasattr(server.tools['file_operations'], 'test_tool'):
            logger.info("Testing test_tool...")
            try:
                result = await server.tools['file_operations'].test_tool("Test User")
                logger.info(f"test_tool result: {result}")
            except Exception as e:
                logger.error(f"Error calling test_tool: {e}", exc_info=True)
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test_tool_registration: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tool_registration())
    if success:
        logger.info("Tool registration test completed successfully")
        sys.exit(0)
    else:
        logger.error("Tool registration test failed")
        sys.exit(1)
