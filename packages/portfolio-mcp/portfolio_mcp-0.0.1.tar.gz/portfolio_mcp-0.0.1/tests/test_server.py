"""Tests for the portfolio-mcp server module."""

from __future__ import annotations

from app.server import cache, mcp, store


class TestServerInitialization:
    """Tests for server initialization."""

    def test_mcp_instance_exists(self) -> None:
        """Test that FastMCP instance is created."""
        assert mcp is not None
        assert mcp.name == "portfolio-mcp"

    def test_cache_instance_exists(self) -> None:
        """Test that RefCache instance is created."""
        assert cache is not None
        assert cache.name == "portfolio-mcp"

    def test_store_instance_exists(self) -> None:
        """Test that PortfolioStore instance is created."""
        assert store is not None
        assert store.namespace == "portfolios"

    def test_store_uses_cache(self) -> None:
        """Test that store uses the configured cache."""
        assert store.cache is cache


class TestHealthCheck:
    """Tests for health_check tool."""

    def _call_health_check(self) -> dict:
        """Helper to call health_check, handling FunctionTool wrapper."""
        # After @mcp.tool decorator, health_check becomes FunctionTool
        # We need to access the underlying function via .fn attribute
        from app import server

        health_fn = server.health_check
        # If it's a FunctionTool, get the underlying function
        if hasattr(health_fn, "fn"):
            return health_fn.fn()
        return health_fn()

    def test_health_check_returns_status(self) -> None:
        """Test that health check returns healthy status."""
        result = self._call_health_check()

        assert "status" in result
        assert result["status"] == "healthy"

    def test_health_check_returns_server_name(self) -> None:
        """Test that health check returns server name."""
        result = self._call_health_check()

        assert "server" in result
        assert result["server"] == "portfolio-mcp"

    def test_health_check_returns_cache_name(self) -> None:
        """Test that health check returns cache name."""
        result = self._call_health_check()

        assert "cache" in result
        assert result["cache"] == "portfolio-mcp"

    def test_health_check_returns_portfolio_count(self) -> None:
        """Test that health check returns portfolio count."""
        result = self._call_health_check()

        assert "portfolios_stored" in result
        assert isinstance(result["portfolios_stored"], int)
        assert result["portfolios_stored"] >= 0

    def test_health_check_structure(self) -> None:
        """Test complete health check response structure."""
        result = self._call_health_check()

        expected_keys = {"status", "server", "cache", "portfolios_stored"}
        assert set(result.keys()) == expected_keys


class TestMCPConfiguration:
    """Tests for MCP server configuration."""

    def test_mcp_has_instructions(self) -> None:
        """Test that MCP has instructions configured."""
        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0

    def test_instructions_mention_portfolio(self) -> None:
        """Test that instructions mention portfolio tools."""
        assert "portfolio" in mcp.instructions.lower()

    def test_instructions_mention_optimization(self) -> None:
        """Test that instructions mention optimization."""
        assert "optim" in mcp.instructions.lower()

    def test_instructions_mention_yahoo(self) -> None:
        """Test that instructions mention Yahoo Finance."""
        assert "yahoo" in mcp.instructions.lower()

    def test_instructions_mention_crypto(self) -> None:
        """Test that instructions mention crypto."""
        assert "crypto" in mcp.instructions.lower()
