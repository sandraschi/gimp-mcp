import asyncio
import json
import sys
from fastmcp import FastMCP

async def test_client():
    # Create a client that connects to the server's stdio
    mcp = FastMCP("Test Client")
    
    try:
        # List available tools
        print("Listing available tools...")
        tools = await mcp.list_tools()
        print("Available Tools:")
        for tool_name, tool_info in tools.items():
            print(f"- {tool_name}: {tool_info.get('description', 'No description')}")
        
        # Test the test_tool
        print("\nTesting test_tool...")
        result = await mcp.call_tool("test_tool", {"name": "GIMP Tester"})
        print("Test Tool Result:", json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_client())
