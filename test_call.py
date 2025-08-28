import asyncio
from fastmcp import FastMCP

async def test_tool():
    # Connect to the running MCP server
    mcp = FastMCP("Test Client")
    
    try:
        # Call the test_tool
        result = await mcp.call_tool("test_tool", {"name": "GIMP User"})
        print("Test Tool Result:", result)
        
        # List all available tools
        tools = await mcp.list_tools()
        print("\nAvailable Tools:")
        for tool_name, tool_info in tools.items():
            print(f"- {tool_name}: {tool_info.get('description', 'No description')}")
            
    except Exception as e:
        print(f"Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(test_tool())
