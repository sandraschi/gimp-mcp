# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2026-04-07

### Added
- **SOTA v13.1 Industrial Modernization**: Comprehensive refactor of the entire control plane.
- **Centralized Schema Registry**: Implementation of `schemas.py` with 17+ Pydantic request models.
- **Standardized Response Interface**: `GimpToolOutput[T]` generic wrapper for consistent success/error signaling and telemetry.
- **Enhanced Error Handling**: Centralized `handle_operation_error` in `BaseToolCategory`.

### Changed
- **Tool Documentation**: All tools and parameters expanded to 50-200 character LLM-optimized range.
- **Validation Layer**: Replaced legacy dictionary inputs with strict Pydantic validation.
- **Layer Management**: Refactored to utilize structured request models.
- **Image Analysis**: Refactored to utilize structured request models.
- **Performance Tools**: Modernized with caching and resource monitoring schemas.
- **Help System**: Transitioned to schema-backed dynamic documentation.

### Fixed
- Resolved 20+ linting issues related to unused imports and undefined names.
- Fixed circular dependency risks in tool registration.
- Corrected missing `Path` and optional type annotations in batch processing.

---

## [3.0.0] - 2026-01-19

### Added
- **AI Image Generation System**: Revolutionary conversational image creation using advanced AI models
- **generate_image tool**: Create images from natural language descriptions with GIMP post-processing
- **AI Model Support**: Integration with flux-dev and nano-banana-pro models
- **Style Presets**: photorealistic, artistic, technical, fantasy, and abstract styles
- **Quality Levels**: draft, standard, high, and ultra quality options
- **GIMP Post-Processing Pipeline**: Automatic application of sharpen, color correction, and enhancement operations
- **Image Repository**: Versioned asset management with comprehensive metadata and search capabilities
- **Quality Assessment**: Automatic evaluation and enhancement of generated images
- **Conversational Refinement**: Iterative improvement cycles with user feedback
- **Batch Processing**: Generate multiple images with consistent parameters

### Changed
- Updated server instructions to include AI image generation capabilities
- Enhanced help system with comprehensive AI generation documentation
- Improved portmanteau architecture to support agentic workflows

### Fixed
- N/A

### Removed
- N/A

---

## [2.0.0] - 2025-10-21

### Added
- Initial release
- Core functionality implemented
- Documentation created

### Changed
- N/A

### Fixed
- N/A

### Removed
- N/A

---

## How to Update This File

When making changes, add them under the appropriate section:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
