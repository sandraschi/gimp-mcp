# GIMP MCP Tools Registration Fix Guide 🔧

**Status**: CRITICAL BUG - Server runs but shows no tools  
**Date**: 2025-08-28  
**FastMCP Version**: 2.11.3+ (needs update to 2.13+)

## 🚨 Problem Description

The GIMP MCP server starts successfully but shows **NO TOOLS** in Claude Desktop. Root cause: **Tool registration pattern is broken** due to FastMCP version compatibility issues.

### Current Symptoms:
- ✅ Server starts without errors
- ✅ MCP connection established  
- ❌ **Zero tools appear in Claude Desktop**
- ❌ Tool discovery fails silently

## 🔍 Diagnosed Issues

### 1. **FastMCP Tool Registration Pattern Mismatch** 🎯
**Problem**: Using outdated tool registration pattern for FastMCP 2.13+

```python
# ❌ WRONG (current broken pattern):
@app.tool()
async def create_image(width: int, height: int) -> Dict[str, Any]:
    """Create new GIMP image"""
    # Missing 'self' - FastMCP can't bind to instance

# ✅ RIGHT pattern for FastMCP 2.13+:
@app.tool() 
async def create_image(self, width: int, height: int) -> Dict[str, Any]:
    """Create new GIMP image"""
    # Bound method with self parameter
```

### 2. **Missing Tool Instance Context** ⚙️
Tools are registered but FastMCP can't find execution context due to:
- Decorator applied to unbound functions
- Missing class instance binding
- Incorrect method signatures

### 3. **FastMCP Version Compatibility** 📦
- Current: `fastmcp>=2.11.3`
- Required: `fastmcp>=2.13.0` for stable tool registration
- Breaking changes in tool discovery mechanism

## 🛠️ **Complete Fix Implementation**

### **Phase 1: Fix Tool Registration Pattern** 

#### Step 1: Update All Tool Files
Fix every tool method in these files:

- `src/gimp_mcp/tools/image_tools.py`
- `src/gimp_mcp/tools/layer_tools.py` 
- `src/gimp_mcp/tools/text_tools.py`
- `src/gimp_mcp/tools/filter_tools.py`
- `src/gimp_mcp/tools/path_tools.py`

#### Step 2: Tool Method Signature Fix Pattern

**Before (broken):**
```python
@app.tool()
async def create_image(width: int, height: int, fill_color: str = "white") -> Dict[str, Any]:
```

**After (fixed):**
```python
@app.tool()
async def create_image(self, width: int, height: int, fill_color: str = "white") -> Dict[str, Any]:
```

#### Step 3: Class Integration Check
Ensure all tool classes properly instantiate:

```python
# In main.py or __init__.py
class GimpMCPServer:
    def __init__(self):
        self.image_tools = ImageTools()  # Must instantiate
        self.layer_tools = LayerTools()
        # etc.
```

### **Phase 2: FastMCP Version Upgrade** 📦

#### Update pyproject.toml:
```toml
[tool.poetry.dependencies]
python = "^3.8"
fastmcp = "^2.13.0"  # Upgrade from 2.11.3
gimpfu = "^2.10.0"
Pillow = "^10.0.0"
```

#### Install Updated Dependencies:
```bash
cd D:\Dev\repos\gimp-mcp
poetry install --sync
```

### **Phase 3: Server Integration Fix** 🔧

#### Update main server file to properly register tool instances:

```python
# main.py or server.py
from fastmcp import FastMCP
from .tools.image_tools import ImageTools
from .tools.layer_tools import LayerTools
# ... other imports

app = FastMCP("GIMP MCP")

# Instantiate all tool classes
image_tools = ImageTools()
layer_tools = LayerTools()
# ... other tools

# Tools are auto-discovered via @app.tool() decorators
# No manual registration needed with bound methods

if __name__ == "__main__":
    app.run()
```

### **Phase 4: Validation & Testing** ✅

#### Test 1: Tool Discovery
```bash
# Check if tools are properly registered
python -c "from main import app; print(f'Registered tools: {len(app.list_tools())}')"
```

#### Test 2: Claude Desktop Integration
1. Restart Claude Desktop
2. Verify GIMP MCP shows tools in dropdown
3. Test a simple tool like `create_image`

#### Test 3: Error Handling
```python
# Test each tool category
await image_tools.create_image(800, 600)
await layer_tools.add_layer("Test Layer")
await text_tools.add_text("Hello GIMP!")
```

## 📋 **Implementation Checklist**

- [ ] **Phase 1**: Fix tool registration patterns 
  - [ ] Add `self` parameter to all `@app.tool()` methods
  - [ ] Update `image_tools.py`
  - [ ] Update `layer_tools.py`  
  - [ ] Update `text_tools.py`
  - [ ] Update `filter_tools.py`
  - [ ] Update `path_tools.py`

- [ ] **Phase 2**: Upgrade FastMCP
  - [ ] Update `pyproject.toml` to FastMCP 2.13+
  - [ ] Run `poetry install --sync`
  - [ ] Test server startup

- [ ] **Phase 3**: Server Integration  
  - [ ] Verify tool class instantiation
  - [ ] Check app.tool() decorator binding
  - [ ] Test tool discovery mechanism

- [ ] **Phase 4**: Full Testing
  - [ ] Restart Claude Desktop
  - [ ] Verify tools appear in MCP dropdown
  - [ ] Test individual tool execution
  - [ ] Validate error handling

## 🎯 **Expected Outcome**

After implementing all fixes:
- ✅ **20+ tools** visible in Claude Desktop
- ✅ Full GIMP automation capability
- ✅ Proper error handling and responses  
- ✅ FastMCP 2.13+ compatibility

## ⏱️ **Time Estimate**

**Total Implementation Time**: 2-3 hours
- Phase 1 (Tool fixes): 1-1.5 hours
- Phase 2 (FastMCP upgrade): 30 minutes  
- Phase 3 (Integration): 30 minutes
- Phase 4 (Testing): 30 minutes

## 🚨 **Priority**: CRITICAL
This fix is blocking all GIMP MCP functionality. Recommend immediate implementation.

---
**Next Action**: Start with Phase 1 tool registration pattern fixes across all tool files.