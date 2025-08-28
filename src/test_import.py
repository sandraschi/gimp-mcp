import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

print("\nAttempting to import gimp_mcp...")
try:
    import gimp_mcp
    print("Successfully imported gimp_mcp")
    print("gimp_mcp path:", gimp_mcp.__file__)
    
    # Try importing FileOperationTools
    from gimp_mcp.tools.file_operations import FileOperationTools
    print("Successfully imported FileOperationTools")
    
    # Try creating an instance
    from gimp_mcp.gimp_cli import GimpCliWrapper
    from gimp_mcp.config import GimpConfig
    
    print("Creating GimpCliWrapper and GimpConfig...")
    cli_wrapper = GimpCliWrapper()
    config = GimpConfig()
    
    print("Creating FileOperationTools instance...")
    tools = FileOperationTools(cli_wrapper, config)
    print("Successfully created FileOperationTools instance")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
