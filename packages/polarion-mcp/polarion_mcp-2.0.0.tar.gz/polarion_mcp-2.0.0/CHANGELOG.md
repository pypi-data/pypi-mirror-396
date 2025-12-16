# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2024-12-13

### Added

- **New Tools**:

  - `get_polarion_work_item_revisions()` - Fetch revision history for work items (newest to oldest)
  - `get_polarion_work_item_at_revision()` - Get work item at a specific revision for historical analysis
  - `get_polarion_work_items_details()` - Batch fetch detailed information for multiple work items including custom fields and linked items
  - `get_polarion_work_item_text()` - Get formatted text representation of work items (title, description, key fields)

- **Enhanced Features**:

  - Added async Context support to `get_polarion_work_items()` for progress reporting
  - Added async Context support to `get_polarion_work_item_revisions()` with real-time progress updates
  - Added async Context support to `get_polarion_work_items_details()` with per-item progress tracking
  - Added async Context support to `polarion_github_requirements_coverage()` for better user feedback

- **Client Methods**:
  - Added `get_work_item_revisions()` to PolarionClient for revision history retrieval
  - Added `get_work_item_at_revision()` to PolarionClient for historical work item fetching
  - Added `get_work_items_details()` to PolarionClient for batch detailed work item fetching

### Improved

- Enhanced user experience with progress reporting on long-running operations
- Better visibility into multi-item fetching operations with per-item progress updates
- Comprehensive documentation for all new tools with usage examples and workflow guidance

## [Unreleased]

### Changed

- **BREAKING**: Removed Docker dependency - users no longer need Docker installed
- Restructured project as a proper Python package (`polarion_mcp/`)
- Moved from Docker-based deployment to PyPI distribution
- Updated installation method from Docker to pip
- Simplified mcp.json configuration from complex Docker args to simple command

### Added

- `polarion_mcp/` package with modular structure:
  - `__init__.py` - Package initialization and exports
  - `client.py` - Polarion API client (extracted from server)
  - `server.py` - MCP server with all tool definitions
  - `cli.py` - Command-line interface entry point
- GitHub Actions workflow for automatic PyPI publishing on version tags
- Comprehensive `.gitignore` for Python projects
- `MIGRATION.md` - Guide for existing Docker-based users
- CLI entry point: `polarion-mcp` command
- Support for `uvx` installation method (modern, zero-install approach)

### Removed

- `Dockerfile` - No longer needed
- `docker-build.sh` - Docker build script
- `package.json` - Node.js configuration (not used)
- `.github/workflows/docker-publish.yml` - Docker CI/CD pipeline
- `polarion_mcp_server.py` - Monolithic server file (split into package)
- FastAPI/uvicorn dependencies - Using stdio MCP only

### Updated

- `pyproject.toml` - Complete package configuration with:
  - Proper package discovery
  - Console script entry point: `polarion-mcp`
  - Version pinning for dependencies
  - Metadata and classifiers
- `requirements.txt` - Version-pinned dependencies, removed unnecessary packages
- `README.md` - Updated with pip and uvx installation options
- `USER_GUIDE.md` - Simplified 30-second setup guide for new installation method
- `DISTRIBUTION.md` - Complete PyPI publishing guide for maintainers

### Migration Guide

See `MIGRATION.md` for detailed information on updating from Docker-based setup.

## [0.1.0] - 2024-10-23

### Initial Release

- Polarion MCP Server with Docker-based distribution
- 8 MCP tools for Polarion interaction
- Token-based authentication
- Project, work item, and document querying
- GitHub requirements coverage analysis tool
- Comprehensive documentation

---

## Installation

### New Method (PyPI)

```bash
pip install polarion-mcp
```

### Legacy Method (Docker)

Use version tags before this refactoring. See git history.

## Future Plans

- Pre-built executables for Windows/macOS/Linux
- Advanced caching strategies
- Custom field support
- Revision history querying
- Multi-project support
- Web-based configuration UI
