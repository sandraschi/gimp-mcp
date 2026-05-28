# GIMP MCP Server - DXT Extension Package

## 📦 Package Information

- **Name**: gimp-mcp
- **Version**: 0.1.0
- **Package Size**: 2.0 MB
- **SHA256**: 424e2aac40a87b1d6233dd00192ac476faa0c26b
- **Total Files**: 453
- **Unpacked Size**: 5.7 MB

## 🚀 What is GIMP MCP Server?

The GIMP MCP Server is a powerful Model Context Protocol (MCP) server that enables AI agents to perform professional image editing operations using GIMP (GNU Image Manipulation Program). It provides comprehensive image manipulation capabilities through a standardized MCP interface.

## ✨ Key Features

### Core Image Operations
- **File Management**: Open, save, export images in various formats
- **Layer Control**: Create, duplicate, merge, and manage layers
- **Transform Tools**: Resize, rotate, flip, and crop images
- **Color Adjustments**: Brightness, contrast, saturation, and hue modifications
- **Filter Applications**: Apply GIMP's extensive filter collection
- **Batch Processing**: Process multiple images automatically

### Advanced Capabilities
- **Image Analysis**: Quality assessment and statistics extraction
- **Performance Optimization**: Caching and parallel processing
- **Script Integration**: Execute custom GIMP Script-Fu scripts
- **Format Conversion**: Convert between image formats seamlessly

## 🛠️ Installation

### Prerequisites
- **Claude Desktop**: Latest version with MCP support
- **GIMP**: Version 3.0 or later installed on your system
- **Python**: 3.8 or later (included with Claude Desktop)

### Installation Steps
1. **Download**: Obtain the `gimp-mcp-0.1.0-complete.dxt` file
2. **Install**: Drag and drop the DXT file into Claude Desktop
3. **Configure**: Follow the setup prompts to configure GIMP executable path
4. **Restart**: Restart Claude Desktop to activate the extension

**Important**: This is a **completely standalone package** that includes all Python dependencies. No additional package installations are required!

## ⚙️ Configuration

### Required Settings
- **GIMP Executable Path**: Path to your GIMP installation
- **Temporary Directory**: Directory for processing files
- **Allowed Directories**: Directories the server can access
- **Process Limits**: Maximum concurrent operations and timeouts

### Platform-Specific GIMP Paths
- **Windows**: `C:\Program Files\GIMP 3\bin\gimp-3.0.exe`
- **macOS**: `/Applications/GIMP.app/Contents/MacOS/GIMP`
- **Linux**: `/usr/bin/gimp` or `/usr/local/bin/gimp`

## 🔧 Usage

### Basic Operations
```python
# Open an image
result = await open_image("path/to/image.jpg")

# Apply a filter
result = await apply_blur_filter("gaussian", radius=5.0)

# Save the result
result = await save_image("output.png", format="PNG")
```

### Batch Processing
```python
# Process multiple images
images = ["image1.jpg", "image2.jpg", "image3.jpg"]
for image in images:
    result = await resize_image(image, width=1920, height=1080)
    await save_image(f"resized_{image}", format="JPEG")
```

### Advanced Features
```python
# Analyze image quality
quality = await analyze_image_quality("image.jpg")

# Optimize performance
await optimize_image_processing(level="high")

# Get system performance info
performance = await get_system_performance_info()
```

## 📚 Available Tools

### File Operations
- `open_image` - Open image files with format detection
- `save_image` - Save images in specified format
- `export_image` - Export with specific settings
- `batch_open_images` - Open multiple images
- `batch_save_images` - Save multiple images

### Layer Management
- `create_layer` - Create new layers
- `duplicate_layer` - Copy existing layers
- `delete_layer` - Remove layers
- `reorder_layer` - Change layer order
- `set_layer_properties` - Modify layer properties
- `merge_layers` - Combine layers
- `get_layer_info` - Get layer details

### Transform Operations
- `resize_image` - Resize images
- `rotate_image` - Rotate by specific angles
- `flip_image` - Flip horizontally/vertically
- `crop_image` - Crop to dimensions
- `scale_layer` - Scale individual layers
- `transform_selection` - Transform selections

### Color Adjustments
- `adjust_brightness_contrast` - Modify brightness/contrast
- `adjust_hue_saturation` - Change color properties
- `adjust_color_balance` - Fine-tune color channels
- `convert_to_grayscale` - Remove color
- `invert_colors` - Create negative effect
- `adjust_gamma` - Modify gamma correction

### Filter Applications
- `apply_blur_filter` - Apply blur effects
- `apply_sharpen_filter` - Enhance sharpness
- `apply_noise_filter` - Add/reduce noise
- `apply_edge_detection` - Find edges
- `apply_emboss_filter` - Create 3D effect
- `apply_custom_filter` - Apply custom filters

### Batch Processing
- `batch_resize_images` - Resize multiple images
- `batch_convert_formats` - Convert formats
- `batch_apply_filters` - Apply filters to multiple images
- `batch_watermark` - Add watermarks
- `batch_optimize` - Optimize multiple images

### Image Analysis
- `analyze_image_quality` - Assess quality
- `extract_image_statistics` - Get statistics
- `detect_image_issues` - Find problems
- `compare_images` - Compare two images
- `generate_image_report` - Create analysis report

### Performance Tools
- `optimize_image_processing` - Optimize processing
- `clear_cache` - Clear caches
- `get_performance_metrics` - View metrics
- `optimize_batch_processing` - Enable parallel processing
- `get_system_performance_info` - Monitor system

## 🚨 Troubleshooting

### Common Issues

#### GIMP Not Found
- Verify GIMP is installed and accessible
- Check the executable path in configuration
- Ensure GIMP version is 3.0 or later

#### Permission Errors
- Check directory access permissions
- Verify allowed directories configuration
- Ensure temporary directory is writable

#### Format Not Supported
- Check image file integrity
- Verify GIMP supports the format
- Try converting to a supported format first

#### Memory Issues
- Reduce batch processing size
- Lower image resolution for large operations
- Close other applications to free memory

#### Timeout Errors
- Increase process timeout in configuration
- Check system performance
- Reduce operation complexity

### Recovery Strategies
1. **Retry Operations**: Some operations may succeed on retry
2. **Reduce Batch Size**: Process fewer images simultaneously
3. **Check Resources**: Ensure adequate memory and disk space
4. **Verify Files**: Check if source files are corrupted
5. **Restart Service**: Restart Claude Desktop if issues persist

## 📈 Performance Optimization

### Caching
- Operation results are cached for faster access
- Image metadata is stored for quick retrieval
- Filter presets are saved for reuse

### Parallel Processing
- Multiple images can be processed simultaneously
- System resources are monitored and optimized
- Batch operations use efficient queuing

### Resource Management
- Memory usage is optimized for large operations
- Disk I/O is minimized during processing
- System performance is continuously monitored

## 🔒 Security & Privacy

### Data Handling
- All operations are performed locally
- Images never leave your machine
- Temporary files are automatically cleaned up
- Access is limited to specified directories

### Best Practices
- Keep GIMP and dependencies updated
- Use secure configuration storage
- Limit access to necessary directories only
- Monitor operations for security

## 🔗 Integration

### MCP Ecosystem
- Compatible with all MCP-compliant clients
- Integrates with Claude Desktop seamlessly
- Supports standard MCP protocols
- Extensible for custom workflows

### External Tools
- Works with existing GIMP installations
- Supports custom Script-Fu scripts
- Compatible with GIMP plugins
- Integrates with image processing workflows

## 📞 Support

### Documentation
- **GitHub Repository**: [gimp-mcp](https://github.com/sandraschi/gimp-mcp)
- **API Reference**: See tool documentation above
- **Examples**: Check the main README for usage examples

### Issues & Questions
- **GitHub Issues**: [Report bugs](https://github.com/sandraschi/gimp-mcp/issues)
- **Discussions**: [Ask questions](https://github.com/sandraschi/gimp-mcp/discussions)
- **License**: MIT License

## 🆕 What's New in 0.1.0

### Initial Release Features
- Complete MCP server implementation
- Comprehensive image editing tools
- Layer management capabilities
- Batch processing support
- Performance optimization tools
- Image analysis features

### Technical Improvements
- FastMCP 2.10.1+ compatibility
- **Complete dependency bundling** - No external installations needed
- Optimized Python path configuration
- Robust error handling
- Comprehensive testing coverage
- Professional documentation

## 🚀 Future Roadmap

### Planned Features
- Advanced selection tools
- More filter options
- Enhanced batch processing
- Performance monitoring dashboard
- Plugin system for extensions

### Community Contributions
- Custom filter implementations
- Workflow templates
- Integration examples
- Performance optimizations

---

*The GIMP MCP Server DXT extension provides professional-grade image editing capabilities through Claude Desktop, enabling AI-assisted image manipulation with the power of GIMP. This package is completely standalone with all dependencies included.*
