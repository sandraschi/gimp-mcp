"""Test PDB proxy end-to-end."""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gimp_mcp.config import GimpConfig
from gimp_mcp.cli_wrapper import GimpCliWrapper
from gimp_mcp.tools.pdb_proxy import gimp_pdb

gimp_bin = os.environ.get("GIMP_BIN", r"C:\Users\sandr\AppData\Local\Programs\GIMP 3\bin\gimp-console-3.exe")
cfg = GimpConfig(gimp_executable=gimp_bin, temp_directory=os.environ.get("TEMP", os.path.expanduser("~")))
cli = GimpCliWrapper(cfg)
for proc in ["gimp-version", "gimp-selection-all"]:
    r = asyncio.run(gimp_pdb(proc, [], cli_wrapper=cli, config=cfg))
    status = "OK" if r.get("success") else "FAIL"
    print(f"[{status}] {proc}")
