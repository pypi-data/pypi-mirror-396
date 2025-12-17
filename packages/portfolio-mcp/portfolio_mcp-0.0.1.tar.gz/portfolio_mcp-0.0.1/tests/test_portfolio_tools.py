"""Tests for portfolio CRUD tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.storage import PortfolioStore


class TestCreatePortfolio:
    """Tests for create_portfolio tool."""

    def test_create_with_synthetic_data(self, store: PortfolioStore) -> None:
        """Should create a portfolio with generated synthetic data."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        # Get the tool function
        create_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "create_portfolio":
                create_portfolio = tool.fn
                break

        assert create_portfolio is not None

        result = create_portfolio(
            name="test_synthetic",
            symbols=["AAPL", "GOOG", "AMZN"],
            days=100,
            seed=42,
        )

        assert "error" not in result
        assert result["name"] == "test_synthetic"
        # ref_id format is "cache_name:hash", not "namespace:key"
        assert "ref_id" in result
        assert ":" in result["ref_id"]
        assert result["symbols"] == ["AAPL", "GOOG", "AMZN"]
        assert "metrics" in result
        assert "expected_return" in result["metrics"]
        assert "volatility" in result["metrics"]
        assert "sharpe_ratio" in result["metrics"]

    def test_create_with_provided_data(
        self,
        store: PortfolioStore,
        sample_prices: dict[str, list[float]],
        sample_dates: list[str],
        sample_weights: dict[str, float],
    ) -> None:
        """Should create a portfolio with provided price data."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        create_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "create_portfolio":
                create_portfolio = tool.fn
                break

        result = create_portfolio(
            name="test_provided",
            symbols=list(sample_prices.keys()),
            prices=sample_prices,
            dates=sample_dates,
            weights=sample_weights,
        )

        assert "error" not in result
        assert result["name"] == "test_provided"
        assert result["weights"] == sample_weights
        assert result["num_days"] == len(sample_dates)

    def test_create_duplicate_fails(self, store: PortfolioStore) -> None:
        """Should fail when creating a portfolio with existing name."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        create_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "create_portfolio":
                create_portfolio = tool.fn
                break

        # Create first
        create_portfolio(
            name="duplicate_test",
            symbols=["AAPL"],
            days=50,
            seed=42,
        )

        # Try to create duplicate
        result = create_portfolio(
            name="duplicate_test",
            symbols=["AAPL"],
            days=50,
            seed=42,
        )

        assert "error" in result
        assert "already exists" in result["error"]

    def test_create_with_invalid_weights(self, store: PortfolioStore) -> None:
        """Should fail when weights don't sum to 1.0."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        create_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "create_portfolio":
                create_portfolio = tool.fn
                break

        result = create_portfolio(
            name="invalid_weights",
            symbols=["AAPL", "GOOG"],
            weights={"AAPL": 0.3, "GOOG": 0.3},  # Sum = 0.6
            days=50,
        )

        assert "error" in result
        assert "sum to 1.0" in result["error"]


class TestGetPortfolio:
    """Tests for get_portfolio tool."""

    def test_get_existing_portfolio(
        self, store: PortfolioStore, stored_portfolio: tuple[str, str]
    ) -> None:
        """Should retrieve an existing portfolio."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        get_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "get_portfolio":
                get_portfolio = tool.fn
                break

        name, _ = stored_portfolio
        result = get_portfolio(name=name)

        assert "error" not in result
        assert result["name"] == name
        assert "metrics" in result
        assert "symbols" in result

    def test_get_nonexistent_portfolio(self, store: PortfolioStore) -> None:
        """Should return error for non-existent portfolio."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        get_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "get_portfolio":
                get_portfolio = tool.fn
                break

        result = get_portfolio(name="nonexistent")

        assert "error" in result
        assert "not found" in result["error"]


class TestListPortfolios:
    """Tests for list_portfolios tool."""

    def test_list_empty(self, store: PortfolioStore) -> None:
        """Should return empty list when no portfolios exist."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        list_portfolios = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "list_portfolios":
                list_portfolios = tool.fn
                break

        result = list_portfolios()

        assert result["count"] == 0
        assert result["portfolios"] == []

    def test_list_multiple(
        self, store: PortfolioStore, stored_portfolio: tuple[str, str]
    ) -> None:
        """Should list all stored portfolios."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        list_portfolios = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "list_portfolios":
                list_portfolios = tool.fn
                break

        result = list_portfolios()

        assert result["count"] >= 1
        names = [p["name"] for p in result["portfolios"]]
        name, _ = stored_portfolio
        assert name in names


class TestDeletePortfolio:
    """Tests for delete_portfolio tool."""

    def test_delete_existing(
        self, store: PortfolioStore, stored_portfolio: tuple[str, str]
    ) -> None:
        """Should delete an existing portfolio."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        delete_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "delete_portfolio":
                delete_portfolio = tool.fn
                break

        name, _ = stored_portfolio
        result = delete_portfolio(name=name)

        assert result["deleted"] is True
        assert result["name"] == name

        # Verify it's gone
        assert not store.exists(name)

    def test_delete_nonexistent(self, store: PortfolioStore) -> None:
        """Should return error when deleting non-existent portfolio."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        delete_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "delete_portfolio":
                delete_portfolio = tool.fn
                break

        result = delete_portfolio(name="nonexistent")

        assert result["deleted"] is False
        assert "error" in result


class TestUpdatePortfolioWeights:
    """Tests for update_portfolio_weights tool."""

    def test_update_weights(
        self, store: PortfolioStore, stored_portfolio: tuple[str, str]
    ) -> None:
        """Should update weights and recalculate metrics."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        update_portfolio_weights = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "update_portfolio_weights":
                update_portfolio_weights = tool.fn
                break

        name, _ = stored_portfolio

        # Get original data to know the symbols
        original = store.get(name)
        symbols = original["prices"]["columns"]

        # Create new weights (equal distribution)
        new_weights = {s: 1.0 / len(symbols) for s in symbols}

        result = update_portfolio_weights(name=name, weights=new_weights)

        assert "error" not in result
        assert result["new_weights"] == new_weights
        assert "metrics" in result


class TestClonePortfolio:
    """Tests for clone_portfolio tool."""

    def test_clone_same_weights(
        self, store: PortfolioStore, stored_portfolio: tuple[str, str]
    ) -> None:
        """Should clone a portfolio with same weights."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        clone_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "clone_portfolio":
                clone_portfolio = tool.fn
                break

        source_name, _ = stored_portfolio
        result = clone_portfolio(source_name=source_name, new_name="cloned_portfolio")

        assert "error" not in result
        assert result["name"] == "cloned_portfolio"
        assert store.exists("cloned_portfolio")

    def test_clone_with_new_weights(
        self, store: PortfolioStore, stored_portfolio: tuple[str, str]
    ) -> None:
        """Should clone a portfolio with different weights."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        clone_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "clone_portfolio":
                clone_portfolio = tool.fn
                break

        source_name, _ = stored_portfolio

        # Get symbols from source
        original = store.get(source_name)
        symbols = original["prices"]["columns"]

        # Create new weights
        new_weights = {s: 1.0 / len(symbols) for s in symbols}

        result = clone_portfolio(
            source_name=source_name,
            new_name="cloned_different",
            new_weights=new_weights,
        )

        assert "error" not in result
        assert result["name"] == "cloned_different"
        assert result["weights"] == new_weights

    def test_clone_nonexistent_source(self, store: PortfolioStore) -> None:
        """Should return error when source doesn't exist."""
        from fastmcp import FastMCP

        from app.tools.portfolio import register_portfolio_tools

        mcp = FastMCP(name="test")
        register_portfolio_tools(mcp, store)

        clone_portfolio = None
        for tool in mcp._tool_manager._tools.values():
            if tool.name == "clone_portfolio":
                clone_portfolio = tool.fn
                break

        result = clone_portfolio(source_name="nonexistent", new_name="clone")

        assert "error" in result
        assert "not found" in result["error"]
