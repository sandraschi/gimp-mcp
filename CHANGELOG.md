# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.5.1] - 2026-05-28

### Added
- Automated sim-art import: Gazebo model thumbnails, avatar `.thumb.png`, batch match by model name
- MCPB manifest v4.5.1; `build_mcpb.py` bundles install + fleet docs
- Expanded `docs/readme/INSTALL.md` with MCPB and Agent Lab pipeline steps

## [4.5.0] - 2026-05-28

### Added
- **Agent Lab Phase 5**: `gimp_sim_art_tool` for Gazebo icons, texture atlases, VRChat batch
- `utils/sim_art_templates.py`, `utils/fleet_sim_pipeline.py`
- `scripts/sim_art_pipeline.py`, `scripts/run-sim-art-pipeline.ps1`
- `docs/SIM_ART_PIPELINE.md`, webapp Agent Tools Sim Art tab

## [4.4.0] - 2026-05-28

### Added
- **Agent Lab Phase 4**: Prometheus metrics (`utils/telemetry.py`), JSON logging (`utils/structured_logging.py`)
- `/api/metrics` and sidecar `:9073` scrape endpoint
- `Dockerfile`, `docker-compose.yml` with `--profile monitoring`
- `scripts/smoke_test.py`, GHCR `docker-publish` workflow
- `docs/MONITORING.md`, `docs/DOCKER.md`

### Changed
- Optional `monitoring` extra: `prometheus-client`
- Bridge status updates Prometheus gauges

## [4.3.0] - 2026-05-28

### Added
- **Agent Lab Phase 3**: `gimp_import_tool`, `gimp_vision_refine_tool`, fleet texture pipeline
- `utils/fleet_pipeline.py`, `scripts/fleet_pipeline.py`, `scripts/run-fleet-pipeline.ps1`
- `docs/FLEET_PIPELINE.md` — blender → gimp → unity texture handoff
- Webapp Agent Tools **Fleet** tab

## [4.2.0] - 2026-05-28

### Added
- **Agent Lab Phase 2**: `gimp_validation_tool` (validate_image, check_resolution, check_alpha, check_icc, audit_texture)
- Webapp **Agent Tools** page (`/agent-tools`) with Bridge, Vision, Validation, and Capture Gallery tabs
- `POST /api/v1/tool` bridge in `http_app.py` for webapp MCP tool calls
- Shared `tools/agent_lab_registration.py` for CLI + webapp tool registration

### Changed
- `server.py` registers Agent Lab tools for webapp backend
- Dashboard bridge port display updated to **10824**

## [4.1.1] - 2026-05-28

### Added
- **Agent Lab Phase 1**: `gimp_bridge_tool` (status, execution_mode, ping, list_open_images) and `gimp_render_tool` (bridge_status, capture_active, get_image_summary)
- `utils/gimp_runtime.py` and `utils/execution_mode.py` for Hands-In vs Hands-Off agent guidance
- `docs/COMPETITIVE_ANALYSIS.md` and `docs/ROADMAP.md`
- `tests/test_phase1_tools.py`

### Changed
- Bridge TCP port documented as **10824** fleet standard (replaces stale 10775 references)
- `gimp_live_status` delegates to `gimp_bridge` (kept for backwards compatibility)

## [4.1.0] - 2026-05-19

### Added
- **Generic PDB Proxy Tool** (`gimp_pdb`): Universal escape hatch to GIMP's full ~1000-procedure PDB. Accepts any procedure name + positional args, generates Python-Fu code on the fly. Registered on both CLI and webapp servers.
- **AI Image Generation**: Three real backends — Google Gemini Imagen, Stability AI, BFL/Flux. Switchable via `model` parameter on `generate_image` tool. API keys configured through Settings page or env vars (`GEMINI_API_KEY`, `STABILITY_API_KEY`, `BFL_API_KEY`).
- **Local LLM (Glom On)**: Auto-detect Ollama (:11434) and LM Studio (:1234) running on localhost. Settings dropdown to select provider and model. Multimodal models (Gemma 4:4B, LLaVA, etc.) supported for image understanding.
- **Chat Page**: Now tries local LLM first, falls back to cloud API. Provider indicator shows which LLM is active.
- **Image Understanding API**: `/api/llm/understand` and `/api/llm/suggest` endpoints — multimodal LLM can describe an image or propose GIMP operations to achieve a requested edit.
- **Settings Page**: API key management for all three AI providers + local LLM provider/model dropdown with Glom On scan button.
- **9 New Portmanteau Tools** — 17 total:
  - `gimp_workspace` (10 ops): list images, undo/redo, undo groups, metadata, resolution
  - `gimp_channel` (8 ops): create, delete, list, set color/opacity, duplicate channels
  - `gimp_gmic` (4 ops): G'MIC filter integration — 500+ filters via plug-in-gmic
  - `gimp_gegl` (2 ops): GEGL non-destructive editing operations
  - `gimp_color_management` (7 ops): ICC profiles, assignment, conversion, soft proofing
  - `gimp_animation` (5 ops): list frames, set delay, optimize/export GIF
  - `gimp_paths` (8 ops): create, delete, stroke, import/export SVG, vector paths
  - `gimp_parasites` (9 ops): XCF metadata — list, attach, detach parasites on images/drawables
- **SOTA Webapp Dashboard**: 5 new fleet-standard pages — Dashboard, Apps Hub, Chat, Skills, API Docs
- **State Management**: Zustand store for app state, toast notifications, global logger modal, help modal.
- **Standalone GIMP 3.2.4 Support**: Detects and uses standalone (non-Store) GIMP via `gimp-console-3.exe`. Uninstalled sandboxed Windows Store version.
- **GIMP Bridge Plugin**: Auto-installed to GIMP's plug-ins directory. Port changed to 10775 (10774 was squatted by Store remnants). `--restart-gimp` start.ps1 flag.
- **Fleet-wide `strictPort: true`**: Added to 63 repos' vite.config files to prevent silent port drift.

### Changed
- **CLI Batch Mode Fix**: Replaced hanging `pdb.gimp_quit(1)` with `--quit` flag. Fixed `\U` unicode escape bug in temp file paths. Both Script-Fu and Python-Fu modes work.
- **PDB Proxy Code Gen**: Uses `gi.repository.Gimp.get_pdb()` for GIMP 3 (no `gimpfu` module) with `lookup_procedure`/`create_config`/`run` pattern. Falls back to gimpfu for GIMP 2.x bridge.
- **GIMP Detector**: Added Windows Store path detection via process list and package directory scan.
- **justfile**: Expanded from 6 to 21 recipes covering startup, bridge, PDB, testing, cleaning.

### Fixed
- Port squatters on 10772/10773/10774 from repos missing `strictPort: true`.
- `start.ps1` port clearing now verifies port is actually free after kill attempts.

## [4.0.1] - 2026-04-27

### Added
- **Industrial Startup Script**: Root `start.ps1` with `-Headless`, `-BackendOnly`, and `-NoBrowser` support.
- **Improved Port Handling**: Automatic TCP squatter termination and health-check polling.

## [4.0.0] - 2026-03-24

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
