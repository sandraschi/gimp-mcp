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
    @mcp.tool(
        name="greet",
        description="A simple greeting tool",
        parameters={
            "name": {
                "type": "string",
                "description": "Your name",
                "default": "World"
            }
        }
    )
    async def greet(name: str) -> dict:
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
