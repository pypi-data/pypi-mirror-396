"""Tests for analysis tools in FinQuant MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import pytest
from finquant.portfolio import build_portfolio

from app.storage import PortfolioStore
from app.tools.analysis import register_analysis_tools
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
def analysis_store(cache: RefCache) -> PortfolioStore:
    """Create a PortfolioStore for analysis tests."""
    return PortfolioStore(cache=cache, namespace="analysis_test")


@pytest.fixture
def analysis_tools_with_cache(
    mock_mcp: MockMCP, analysis_store: PortfolioStore, cache: RefCache
) -> tuple[dict[str, Callable[..., Any]], RefCache]:
    """Register analysis tools and return them with cache for resolution."""
    register_analysis_tools(mock_mcp, analysis_store, cache)
    return mock_mcp.tools, cache


@pytest.fixture
def analysis_tools(
    analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
) -> dict[str, Callable[..., Any]]:
    """Register analysis tools and return them."""
    tools, _ = analysis_tools_with_cache
    return tools


@pytest.fixture
def stored_analysis_portfolio(
    analysis_store: PortfolioStore,
    sample_prices: dict[str, list[float]],
    sample_dates: list[str],
    sample_weights: dict[str, float],
) -> str:
    """Create and store a portfolio for analysis tests."""
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

    name = "analysis_test_portfolio"
    analysis_store.store(portfolio, name)
    return name


class TestGetPortfolioMetrics:
    """Tests for get_portfolio_metrics tool."""

    def test_returns_all_expected_metrics(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], Any],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that metrics include all expected fields."""
        tools, cache = analysis_tools_with_cache
        get_metrics = tools["get_portfolio_metrics"]
        raw_result = get_metrics(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache=cache)

        assert "portfolio_name" in result
        assert result["portfolio_name"] == stored_analysis_portfolio
        assert "expected_return" in result
        assert "volatility" in result
        assert "sharpe_ratio" in result
        assert "sortino_ratio" in result
        assert "value_at_risk" in result
        assert "downside_risk" in result
        assert "skewness" in result
        assert "kurtosis" in result
        assert "settings" in result

    def test_metrics_have_reasonable_values(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], Any],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that metrics are within reasonable bounds."""
        tools, cache = analysis_tools_with_cache
        get_metrics = tools["get_portfolio_metrics"]
        raw_result = get_metrics(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache=cache)

        # Expected return should be a reasonable annual return
        assert -1.0 <= result["expected_return"] <= 5.0

        # Volatility should be positive
        assert result["volatility"] > 0

        # Sharpe ratio should be a reasonable value
        assert -10.0 <= result["sharpe_ratio"] <= 10.0

    def test_nonexistent_portfolio_returns_error(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that querying nonexistent portfolio returns error."""
        tools, cache = analysis_tools_with_cache
        get_metrics = tools["get_portfolio_metrics"]
        raw_result = get_metrics(name="nonexistent_portfolio")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result
        assert "nonexistent_portfolio" in result["error"]
        assert "suggestion" in result


class TestGetReturns:
    """Tests for get_returns tool."""

    def test_daily_returns(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test getting daily returns."""
        tools, cache = analysis_tools_with_cache
        get_returns = tools["get_returns"]
        raw_result = get_returns(name=stored_analysis_portfolio, return_type="daily")
        result = unwrap_cached(raw_result, cache)

        assert "return_type" in result
        assert result["return_type"] == "daily"
        assert "dates" in result
        assert "returns" in result
        assert "portfolio_returns" in result
        assert "statistics" in result

    def test_log_returns(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test getting log returns."""
        tools, cache = analysis_tools_with_cache
        get_returns = tools["get_returns"]
        raw_result = get_returns(name=stored_analysis_portfolio, return_type="log")
        result = unwrap_cached(raw_result, cache)

        assert result["return_type"] == "log"
        assert "returns" in result

    def test_cumulative_returns(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test getting cumulative returns."""
        tools, cache = analysis_tools_with_cache
        get_returns = tools["get_returns"]
        raw_result = get_returns(
            name=stored_analysis_portfolio, return_type="cumulative"
        )
        result = unwrap_cached(raw_result, cache)

        assert result["return_type"] == "cumulative"
        assert "returns" in result
        # Cumulative returns start at 0 or near 0
        assert "portfolio_returns" in result
        assert len(result["portfolio_returns"]) > 0

    def test_percentage_formatting(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test percentage formatting option."""
        tools, cache = analysis_tools_with_cache
        get_returns = tools["get_returns"]

        # With percentage (default)
        raw_result_pct = get_returns(
            name=stored_analysis_portfolio, return_type="daily", as_percentage=True
        )
        result_pct = unwrap_cached(raw_result_pct, cache)

        # Without percentage
        raw_result_raw = get_returns(
            name=stored_analysis_portfolio, return_type="daily", as_percentage=False
        )
        result_raw = unwrap_cached(raw_result_raw, cache)

        # Both should have data
        assert "statistics" in result_pct
        assert "statistics" in result_raw

    def test_invalid_return_type(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that invalid return type is handled."""
        tools, cache = analysis_tools_with_cache
        get_returns = tools["get_returns"]
        raw_result = get_returns(name=stored_analysis_portfolio, return_type="invalid")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result
        assert "valid_types" in result

    def test_nonexistent_portfolio(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = analysis_tools_with_cache
        get_returns = tools["get_returns"]
        raw_result = get_returns(name="nonexistent", return_type="daily")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result


class TestGetCorrelationMatrix:
    """Tests for get_correlation_matrix tool."""

    def test_returns_correlation_data(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that correlation matrix is returned."""
        tools, cache = analysis_tools_with_cache
        get_correlation = tools["get_correlation_matrix"]
        raw_result = get_correlation(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "symbols" in result
        assert "correlation_matrix" in result
        assert "correlations" in result

    def test_correlation_matrix_shape(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test correlation matrix has correct shape."""
        tools, cache = analysis_tools_with_cache
        get_correlation = tools["get_correlation_matrix"]
        raw_result = get_correlation(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        symbols = result["symbols"]
        matrix = result["correlation_matrix"]

        # Square matrix
        assert len(matrix) == len(symbols)
        for row in matrix:
            assert len(row) == len(symbols)

    def test_correlation_diagonal_is_one(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that diagonal of correlation matrix is 1."""
        tools, cache = analysis_tools_with_cache
        get_correlation = tools["get_correlation_matrix"]
        raw_result = get_correlation(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        matrix = result["correlation_matrix"]
        for index in range(len(matrix)):
            assert abs(matrix[index][index] - 1.0) < 1e-10

    def test_correlation_values_in_range(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that correlations are between -1 and 1."""
        tools, cache = analysis_tools_with_cache
        get_correlation = tools["get_correlation_matrix"]
        raw_result = get_correlation(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        matrix = result["correlation_matrix"]
        for row in matrix:
            for value in row:
                assert -1.0 <= value <= 1.0

    def test_nonexistent_portfolio(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = analysis_tools_with_cache
        get_correlation = tools["get_correlation_matrix"]
        raw_result = get_correlation(name="nonexistent")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result


class TestGetCovarianceMatrix:
    """Tests for get_covariance_matrix tool."""

    def test_returns_covariance_data(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that covariance matrix is returned."""
        tools, cache = analysis_tools_with_cache
        get_covariance = tools["get_covariance_matrix"]
        raw_result = get_covariance(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "symbols" in result
        assert "covariance_matrix" in result
        assert "variances" in result

    def test_covariance_matrix_shape(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test covariance matrix has correct shape."""
        tools, cache = analysis_tools_with_cache
        get_covariance = tools["get_covariance_matrix"]
        raw_result = get_covariance(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        symbols = result["symbols"]
        matrix = result["covariance_matrix"]

        assert len(matrix) == len(symbols)
        for row in matrix:
            assert len(row) == len(symbols)

    def test_variances_are_positive(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that variances are positive."""
        tools, cache = analysis_tools_with_cache
        get_covariance = tools["get_covariance_matrix"]
        raw_result = get_covariance(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        for symbol, variance in result["variances"].items():
            assert variance > 0, f"Variance for {symbol} should be positive"

    def test_annualized_vs_raw(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test annualized vs raw covariance."""
        tools, cache = analysis_tools_with_cache
        get_covariance = tools["get_covariance_matrix"]

        raw_result_ann = get_covariance(name=stored_analysis_portfolio, annualized=True)
        result_ann = unwrap_cached(raw_result_ann, cache)

        raw_result_raw = get_covariance(
            name=stored_analysis_portfolio, annualized=False
        )
        result_raw = unwrap_cached(raw_result_raw, cache)

        # Annualized should be larger by factor of ~252
        symbols = result_ann["symbols"]
        if len(symbols) > 0:
            annual_var = result_ann["variances"][symbols[0]]
            raw_var = result_raw["variances"][symbols[0]]
            # Allow some tolerance
            ratio = annual_var / raw_var if raw_var > 0 else 0
            assert 200 < ratio < 300, "Annualization should multiply by ~252"

    def test_nonexistent_portfolio(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = analysis_tools_with_cache
        get_covariance = tools["get_covariance_matrix"]
        raw_result = get_covariance(name="nonexistent")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result


class TestComparePortfolios:
    """Tests for compare_portfolios tool."""

    @pytest.fixture
    def second_portfolio(
        self,
        analysis_store: PortfolioStore,
        sample_prices: dict[str, list[float]],
        sample_dates: list[str],
    ) -> str:
        """Create a second portfolio with different weights."""
        date_index = pd.to_datetime(sample_dates)
        prices_df = pd.DataFrame(sample_prices, index=date_index).astype(np.float64)

        # Different weights
        symbols = list(sample_prices.keys())
        weights = {symbols[0]: 0.6, symbols[1]: 0.3, symbols[2]: 0.1}
        allocation_data = []
        for symbol in symbols:
            allocation_data.append(
                {
                    "Allocation": np.float64(weights[symbol] * 100),
                    "Name": symbol,
                }
            )
        allocation_df = pd.DataFrame(allocation_data)
        allocation_df["Allocation"] = allocation_df["Allocation"].astype(np.float64)

        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = 0.02

        name = "second_test_portfolio"
        analysis_store.store(portfolio, name)
        return name

    def test_compare_two_portfolios(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
        second_portfolio: str,
    ) -> None:
        """Test comparing two portfolios."""
        tools, cache = analysis_tools_with_cache
        compare = tools["compare_portfolios"]
        raw_result = compare(names=[stored_analysis_portfolio, second_portfolio])
        result = unwrap_cached(raw_result, cache)

        assert "portfolios" in result
        assert "rankings" in result
        assert "best_by_metric" in result

        # Both portfolios should be in results
        assert stored_analysis_portfolio in result["portfolios"]
        assert second_portfolio in result["portfolios"]

    def test_compare_includes_metrics(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
        second_portfolio: str,
    ) -> None:
        """Test that comparison includes relevant metrics."""
        tools, cache = analysis_tools_with_cache
        compare = tools["compare_portfolios"]
        raw_result = compare(names=[stored_analysis_portfolio, second_portfolio])
        result = unwrap_cached(raw_result, cache)

        for _portfolio_name, metrics in result["portfolios"].items():
            assert "expected_return" in metrics
            assert "volatility" in metrics
            assert "sharpe_ratio" in metrics

    def test_compare_with_missing_portfolio(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test comparing with a missing portfolio."""
        tools, cache = analysis_tools_with_cache
        compare = tools["compare_portfolios"]
        raw_result = compare(names=[stored_analysis_portfolio, "nonexistent"])
        result = unwrap_cached(raw_result, cache)

        # Should still work for existing portfolio or return error
        # Implementation may vary
        assert "portfolios" in result or "error" in result

    def test_compare_empty_list(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test comparing empty list."""
        tools, cache = analysis_tools_with_cache
        compare = tools["compare_portfolios"]
        raw_result = compare(names=[])
        result = unwrap_cached(raw_result, cache)

        assert "error" in result or len(result.get("portfolios", {})) == 0


class TestGetIndividualStockMetrics:
    """Tests for get_individual_stock_metrics tool."""

    def test_returns_metrics_per_stock(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that metrics are returned for each stock."""
        tools, cache = analysis_tools_with_cache
        get_metrics = tools["get_individual_stock_metrics"]
        raw_result = get_metrics(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "stocks" in result

        # Check each stock has expected metrics
        for _symbol, metrics in result["stocks"].items():
            assert "mean_return" in metrics
            assert "volatility" in metrics
            assert "sharpe_ratio" in metrics
            assert "weight" in metrics

    def test_weights_sum_to_one(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that weights sum to approximately 1."""
        tools, cache = analysis_tools_with_cache
        get_metrics = tools["get_individual_stock_metrics"]
        raw_result = get_metrics(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        total_weight = sum(metrics["weight"] for metrics in result["stocks"].values())
        assert abs(total_weight - 1.0) < 0.01

    def test_nonexistent_portfolio(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = analysis_tools_with_cache
        get_metrics = tools["get_individual_stock_metrics"]
        raw_result = get_metrics(name="nonexistent")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result


class TestGetDrawdownAnalysis:
    """Tests for get_drawdown_analysis tool."""

    def test_returns_drawdown_metrics(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that drawdown analysis returns expected fields."""
        tools, cache = analysis_tools_with_cache
        get_drawdown = tools["get_drawdown_analysis"]
        raw_result = get_drawdown(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        assert "max_drawdown" in result
        assert "max_drawdown_period" in result
        assert "current_drawdown" in result
        assert "recovery_needed" in result

    def test_max_drawdown_is_negative_or_zero(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that max drawdown is negative or zero."""
        tools, cache = analysis_tools_with_cache
        get_drawdown = tools["get_drawdown_analysis"]
        raw_result = get_drawdown(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        # Max drawdown should be <= 0 (represents a loss)
        assert result["max_drawdown"] <= 0

    def test_recovery_needed_is_positive(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
        stored_analysis_portfolio: str,
    ) -> None:
        """Test that recovery needed is positive when there's a drawdown."""
        tools, cache = analysis_tools_with_cache
        get_drawdown = tools["get_drawdown_analysis"]
        raw_result = get_drawdown(name=stored_analysis_portfolio)
        result = unwrap_cached(raw_result, cache)

        # If there's a drawdown, recovery needed should be positive
        if result["current_drawdown"] < 0:
            assert result["recovery_needed"] > 0

    def test_nonexistent_portfolio(
        self,
        analysis_tools_with_cache: tuple[dict[str, Callable[..., Any]], RefCache],
    ) -> None:
        """Test that nonexistent portfolio returns error."""
        tools, cache = analysis_tools_with_cache
        get_drawdown = tools["get_drawdown_analysis"]
        raw_result = get_drawdown(name="nonexistent")
        result = unwrap_cached(raw_result, cache)

        assert "error" in result
