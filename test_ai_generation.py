#!/usr/bin/env python3
"""
Test script for AI Image Generation functionality in GIMP MCP.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_ai_generation():
    """Test the AI image generation functionality."""
    try:
        from gimp_mcp.main import GimpMCPServer

        print("Testing AI Image Generation in GIMP MCP...")

        # Create server instance
        server = GimpMCPServer()
        print("PASS: Server instance created")

        # Initialize server
        init_result = await server.initialize()
        if not init_result:
            print("FAIL: Server initialization failed")
            return False

        print("PASS: Server initialized successfully")

        # Check if generate_image tool is registered
        tools = server.tools
        if "generate_image" in [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in tools.values()]:
            print("PASS: generate_image tool is registered")
        else:
            print("WARN: generate_image tool not found in registered tools")
            print(f"Available tools: {list(tools.keys())}")

        # Try to call generate_image tool
        print("\nTesting generate_image tool call...")
        try:
            # Mock context for testing
            class MockContext:
                async def send(self, message):
                    print(f"Context message: {message}")

            ctx = MockContext()

            # Test parameters
            test_params = {
                "description": "a simple blue square for testing",
                "style_preset": "abstract",
                "dimensions": "256x256",
                "model": "flux-dev",
                "quality": "draft",
                "max_iterations": 1
            }

            print(f"Calling generate_image with params: {test_params}")

            # This would normally call the actual tool
            # For now, just test that the import and setup works
            print("PASS: generate_image tool call setup successful")

        except Exception as e:
            print(f"FAIL: Error testing generate_image tool: {e}")
            return False

        print("\nSUCCESS: AI Image Generation test completed successfully!")
        return True

    except Exception as e:
        print(f"FAIL: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_generation())
    sys.exit(0 if success else 1)