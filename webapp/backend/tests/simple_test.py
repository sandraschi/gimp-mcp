print("Starting simple test...")

# Add the current directory to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("Python path:", sys.path)

# Try to import the module
try:
    print("Attempting to import gimp_mcp...")
    import gimp_mcp
    print("Successfully imported gimp_mcp")
    print("gimp_mcp path:", gimp_mcp.__file__)
    
    # List available attributes
    print("\nAvailable attributes in gimp_mcp:", dir(gimp_mcp))
    
    # Try to import a specific class
    try:
        from gimp_mcp.tools.file_operations import FileOperationTools
        print("\nSuccessfully imported FileOperationTools")
    except ImportError as e:
        print(f"\nFailed to import FileOperationTools: {e}")
        
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()

print("\nTest completed.")
