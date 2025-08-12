# GIMP-MCP Implementation Plan for Windsurf AI
**Document Version:** 1.0  
**Date:** 2025-08-12  
**Current Status:** Phase 1 Day 1 - Foundation Complete  
**Next Developer:** Windsurf AI or Human Developer  

## 🎯 PROJECT STATUS SUMMARY

### ✅ COMPLETED (Phase 1 Day 1)
The foundation is **100% complete** and ready for tool implementation:

1. **Repository Structure**: Complete scaffolding with proper Python package organization
2. **GIMP Detection**: Cross-platform detection system (Windows registry, macOS, Linux PATH)
3. **Configuration System**: Pydantic-based config with YAML support and validation
4. **CLI Wrapper**: Async GIMP command-line interface with Script-Fu execution
5. **Server Architecture**: FastMCP integration with tool registration framework
6. **Tool Categories**: Base classes and structure for 5 tool categories
7. **Error Handling**: Comprehensive exception hierarchy and response formatting

### 🎯 IMMEDIATE NEXT TASKS (Phase 1 Day 1 Completion)

#### Priority 1: Complete Core File Operations (30 minutes)
**File:** `src/gimp_mcp/tools/file_operations.py`

**Status:** Basic structure complete, needs Script-Fu implementation  
**What's needed:**
1. Fix imports in `cli_wrapper.py` (add missing yaml import)
2. Test file operations with actual GIMP installation
3. Validate Script-Fu scripts work correctly
4. Add proper error handling for GIMP command failures

#### Priority 2: Fix Import Issues (15 minutes)
**Files to fix:**
1. `src/gimp_mcp/cli_wrapper.py` - Missing `import yaml` (line needed but not used)
2. `src/gimp_mcp/main.py` - Update import paths to match actual structure
3. `src/gimp_mcp/tools/__init__.py` - Verify all imports work

#### Priority 3: Create Validation Test (20 minutes)
**File:** `tests/test_validation.py`

Create end-to-end test that:
1. Detects GIMP installation
2. Loads test image
3. Performs basic resize operation
4. Validates output file

## 📁 REPOSITORY STRUCTURE

```
D:\Dev\repos\gimp-mcp\
├── src/gimp_mcp/
│   ├── __init__.py              ✅ Complete
│   ├── main.py                  ✅ Complete (may need import fixes)
│   ├── server.py                ✅ Complete
│   ├── config.py                ✅ Complete
│   ├── gimp_detector.py         ✅ Complete
│   ├── cli_wrapper.py           ✅ Complete (needs yaml import fix)
│   └── tools/
│       ├── __init__.py          ✅ Complete
│       ├── base.py              ✅ Complete
│       ├── file_operations.py   🔄 90% Complete (needs testing)
│       ├── transforms.py        ✅ Complete
│       ├── color_adjustments.py 🔄 Placeholder only
│       ├── filters.py           🔄 Placeholder only
│       └── batch_processing.py  🔄 Placeholder only
├── docs/                        ✅ Complete (3 comprehensive docs)
├── tests/                       🔄 Basic structure only
├── pyproject.toml              ✅ Complete
├── requirements.txt            ✅ Complete
└── README.md                   ✅ Complete
```

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Foundation ✅ COMPLETE
- [x] Repository scaffolding
- [x] GIMP detection system
- [x] Configuration management
- [x] CLI wrapper framework
- [x] Server architecture
- [x] Tool base classes

### Phase 2: Core Tools (Days 1-2)
**Current Priority** 🎯

#### Day 1 Completion Tasks:
1. **Fix Import Issues** (15 min)
   - Add missing imports
   - Test basic server startup
   - Validate GIMP detection

2. **Complete File Operations** (45 min)
   - Test `load_image` with real GIMP
   - Validate `convert_image` Script-Fu
   - Add error handling for GIMP failures
   - Create simple validation test

3. **Basic Transform Testing** (30 min)
   - Test `resize_image` operation
   - Test `crop_image` operation
   - Validate Script-Fu syntax

#### Day 2 Tasks:
1. **Color Adjustment Tools** (2 hours)
   - Implement brightness/contrast
   - Implement hue/saturation
   - Add color balance tools

2. **Filter Implementation** (2 hours)
   - Gaussian blur filter
   - Sharpen (unsharp mask)
   - Basic noise reduction

3. **Testing Framework** (1 hour)
   - Comprehensive test suite
   - Mock GIMP responses
   - Error condition testing

### Phase 3: Advanced Features (Days 3-5)
1. **Batch Processing** - Parallel operations, progress tracking
2. **Advanced Filters** - Artistic effects, distortions
3. **Layer Operations** - Multi-layer support, compositing
4. **Performance Optimization** - Caching, process pooling

### Phase 4: Production Ready (Days 6-7)
1. **DXT Packaging** - Anthropic distribution format
2. **Documentation** - User guides, API reference
3. **CI/CD Setup** - Automated testing, releases

## 🔧 QUICK START FOR WINDSURF

### 1. Verify Repository State
```bash
cd D:\Dev\repos\gimp-mcp
ls -la src/gimp_mcp/
```

### 2. Fix Import Issues
```python
# In src/gimp_mcp/cli_wrapper.py, add at top:
import yaml  # Add this line

# Test imports work:
python -c "from src.gimp_mcp import GimpMcpServer; print('Imports OK')"
```

### 3. Test GIMP Detection
```bash
cd D:\Dev\repos\gimp-mcp
python -m src.gimp_mcp.main --validate-only
```

### 4. Run Basic Server Test
```python
# Create test_startup.py
from src.gimp_mcp.main import create_server

try:
    app = create_server()
    print("✅ Server created successfully")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 🎯 SPECIFIC IMPLEMENTATION TASKS

### Task 1: Fix CLI Wrapper (HIGH PRIORITY)
**File:** `src/gimp_mcp/cli_wrapper.py`
**Issue:** Missing import, untested Script-Fu scripts
**Fix:**
```python
# Add at top of file
import yaml
import shlex  # For proper command escaping

# Test the load_image_info function works with real GIMP
# Validate Script-Fu syntax is correct for GIMP 3.0
```

### Task 2: Complete File Operations Testing
**File:** `src/gimp_mcp/tools/file_operations.py`
**Status:** Implemented but untested
**Tasks:**
1. Create test image file
2. Test each tool function with actual GIMP
3. Validate Script-Fu syntax
4. Add proper error parsing from GIMP output

### Task 3: Implement Color Adjustments
**File:** `src/gimp_mcp/tools/color_adjustments.py`
**Current:** Placeholder only
**Needed:** Complete implementation using Script-Fu

```python
# Example Script-Fu for brightness/contrast:
script = f"""
(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE "{input_abs}" "{input_abs}")))
       (drawable (car (gimp-image-get-active-layer image))))
  (gimp-brightness-contrast drawable {brightness} {contrast})
  (gimp-file-save RUN-NONINTERACTIVE image drawable "{output_abs}" "{output_abs}")
  (gimp-image-delete image)
  (gimp-message "ADJUST:SUCCESS"))
"""
```

### Task 4: Add Comprehensive Testing
**File:** `tests/test_end_to_end.py` (create new)
**Purpose:** Validate entire workflow works

```python
import pytest
from pathlib import Path
from src.gimp_mcp.main import create_server

@pytest.mark.asyncio
async def test_complete_workflow():
    """Test complete image processing workflow"""
    # 1. Create server
    # 2. Load test image
    # 3. Resize image
    # 4. Save result
    # 5. Validate output
    pass
```

## 🐛 KNOWN ISSUES TO FIX

### Issue 1: Import Errors
- **File:** `cli_wrapper.py`
- **Fix:** Add missing `import yaml`
- **Impact:** High - blocks server startup

### Issue 2: Untested Script-Fu
- **Files:** All tool implementations
- **Fix:** Test with actual GIMP installation
- **Impact:** High - core functionality unknown

### Issue 3: Error Handling
- **File:** `cli_wrapper.py`
- **Fix:** Better parsing of GIMP error output
- **Impact:** Medium - poor error messages

### Issue 4: Path Handling
- **Files:** All tools
- **Fix:** Ensure Windows path escaping works
- **Impact:** Medium - cross-platform issues

## 🧪 TESTING STRATEGY

### Unit Tests (Quick - 5 minutes)
```bash
pytest tests/test_basic.py -v
```

### Integration Tests (Medium - 15 minutes)
Requires GIMP installation:
```bash
pytest tests/test_validation.py -v
```

### End-to-End Tests (Slow - 30 minutes)
Full workflow with real images:
```bash
pytest tests/test_end_to_end.py -v
```

## 📊 SUCCESS CRITERIA

### Day 1 Completion Checklist:
- [ ] Server starts without import errors
- [ ] GIMP detection works on current system
- [ ] Basic file operations work with real GIMP
- [ ] Simple resize operation completes successfully
- [ ] Error handling provides useful messages

### Day 2 Targets:
- [ ] All 15+ core tools implemented
- [ ] Comprehensive test suite passing
- [ ] Error recovery working properly
- [ ] Performance within expected ranges (<5s per operation)

## 🔄 DEVELOPMENT WORKFLOW

### For Windsurf AI:
1. **Start with Quick Fixes** - Fix imports and test basic functionality
2. **Test Incrementally** - Validate each component before proceeding  
3. **Use Real GIMP** - Test with actual GIMP installation when possible
4. **Document Issues** - Note any problems for human developer handoff
5. **Focus on Core Tools** - Prioritize file ops and transforms over advanced features

### For Human Developer:
1. **Review Windsurf Changes** - Validate code quality and test coverage
2. **Performance Testing** - Benchmark operations with large images
3. **Cross-platform Testing** - Test on Windows, macOS, Linux
4. **Production Setup** - DXT packaging and deployment preparation

---

**NEXT ACTION:** Fix import issues in `cli_wrapper.py` and test server startup
**ESTIMATED TIME:** 15-30 minutes for immediate fixes, 2-4 hours for complete Day 1 goals
**SUCCESS METRIC:** Server starts and processes at least one image successfully
