"""Test CLI batch mode."""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gimp_mcp.config import GimpConfig
from gimp_mcp.cli_wrapper import GimpCliWrapper

gimp_bin = os.environ.get("GIMP_BIN", r"C:\Users\sandr\AppData\Local\Programs\GIMP 3\bin\gimp-console-3.exe")
cfg = GimpConfig(gimp_executable=gimp_bin, temp_directory=os.environ.get("TEMP", os.path.expanduser("~")))
cli = GimpCliWrapper(cfg)
r = asyncio.run(cli.execute_python_fu('print("CLI_OK")'))
print(r)
