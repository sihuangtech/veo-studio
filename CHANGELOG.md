# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-24

### Added
- Reference video analysis feature for generating video prompts from existing videos
- File upload state polling to ensure files are ready before processing
- Project-specific temporary directory (`.temp`) for temporary files

### Changed
- Renamed `run_gui.py` to `gui.py` for consistency
- Removed `config.example.json` file

### Documentation
- Added Chinese and English changelog files
- Updated project documentation

## [1.1.0] - 2025-12-22

### Added
- Support for custom Google GenAI API base URL configuration
- Ability to configure API endpoint in `config.json`

### Documentation
- Updated model selection instructions to reflect GUI dropdown and `config.json` usage

## [1.0.0] - 2025-12-13

### Added
- Initial Google Veo video generation project
- Graphical user interface (GUI) for video generation
- Command-line interface (CLI) support
- Support for Google GenAI API integration
- Configuration management via `config.json`
- Model selection dropdown in GUI
- Prompt and negative prompt input fields
- Aspect ratio and person generation settings
- Seed-based reproducible generation
- Video output management

### Changed
- Restructured project into an `app` package
- Adopted `uv` for dependency management
- Updated documentation and core logic files
