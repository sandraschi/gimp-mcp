# GIMP-MCP DXT Packaging Fix ⚡

**Issue:** DXT package missing FastMCP dependencies  
**Status:** ✅ FIXED  
**Timestamp:** 2025-08-17

## The Problem
When building with `dxt pack`, FastMCP dependencies weren't included:
```
ModuleNotFoundError: No module named 'fastmcp'
```

## The Fix - Update pyproject.toml
```toml
[project]
name = "gimp-mcp"
version = "0.1.0"
dependencies = [
    "fastmcp>=2.10.1",
    "typing-extensions>=4.8.0",
    "pillow>=10.0.0"
]

[project.scripts]
gimp-mcp = "gimp_mcp.server:main"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["gimp_mcp*"]
```

## Critical DXT Commands
```powershell
# In gimp-mcp directory
dxt validate  # Must pass BEFORE pack
dxt pack      # Creates .dxt file with ALL dependencies
```

## Manual Fix (if already installed)
```powershell
cd "C:\Users\sandr\AppData\Roaming\Claude\Claude Extensions\local.dxt.sandra-schipal.gimp-mcp"
pip install fastmcp --target lib
pip install typing-extensions --target lib
```

## Prevention
1. ✅ Always include FastMCP in pyproject.toml dependencies
2. ✅ Run `dxt validate` before `dxt pack`
3. ✅ Test module imports after installation

**This prevents the "Server disconnected" error in Claude Desktop!** 🎯