import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

print("Python path:", sys.path)
print("\nAttempting to import gimp_mcp...")

try:
    from gimp_mcp.tools.file_operations import FileOperationTools
    print("Successfully imported FileOperationTools")
    print("Class methods:", dir(FileOperationTools))
    
    # Test creating an instance
    from gimp_mcp.gimp_cli import GimpCliWrapper
    from gimp_mcp.config import GimpConfig
    
    print("\nCreating GimpCliWrapper and GimpConfig...")
    cli_wrapper = GimpCliWrapper()
    config = GimpConfig()
    
    print("Creating FileOperationTools instance...")
    tools = FileOperationTools(cli_wrapper, config)
    print("Successfully created FileOperationTools instance")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
