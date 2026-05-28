"""
Script to start the GIMP MCP server with default configuration.
"""
import logging
from pathlib import Path
from gimp_mcp.config import GimpConfig, load_config
from gimp_mcp.server import GimpMcpServer

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Try to load config from default location or create a new one
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Creating default configuration...")
        config = GimpConfig()
    
    # Start the server
    print("Starting GIMP MCP Server...")
    print(f"Configuration: {config.model_dump_json(indent=2)}")
    
    try:
        server = GimpMcpServer(config=config)
        server.run()
    except Exception as e:
        print(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    main()
