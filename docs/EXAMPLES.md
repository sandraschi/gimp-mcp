# 🎨 GIMP-MCP Examples

This document provides practical examples of how to use GIMP-MCP tools for common tasks.

## 🖼️ File Operations

### Get Image Information
To get detailed information about an image file:
```python
# Call the gimp_file:get_image_info tool
await use_tool('gimp_file', 'get_image_info', {
    'input_path': 'C:/Images/photo.jpg'
})
```

### Convert Image Format
To convert an image from one format to another (e.g., JPEG to WebP):
```python
# Call the gimp_file:convert_format tool
await use_tool('gimp_file', 'convert_format', {
    'input_path': 'C:/Images/photo.jpg',
    'output_path': 'C:/Images/photo.webp',
    'output_format': 'webp',
    'quality': 85
})
```

## 📐 Transform Operations

### Resize an Image
To resize an image to specific dimensions while maintaining the aspect ratio:
```python
# Call the gimp_transform:resize_image tool
await use_tool('gimp_transform', 'resize_image', {
    'input_path': 'C:/Images/photo.jpg',
    'output_path': 'C:/Images/resized.jpg',
    'width': 1920,
    'height': 1080,
    'maintain_aspect': True
})
```

### Crop an Image
To crop a specific region of an image:
```python
# Call the gimp_transform:crop_image tool
await use_tool('gimp_transform', 'crop_image', {
    'input_path': 'C:/Images/photo.jpg',
    'output_path': 'C:/Images/cropped.jpg',
    'x': 100,
    'y': 100,
    'width': 800,
    'height': 600
})
```

## 🌈 Color Adjustments

### Adjust Brightness and Contrast
To improve the tonal quality of an image:
```python
# Call the gimp_color:adjust_brightness_contrast tool
await use_tool('gimp_color', 'adjust_brightness_contrast', {
    'input_path': 'C:/Images/photo.jpg',
    'output_path': 'C:/Images/adjusted.jpg',
    'brightness': 0.2,
    'contrast': 0.1
})
```

## ✨ Filters and Effects

### Apply Gaussian Blur
To apply a smooth blur to an image:
```python
# Call the gimp_filter:apply_blur tool
await use_tool('gimp_filter', 'apply_blur', {
    'input_path': 'C:/Images/photo.jpg',
    'output_path': 'C:/Images/blurred.jpg',
    'radius': 5.0,
    'method': 'gaussian'
})
```

---

**These examples demonstrate common workflows using GIMP-MCP tools.** For more detailed information about each tool's parameters, please refer to the [Tool Reference](TOOL_REFERENCE.md) documentation.
