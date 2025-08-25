# New GIMP MCP Tools - FastMCP 2.10 Implementation

This document describes the newly implemented tools for the GIMP MCP server, following FastMCP 2.10 standards with stdio transport support for MCP client connections.

## 🚀 FastMCP 2.10 Integration

The GIMP MCP server now fully supports FastMCP 2.10 standards with:

- **Stdio Transport**: Primary mode for MCP client connections (Claude Desktop, etc.)
- **HTTP Transport**: Optional web-based access mode
- **Modern Decorators**: `@app.tool()` decorators for tool registration
- **Async Support**: Full async/await pattern implementation
- **Type Safety**: Comprehensive type hints and validation

### Transport Modes

```bash
# Stdio mode (default) - for MCP client connections
gimp-mcp

# HTTP mode - for web-based access
gimp-mcp --http --host localhost --port 8000

# Validation mode
gimp-mcp --validate-only
```

## 🆕 New Tool Categories

### 1. Layer Management Tools (`LayerManagementTools`)

Comprehensive layer operations for GIMP images.

#### Available Tools

- **`create_layer`** - Create new layers with custom properties
- **`duplicate_layer`** - Duplicate existing layers
- **`delete_layer`** - Remove layers from images
- **`reorder_layer`** - Change layer stacking order
- **`set_layer_properties`** - Modify layer opacity, blend mode, visibility
- **`merge_layers`** - Combine multiple layers
- **`get_layer_info`** - Retrieve detailed layer information

#### Example Usage

```python
# Create a new layer
result = await create_layer(
    input_path="input.png",
    output_path="output.png",
    layer_name="Background",
    opacity=80.0,
    blend_mode="multiply"
)

# Duplicate a layer
result = await duplicate_layer(
    input_path="input.png",
    output_path="output.png",
    layer_index=0,
    new_name="Copy of Background"
)

# Set layer properties
result = await set_layer_properties(
    input_path="input.png",
    output_path="output.png",
    layer_index=0,
    opacity=75.0,
    blend_mode="overlay",
    visible=True,
    locked=False
)
```

#### Supported Blend Modes

- `normal`, `multiply`, `screen`, `overlay`
- `darken`, `lighten`, `color-dodge`, `color-burn`
- `hard-light`, `soft-light`, `difference`, `exclusion`
- `hue`, `saturation`, `color`, `value`

### 2. Image Analysis Tools (`ImageAnalysisTools`)

Advanced image analysis and quality assessment capabilities.

#### Available Tools

- **`analyze_image_quality`** - Comprehensive quality analysis
- **`extract_image_statistics`** - Detailed image statistics
- **`detect_image_issues`** - Identify quality problems
- **`compare_images`** - Compare two images
- **`generate_image_report`** - Generate comprehensive reports

#### Example Usage

```python
# Analyze image quality
result = await analyze_image_quality(
    input_path="image.png",
    analysis_type="comprehensive"
)

# Extract statistics with histogram data
result = await extract_image_statistics(
    input_path="image.png",
    include_histogram=True,
    include_color_info=True
)

# Detect common issues
result = await detect_image_issues(
    input_path="image.png",
    check_types=["resolution", "compression", "color"]
)

# Compare two images
result = await compare_images(
    image1_path="image1.png",
    image2_path="image2.png",
    comparison_type="comprehensive"
)
```

#### Analysis Types

- **`basic`** - Essential metrics only
- **`comprehensive`** - Full analysis with recommendations
- **`detailed`** - Maximum detail with technical information

#### Issue Detection

- **Resolution**: Low resolution warnings
- **Compression**: Quality and artifact detection
- **Color**: Color depth and palette analysis
- **Noise**: Image noise assessment
- **Artifacts**: Compression and processing artifacts

### 3. Performance Optimization Tools (`PerformanceTools`)

Performance monitoring, caching, and optimization capabilities.

#### Available Tools

- **`optimize_image_processing`** - Optimize processing with caching
- **`clear_cache`** - Manage performance cache
- **`get_performance_metrics`** - Retrieve performance statistics
- **`optimize_batch_processing`** - Optimize bulk operations
- **`get_system_performance_info`** - System resource monitoring

#### Example Usage

```python
# Optimize image processing with caching
result = await optimize_image_processing(
    input_path="input.png",
    output_path="output.png",
    optimization_level="balanced",
    enable_caching=True,
    memory_limit_mb=512
)

# Get performance metrics
result = await get_performance_metrics(
    operation_type="optimize_balanced",
    time_range_hours=24
)

# Optimize batch processing
result = await optimize_batch_processing(
    input_directory="/input/images",
    output_directory="/output/images",
    optimization_settings={
        "compression_quality": 90,
        "interpolation_method": "lanczos",
        "memory_optimization": True
    },
    enable_parallel=True,
    max_workers=4
)

# Monitor system performance
result = await get_system_performance_info()
```

#### Optimization Levels

- **`fast`** - Speed over quality (70% quality, linear interpolation)
- **`balanced`** - Speed/quality balance (85% quality, cubic interpolation)
- **`quality`** - Maximum quality (95% quality, lanczos interpolation)

#### Cache Management

- **Result Cache**: Store processed image results
- **Metrics Cache**: Performance measurement storage
- **Temporary Files**: Automatic cleanup and management
- **Memory Optimization**: Configurable memory limits

## 🔧 Tool Registration and Usage

### FastMCP 2.10 Tool Registration

All tools are automatically registered using the modern `@app.tool()` decorator:

```python
@app.tool()
async def tool_name(
    param1: str,
    param2: int = 10,
    param3: Optional[bool] = None
) -> Dict[str, Any]:
    """Tool description with parameter documentation."""
    # Tool implementation
    pass
```

### Parameter Validation

All tools include comprehensive parameter validation:

- **File Paths**: Existence and accessibility checks
- **Value Ranges**: Numeric parameter validation
- **Enum Values**: String parameter validation
- **Type Checking**: Runtime type validation
- **Security**: Path and access validation

### Response Format

Standardized response format for all tools:

```python
# Success response
{
    "success": True,
    "message": "Operation completed successfully",
    "details": {
        "input_path": "input.png",
        "output_path": "output.png",
        # Additional operation-specific details
    }
}

# Error response
{
    "success": False,
    "message": "Error description",
    "details": {
        "error_type": "validation_error",
        "error_code": "INVALID_PARAMETER"
    }
}
```

## 📊 Performance Monitoring

### Metrics Collection

The performance tools automatically collect:

- **Processing Times**: Operation duration tracking
- **Memory Usage**: Memory consumption monitoring
- **Cache Performance**: Hit/miss ratio tracking
- **System Resources**: CPU, memory, disk usage
- **GIMP Processes**: GIMP-specific resource monitoring

### Performance Analysis

```python
# Get comprehensive performance report
metrics = await get_performance_metrics()

# Analyze specific operation types
optimization_metrics = await get_performance_metrics(
    operation_type="optimize_balanced"
)

# Time-based analysis
recent_metrics = await get_performance_metrics(
    time_range_hours=1
)
```

### Cache Performance

```python
# Cache statistics
cache_stats = metrics["cache_statistics"]
hit_rate = cache_stats["hit_rate"]  # 0.0 to 1.0
cache_hits = cache_stats["cache_hits"]
cache_misses = cache_stats["cache_misses"]
```

## 🧪 Testing and Validation

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific tool tests
pytest tests/test_new_tools.py::TestLayerManagementTools
pytest tests/test_new_tools.py::TestImageAnalysisTools
pytest tests/test_new_tools.py::TestPerformanceTools

# Run with coverage
pytest --cov=gimp_mcp tests/
```

### Test Categories

- **Unit Tests**: Individual tool functionality
- **Integration Tests**: Tool interaction testing
- **Performance Tests**: Optimization and caching
- **Error Handling**: Validation and error cases
- **Mock Testing**: GIMP CLI wrapper simulation

## 🔒 Security Features

### File Validation

- **Path Security**: Access control and validation
- **File Type Checking**: MIME type verification
- **Size Limits**: Configurable file size restrictions
- **Directory Access**: Restricted directory access

### Process Isolation

- **Sandboxed Operations**: Isolated GIMP processes
- **Timeout Protection**: Operation time limits
- **Resource Limits**: Memory and CPU constraints
- **Error Recovery**: Graceful failure handling

## 📈 Usage Examples

### Complete Workflow Example

```python
# 1. Analyze input image
analysis = await analyze_image_quality(
    input_path="input.png",
    analysis_type="comprehensive"
)

# 2. Create optimized layer
layer_result = await create_layer(
    input_path="input.png",
    output_path="with_layer.png",
    layer_name="Enhancement",
    opacity=85.0,
    blend_mode="overlay"
)

# 3. Optimize processing
optimized = await optimize_image_processing(
    input_path="with_layer.png",
    output_path="final.png",
    optimization_level="quality",
    enable_caching=True
)

# 4. Monitor performance
performance = await get_performance_metrics()
print(f"Total operations: {performance['performance_statistics']['total_operations']}")
```

### Batch Processing Example

```python
# Optimize multiple images
batch_result = await optimize_batch_processing(
    input_directory="/photos/raw",
    output_directory="/photos/optimized",
    optimization_settings={
        "compression_quality": 90,
        "interpolation_method": "lanczos",
        "memory_optimization": True,
        "cache_results": True
    },
    enable_parallel=True,
    max_workers=4
)

print(f"Processed {batch_result['processing_results']['processed_files']} files")
print(f"Success rate: {batch_result['processing_results']['success_rate']:.1%}")
```

## 🚀 Advanced Features

### Custom Optimization Scripts

The performance tools support custom GIMP Script-Fu optimization:

```python
# Custom optimization parameters
custom_settings = {
    "compression_quality": 95,
    "interpolation_method": "lanczos",
    "memory_limit_mb": 1024,
    "custom_filters": ["unsharp_mask", "noise_reduction"]
}
```

### Layer Effect Chains

Advanced layer operations with effect chaining:

```python
# Create effect chain
effects = [
    {"type": "blur", "radius": 2.0, "method": "gaussian"},
    {"type": "sharpen", "amount": 0.5},
    {"type": "color_balance", "red": 0.1, "green": -0.05, "blue": 0.02}
]

for effect in effects:
    # Apply each effect in sequence
    pass
```

## 🔧 Configuration

### Performance Settings

```yaml
# config.yaml
performance:
  enable_caching: true
  cache_size_limit: 100
  memory_limit_mb: 512
  enable_parallel_processing: true
  max_workers: 4
  optimization_level: "balanced"
```

### Layer Management Settings

```yaml
# config.yaml
layers:
  default_opacity: 100.0
  default_blend_mode: "normal"
  max_layers: 100
  enable_layer_effects: true
  preserve_metadata: true
```

## 📚 API Reference

### Tool Parameters

All tools follow consistent parameter patterns:

- **`input_path`**: Source image file path (required)
- **`output_path`**: Destination file path (required)
- **`*_index`**: Layer or operation indices (0-based)
- **`*_type`**: Operation or analysis types
- **`enable_*`**: Boolean feature flags
- **`*_limit`**: Numeric limits and thresholds

### Return Values

Standardized return structure:

- **`success`**: Boolean operation status
- **`message`**: Human-readable result description
- **`details`**: Operation-specific data and metrics
- **`performance_metrics`**: Performance data (when applicable)
- **`cached`**: Cache usage indicator

## 🆘 Troubleshooting

### Common Issues

1. **GIMP Not Found**: Use `--validate-only` to check installation
2. **Permission Errors**: Verify file access permissions
3. **Memory Issues**: Adjust memory limits in configuration
4. **Cache Problems**: Use `clear_cache` to reset performance data

### Debug Mode

```bash
# Enable debug logging
gimp-mcp --log-level DEBUG

# Check server health
# The health_check tool provides comprehensive status information
```

### Performance Issues

- **Slow Processing**: Check optimization level and caching
- **High Memory Usage**: Adjust memory limits and batch sizes
- **Cache Inefficiency**: Monitor hit rates and clear old data

## 🔮 Future Enhancements

### Planned Features

- **AI-Powered Analysis**: Machine learning image assessment
- **Advanced Caching**: Predictive caching and optimization
- **Cloud Integration**: Remote processing capabilities
- **Plugin Architecture**: Third-party tool extensions

### Roadmap

- **Q2 2025**: AI integration and advanced analysis
- **Q3 2025**: Cloud processing and collaboration
- **Q4 2025**: Plugin ecosystem and extensibility
- **Q1 2026**: Enterprise features and scaling

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**FastMCP Version**: 2.10+  
**GIMP Version**: 2.10+ / 3.0+
