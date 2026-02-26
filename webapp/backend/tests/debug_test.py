#!/usr/bin/env python
"""Debug test for GIMP MCP server imports and initialization."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print('Python path:', sys.path[:3])

try:
    print('=== Testing main imports ===')
    import gimp_mcp
    print('SUCCESS: gimp_mcp imported successfully')
    
    from gimp_mcp.main import GimpMCPServer
    print('SUCCESS: GimpMCPServer imported successfully')
    
    print('=== Testing tool imports ===')
    from gimp_mcp.tools import FileOperationTools
    print('SUCCESS: FileOperationTools imported')
    
    from gimp_mcp.tools import TransformTools
    print('SUCCESS: TransformTools imported')
    
    from gimp_mcp.tools import HelpTools
    print('SUCCESS: HelpTools imported')
    
    print('=== Testing FastMCP ===')
    from fastmcp import FastMCP
    print('SUCCESS: FastMCP imported')
    
    print('=== Creating test server ===')
    from gimp_mcp.config import GimpConfig
    config = GimpConfig()
    server = GimpMCPServer()
    print('SUCCESS: GimpMCPServer instance created')
    
    print('=== Creating FastMCP instance ===')
    mcp = FastMCP(name='Test', version='1.0.0')
    print('SUCCESS: FastMCP instance created')
    print(f'FastMCP type: {type(mcp)}')
    print(f'FastMCP methods: {[x for x in dir(mcp) if not x.startswith("_") and callable(getattr(mcp, x))]}')
    
    # Test tool registration by examining what happens in the main method
    print('\n=== Testing tool registration debug ===')
    
    # Simulate the registration process
    print(f"FastMCP instance has 'tool' decorator? {hasattr(mcp, 'tool')}")
    
    if hasattr(mcp, 'tool'):
        # Try to register a simple test tool
        @mcp.tool()
        def test_tool():
            """A test tool."""
            return "Test successful"
        
        print('SUCCESS: Test tool registered successfully')
    
    # Test what happens during _register_tools
    print('\n=== Simulating _register_tools ===')
    
    # Check if tools have register_tools method
    print('Checking FileOperationTools methods:')
    file_ops_methods = [x for x in dir(FileOperationTools) if not x.startswith('_')]
    print(f'FileOperationTools methods: {file_ops_methods}')
    
    # Try to create an instance
    print('Creating FileOperationTools instance...')
    file_ops = FileOperationTools(None, config)
    print(f'FileOperationTools instance methods: {[x for x in dir(file_ops) if not x.startswith("_")]}')
    
    # Check if register_tools method exists
    if hasattr(file_ops, 'register_tools'):
        print('SUCCESS: FileOperationTools has register_tools method')
    else:
        print('ERROR: FileOperationTools missing register_tools method')

except Exception as e:
    import traceback
    print(f'ERROR: Error: {e}')
    print('Full traceback:')
    traceback.print_exc()
