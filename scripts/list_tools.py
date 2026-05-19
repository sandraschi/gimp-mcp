"""List all registered portmanteau tools."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gimp_mcp.tools import PORTMANTEAU_TOOLS
for t in PORTMANTEAU_TOOLS:
    print(f"{t['name']:30s} {len(t['operations']):3d} ops  {t.get('description', '')}")
