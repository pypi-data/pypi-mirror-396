"""portfolio-mcp - Portfolio analysis MCP server powered by mcp-refcache."""

from importlib.metadata import PackageNotFoundError, version

# Package name must match [project].name in pyproject.toml
# This is the single source of truth for versioning
# Falls back to "0.0.0-dev" when running from source (e.g., Docker with copied files)
try:
    __version__ = version("portfolio-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

# Re-export config for convenience
from app.config import Settings, get_settings, settings

__all__ = [
    "Settings",
    "__version__",
    "get_settings",
    "settings",
]
