"""Configuration module for portfolio-mcp Server.

Uses pydantic-settings for environment-based configuration with validation.

Environment Variables:
    CACHE_BACKEND: Cache backend type - memory, sqlite, redis (default: auto)
    REDIS_URL: Redis connection URL (default: redis://localhost:6379)
    SQLITE_PATH: SQLite database path (default: XDG data dir)
    PORTFOLIO_MCP_PORT: Server port for HTTP modes (default: 8000)
    PORTFOLIO_MCP_HOST: Server host for HTTP modes (default: 0.0.0.0)
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_default_sqlite_path() -> str:
    """Get XDG-compliant default SQLite path."""
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        base_dir = Path(xdg_data_home)
    else:
        base_dir = Path.home() / ".local" / "share"

    return str(base_dir / "portfolio-mcp" / "cache.db")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # Cache backend configuration
    cache_backend: Literal["memory", "sqlite", "redis", "auto"] = Field(
        default="auto",
        description=(
            "Cache backend type. 'auto' selects sqlite for stdio, redis for HTTP modes."
        ),
    )
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for distributed caching.",
    )
    sqlite_path: str = Field(
        default_factory=_get_default_sqlite_path,
        description="SQLite database path for local persistence.",
    )

    # Server configuration (for HTTP modes)
    portfolio_mcp_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port for SSE and streamable-http modes.",
    )
    portfolio_mcp_host: str = Field(
        default="0.0.0.0",  # nosec B104 - intentional for Docker/container deployments
        description="Server host for SSE and streamable-http modes.",
    )

    # Portfolio-specific configuration
    default_risk_free_rate: float = Field(
        default=0.02,
        ge=0.0,
        le=1.0,
        description="Default risk-free rate for portfolio calculations (e.g., 0.02 = 2%).",
    )
    default_trading_days: int = Field(
        default=252,
        ge=1,
        le=365,
        description="Default number of trading days per year for annualization.",
    )

    @field_validator("sqlite_path")
    @classmethod
    def expand_sqlite_path(cls, value: str) -> str:
        """Expand ~ in SQLite path."""
        return str(Path(value).expanduser())

    def get_cache_backend_for_transport(
        self,
        transport: Literal["stdio", "sse", "streamable-http"],
    ) -> Literal["memory", "sqlite", "redis"]:
        """Get the appropriate cache backend for the given transport.

        Args:
            transport: The MCP transport mode being used.

        Returns:
            The cache backend to use.
        """
        if self.cache_backend != "auto":
            # Explicit backend configured
            return self.cache_backend

        # Auto-select based on transport
        if transport == "stdio":
            return "sqlite"
        else:
            # HTTP modes (sse, streamable-http) use Redis for distributed caching
            return "redis"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Singleton Settings instance loaded from environment.
    """
    return Settings()


# Convenience export for direct access
settings = get_settings()
