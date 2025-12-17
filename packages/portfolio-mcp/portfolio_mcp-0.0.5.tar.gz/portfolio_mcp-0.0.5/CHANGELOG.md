# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.5] - 2024-12-15

### Changed

- **Version bump** - Prepared for release v0.0.5
  - All three variants (dev, PyPI, Docker) now report correct version and variant
  - Full parity achieved across all deployment methods

## [0.0.4] - 2024-12-15

### Fixed

- **Docker version detection** - Docker image now properly installs the package
  - Base image: Copy `uv` to runtime stage for CLI usage
  - App image: Install `portfolio-mcp` package with `uv pip install --no-deps .`
  - CMD now uses `uv run portfolio-mcp` instead of `python -m app`
  - Fixes `__version__` showing `0.0.0-dev` instead of actual version
  - Development image uses editable install: `uv pip install --no-deps -e .`

## [0.0.3] - 2024-12-14

### Added

- **Version info in health_check** - `health_check` now returns `version` and `variant` fields
  - `version`: Package version from `__version__` (e.g., "0.0.3" or "0.0.0-dev")
  - `variant`: Deployment type ("dev" for local development, "installed" for PyPI/Docker)
  - Helps identify which MCP server variant is running

### Changed

- **Health check response structure** - Added `version` and `variant` to response
- **Test coverage** - Added tests for new health_check fields (17 tests passing)

### Fixed

- **Docker config cleanup** - Simplified compose, cleaned Zed settings
- **Bandit false positive** - Disabled B608 for f-string instructions (not SQL)

## [0.0.2] - 2024-12-14

### Fixed

- **Docker image**: Replace Chainguard with `python:slim` base image
  - Chainguard free tier only offers Python 3.14
  - Langfuse doesn't support Python 3.14 yet (pydantic v1 compatibility)
- **Version detection**: Handle `PackageNotFoundError` when running from source
  - Falls back to `0.0.0-dev` for Docker source-copy builds

### Changed

- **Python support**: Drop Python 3.14 from CI matrix (3.12 and 3.13 only)
- **Docker**: Add `PYTHON_VERSION` build arg (default: 3.12)
- **Zed settings**: Use `uvx fastmcp-template stdio` (PyPI install)

## [0.0.1] - 2024-12-14

### Added

- Initial release of FastMCP Template
- Core server implementation with mcp-refcache integration
- Example tools demonstrating caching patterns:
  - `hello` - Simple greeting tool (no caching)
  - `generate_items` - Generate items with public namespace caching
  - `store_secret` - Store secrets with EXECUTE-only agent permissions
  - `compute_with_secret` - Private computation without revealing values
  - `get_cached_result` - Paginate through cached results
  - `health_check` - Server health status
- Admin tools registration (permission-gated)
- Template guide prompt for usage instructions
- CLI with stdio and SSE transport options
- Project configuration:
  - UV-based dependency management
  - Nix flake for reproducible development environment
  - Ruff linting and formatting
  - Pytest with asyncio support
  - Pre-commit hooks (ruff, mypy, bandit, safety)
- GitHub Actions workflows:
  - CI pipeline with Python 3.12/3.13 matrix
  - Release workflow for version tags
- IDE configuration:
  - Zed settings with Pyright LSP and MCP context servers
  - GitHub Copilot instructions
- Documentation:
  - Contributing guidelines
  - Project rules for AI coding assistants

[Unreleased]: https://github.com/l4b4r4b4b4/portfolio-mcp/compare/v0.0.5...HEAD
[0.0.5]: https://github.com/l4b4r4b4b4/portfolio-mcp/releases/tag/v0.0.5
[0.0.4]: https://github.com/l4b4r4b4b4/portfolio-mcp/releases/tag/v0.0.4
[0.0.3]: https://github.com/l4b4r4b4b4/portfolio-mcp/releases/tag/v0.0.3
[0.0.3]: https://github.com/l4b4r4b4b4/portfolio-mcp/releases/tag/v0.0.3
[0.0.2]: https://github.com/l4b4r4b4b4/portfolio-mcp/releases/tag/v0.0.2
[0.0.1]: https://github.com/l4b4r4b4b4/portfolio-mcp/releases/tag/v0.0.1
