"""Call a GIMP PDB procedure via CLI batch mode. Usage: python scripts/pdb_call.py <procedure>"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gimp_mcp.config import GimpConfig
from gimp_mcp.cli_wrapper import GimpCliWrapper
from gimp_mcp.tools.pdb_proxy import gimp_pdb

proc = sys.argv[1] if len(sys.argv) > 1 else "gimp-version"
gimp_bin = os.environ.get("GIMP_BIN", r"C:\Users\sandr\AppData\Local\Programs\GIMP 3\bin\gimp-console-3.exe")
cfg = GimpConfig(gimp_executable=gimp_bin, temp_directory=os.environ.get("TEMP", os.path.expanduser("~")))
cli = GimpCliWrapper(cfg)
r = asyncio.run(gimp_pdb(proc, [], cli_wrapper=cli, config=cfg))
print(r)
