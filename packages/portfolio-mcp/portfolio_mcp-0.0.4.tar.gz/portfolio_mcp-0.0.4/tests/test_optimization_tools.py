"""Tests for optimization tools in FinQuant MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import pytest
from finquant.portfolio import build_portfolio

from app.storage import PortfolioStore
from app.tools.optimization import register_optimization_tools
from tests.conftest import unwrap_cached

if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp_refcache import RefCache


class MockMCP:
    """Mock FastMCP for testing tool registration."""

    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}

    def tool(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Register a tool function."""
        self.tools[func.__name__] = func
        return func


@pytest.fixture
def mock_mcp() -> MockMCP:
    """Create a mock MCP instance."""
    return MockMCP()


@pytest.fixture
def optimization_store(cache: RefCache) -> PortfolioStore:
    """Create a PortfolioStore for optimization tests."""
    return PortfolioStore(cache=cache, namespace="optimization_test")


@pytest.fixture
def optimization_tools_with_cache(
    mock_mcp: MockMCP, optimization_store: PortfolioStore, cache: RefCache
) -> tuple[dict[str, Callable[..., Any]], RefCache]:
    """Register optimization tools and return them with cache."""
    register_optimization_tools(mock_mcp, optimization_store, cache)
    return mock_mcp.tools, cache


@pytest.fixture
def optimization_tools(
    optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
) -> dict[str, Callable[..., Any]]:
    """Register optimization tools and return them."""
    tools, _ = optimization_tools_with_cache
    return tools


@pytest.fixture
def stored_optimization_portfolio(
    optimization_store: PortfolioStore,
    sample_prices: dict[str, list[float]],
    sample_dates: list[str],
    sample_weights: dict[str, float],
) -> str:
    """Create and store a portfolio for optimization tests."""
    date_index = pd.to_datetime(sample_dates)
    prices_df = pd.DataFrame(sample_prices, index=date_index).astype(np.float64)

    symbols = list(sample_prices.keys())
    allocation_data = []
    for symbol in symbols:
        allocation_data.append(
            {
                "Allocation": np.float64(sample_weights[symbol] * 100),
                "Name": symbol,
            }
        )
    allocation_df = pd.DataFrame(allocation_data)
    allocation_df["Allocation"] = allocation_df["Allocation"].astype(np.float64)

    portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
    portfolio.risk_free_rate = 0.02

    name = "optimization_test_portfolio"
    optimization_store.store(portfolio, name)
    return name


class TestOptimizePortfolio:
    """Tests for optimize_portfolio tool."""

    def test_max_sharpe_optimization(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test max Sharpe ratio optimization."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(name=stored_optimization_portfolio, method="max_sharpe")
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert "method" in result
        assert result["method"] == "max_sharpe"
        assert "optimal_weights" in result
        assert "expected_return" in result
        assert "volatility" in result
        assert "sharpe_ratio" in result
        assert "original" in result

    def test_min_volatility_optimization(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test minimum volatility optimization."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(
            name=stored_optimization_portfolio, method="min_volatility"
        )
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert result["method"] == "min_volatility"
        assert "optimal_weights" in result
        assert "volatility" in result

    def test_efficient_return_optimization(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test efficient return optimization with target return."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(
            name=stored_optimization_portfolio,
            method="efficient_return",
            target_return=0.15,
        )
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert result["method"] == "efficient_return"
        assert result["target"]["return"] == 0.15
        assert "optimal_weights" in result

    def test_efficient_return_requires_target(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that efficient_return requires target_return parameter."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(
            name=stored_optimization_portfolio, method="efficient_return"
        )
        result = unwrap_cached(raw_result, cache)

        assert "error" in result
        assert "target_return" in result["error"]

    def test_efficient_volatility_optimization(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test efficient volatility optimization with target volatility."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(
            name=stored_optimization_portfolio,
            method="efficient_volatility",
            target_volatility=0.10,
        )
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert result["method"] == "efficient_volatility"
        assert result["target"]["volatility"] == 0.10
        assert "optimal_weights" in result

    def test_efficient_volatility_requires_target(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that efficient_volatility requires target_volatility."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(
            name=stored_optimization_portfolio, method="efficient_volatility"
        )
        result = unwrap_cached(raw_result, cache)

        assert "error" in result
        assert "target_volatility" in result["error"]

    def test_invalid_method(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that invalid method returns error."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(
            name=stored_optimization_portfolio, method="invalid_method"
        )
        result = unwrap_cached(raw_result, cache)

        assert "error" in result
        assert "valid_methods" in result

    def test_optimal_weights_sum_to_one(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that optimal weights sum to 1."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(name=stored_optimization_portfolio, method="max_sharpe")
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        total_weight = sum(result["optimal_weights"].values())
        assert abs(total_weight - 1.0) < 0.01

    def test_nonexistent_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = optimization_tools_with_cache
        optimize = tools["optimize_portfolio"]
        raw_result = optimize(name="nonexistent", method="max_sharpe")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result


class TestRunMonteCarlo:
    """Tests for run_monte_carlo tool."""

    def test_monte_carlo_returns_expected_fields(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test Monte Carlo simulation returns expected fields."""
        tools, cache = optimization_tools_with_cache
        monte_carlo = tools["run_monte_carlo"]
        raw_result = monte_carlo(name=stored_optimization_portfolio, num_trials=100)
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert "num_trials" in result
        assert "min_volatility_portfolio" in result
        assert "max_sharpe_portfolio" in result
        assert "simulation_stats" in result

    def test_monte_carlo_min_volatility_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test min volatility portfolio from Monte Carlo."""
        tools, cache = optimization_tools_with_cache
        monte_carlo = tools["run_monte_carlo"]
        raw_result = monte_carlo(name=stored_optimization_portfolio, num_trials=100)
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        min_vol = result["min_volatility_portfolio"]
        assert "weights" in min_vol
        assert "expected_return" in min_vol
        assert "volatility" in min_vol
        assert "sharpe_ratio" in min_vol

    def test_monte_carlo_max_sharpe_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test max Sharpe portfolio from Monte Carlo."""
        tools, cache = optimization_tools_with_cache
        monte_carlo = tools["run_monte_carlo"]
        raw_result = monte_carlo(name=stored_optimization_portfolio, num_trials=100)
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        max_sharpe = result["max_sharpe_portfolio"]
        assert "weights" in max_sharpe
        assert "sharpe_ratio" in max_sharpe

    def test_monte_carlo_weights_sum_to_one(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that Monte Carlo weights sum to 1."""
        tools, cache = optimization_tools_with_cache
        monte_carlo = tools["run_monte_carlo"]
        raw_result = monte_carlo(name=stored_optimization_portfolio, num_trials=100)
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        min_vol_weights = result["min_volatility_portfolio"]["weights"]
        total_weight = sum(min_vol_weights.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_nonexistent_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = optimization_tools_with_cache
        run_mc = tools["run_monte_carlo"]
        raw_result = run_mc(name="nonexistent")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result


class TestGetEfficientFrontier:
    """Tests for get_efficient_frontier tool."""

    def test_returns_frontier_points(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that efficient frontier returns points."""
        tools, cache = optimization_tools_with_cache
        get_ef = tools["get_efficient_frontier"]
        raw_result = get_ef(name=stored_optimization_portfolio, num_points=20)
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert "frontier_points" in result
        assert len(result["frontier_points"]) == 20

    def test_frontier_points_structure(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that each frontier point has correct structure."""
        tools, cache = optimization_tools_with_cache
        get_ef = tools["get_efficient_frontier"]
        raw_result = get_ef(name=stored_optimization_portfolio, num_points=10)
        result = unwrap_cached(raw_result, cache)

        for point in result["frontier_points"]:
            assert "volatility" in point
            assert "expected_return" in point
            assert "sharpe_ratio" in point

    def test_optimal_sharpe_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that optimal Sharpe portfolio is included."""
        tools, cache = optimization_tools_with_cache
        get_ef = tools["get_efficient_frontier"]
        raw_result = get_ef(name=stored_optimization_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "optimal_sharpe" in result
        opt = result["optimal_sharpe"]
        assert "weights" in opt
        assert "sharpe_ratio" in opt
        assert "expected_return" in opt

    def test_min_volatility_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that min volatility portfolio is included."""
        tools, cache = optimization_tools_with_cache
        get_ef = tools["get_efficient_frontier"]
        raw_result = get_ef(name=stored_optimization_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "optimal_min_volatility" in result
        min_vol = result["optimal_min_volatility"]
        assert "weights" in min_vol
        assert "volatility" in min_vol

    def test_individual_stocks(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test that individual stock positions are included."""
        tools, cache = optimization_tools_with_cache
        get_ef = tools["get_efficient_frontier"]
        raw_result = get_ef(name=stored_optimization_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "individual_stocks" in result
        stocks = result["individual_stocks"]
        assert len(stocks) > 0

    def test_current_portfolio_position(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_optimization_portfolio: str,
    ) -> None:
        """Test current portfolio position is included."""
        tools, cache = optimization_tools_with_cache
        get_ef = tools["get_efficient_frontier"]
        raw_result = get_ef(name=stored_optimization_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert "current_portfolio" in result
        current = result["current_portfolio"]
        assert "weights" in current
        assert "expected_return" in current
        assert "volatility" in current

    def test_nonexistent_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = optimization_tools_with_cache
        get_ef = tools["get_efficient_frontier"]
        raw_result = get_ef(name="nonexistent")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result


class TestApplyOptimization:
    """Tests for apply_optimization tool."""

    def test_apply_max_sharpe(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        optimization_store: PortfolioStore,
        sample_prices: dict[str, list[float]],
        sample_dates: list[str],
        sample_weights: dict[str, float],
    ) -> None:
        """Test applying max Sharpe optimization."""
        tools, cache = optimization_tools_with_cache
        # Create a fresh portfolio for this test
        date_index = pd.to_datetime(sample_dates)
        prices_df = pd.DataFrame(sample_prices, index=date_index).astype(np.float64)

        symbols = list(sample_prices.keys())
        allocation_data = []
        for symbol in symbols:
            allocation_data.append(
                {
                    "Allocation": np.float64(sample_weights[symbol] * 100),
                    "Name": symbol,
                }
            )
        allocation_df = pd.DataFrame(allocation_data)
        allocation_df["Allocation"] = allocation_df["Allocation"].astype(np.float64)

        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = 0.02

        name = "apply_optimization_test"
        optimization_store.store(portfolio, name)

        apply_opt = tools["apply_optimization"]
        raw_result = apply_opt(name=name, method="max_sharpe")
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        assert "new_weights" in result
        assert "new_metrics" in result
        assert "old_metrics" in result

    def test_apply_updates_stored_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        optimization_store: PortfolioStore,
        sample_prices: dict[str, list[float]],
        sample_dates: list[str],
        sample_weights: dict[str, float],
    ) -> None:
        """Test that apply_optimization updates the stored portfolio."""
        tools, cache = optimization_tools_with_cache
        # Create a fresh portfolio for this test
        date_index = pd.to_datetime(sample_dates)
        prices_df = pd.DataFrame(sample_prices, index=date_index).astype(np.float64)

        symbols = list(sample_prices.keys())
        allocation_data = []
        for symbol in symbols:
            allocation_data.append(
                {
                    "Allocation": np.float64(sample_weights[symbol] * 100),
                    "Name": symbol,
                }
            )
        allocation_df = pd.DataFrame(allocation_data)
        allocation_df["Allocation"] = allocation_df["Allocation"].astype(np.float64)

        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = 0.02

        name = "apply_update_test"
        optimization_store.store(portfolio, name)

        # Get original metrics
        original_data = optimization_store.get(name)
        original_sharpe = original_data["metrics"]["sharpe"]

        # Apply optimization
        apply_opt = tools["apply_optimization"]
        raw_result = apply_opt(name=name, method="max_sharpe")
        result = unwrap_cached(raw_result, cache)

        assert "error" not in result
        # Verify stored portfolio was updated
        updated_data = optimization_store.get(name)
        new_sharpe = updated_data["metrics"]["sharpe"]

        # Optimized Sharpe should be >= original
        assert new_sharpe >= original_sharpe - 0.01

    def test_nonexistent_portfolio(
        self,
        optimization_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = optimization_tools_with_cache
        apply_opt = tools["apply_optimization"]
        raw_result = apply_opt(name="nonexistent", method="max_sharpe")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result
