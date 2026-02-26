#!/usr/bin/env python
"""Quick test of the fixed GIMP MCP tool registration."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print('=== Testing fixed tool registration ===')
    from fastmcp import FastMCP
    from gimp_mcp.tools.file_operations_tools import FileOperationTools
    from gimp_mcp.config import GimpConfig
    
    # Create FastMCP instance
    mcp = FastMCP(name='Test', version='1.0.0')
    print('SUCCESS: FastMCP instance created')
    
    # Create tool instance  
    config = GimpConfig()
    tools = FileOperationTools(None, config)
    print('SUCCESS: FileOperationTools instance created')
    
    # Register tools
    tools.register_tools(mcp)
    print('SUCCESS: Tools registered successfully')

    # Try to see registered tools
    if hasattr(mcp, '_tools') and mcp._tools:
        print(f'SUCCESS: Found {len(mcp._tools)} registered tools: {list(mcp._tools.keys())}')
    elif hasattr(mcp, 'tools') and mcp.tools:
        print(f'SUCCESS: Found {len(mcp.tools)} registered tools: {list(mcp.tools.keys())}')
    else:
        print('ERROR: No tools found in FastMCP instance')
        print(f'FastMCP attributes: {[x for x in dir(mcp) if not x.startswith("_")]}')

    print('\n=== Test completed ===')

except Exception as e:
    import traceback
    print(f'ERROR: {e}')
    traceback.print_exc()
