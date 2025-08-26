"""
Test FastMCP tool registration.
"""
import asyncio
import logging
from fastmcp import FastMCP

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Creating FastMCP instance...")
    mcp = FastMCP(
        name="Test MCP Server",
        version="1.0.0"
    )

    # Register a simple tool
    @mcp.tool
    async def greet(name: str = "World") -> dict:
        """A simple greeting tool
        
        Args:
            name: Your name
            
        Returns:
            A greeting message
        """
        return {"message": f"Hello, {name}!"}

    # Show registered routes
    logger.info("Registered routes:")
    for route in mcp.router.routes:
        logger.info(f"- {route.path} -> {route.endpoint.__name__}")

    # Start the server
    logger.info("Starting server...")
    await mcp.run(transport="stdio")

if __name__ == "__main__":
    asyncio.run(main())
