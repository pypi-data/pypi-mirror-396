"""Tests for data generation tools in FinQuant MCP."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from app.storage import PortfolioStore
from app.tools.data import register_data_tools

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
def data_store(cache: RefCache) -> PortfolioStore:
    """Create a PortfolioStore for data tests."""
    return PortfolioStore(cache=cache, namespace="data_test")


@pytest.fixture
def data_tools(
    mock_mcp: MockMCP, data_store: PortfolioStore
) -> dict[str, Callable[..., Any]]:
    """Register data tools and return them."""
    register_data_tools(mock_mcp, data_store)
    return mock_mcp.tools


class TestGeneratePriceSeries:
    """Tests for generate_price_series tool."""

    def test_generates_correct_structure(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that generate_price_series returns correct structure."""
        generate = data_tools["generate_price_series"]
        result = generate(symbols=["AAPL", "GOOG", "MSFT"], days=50, seed=42)

        assert "symbols" in result
        assert "dates" in result
        assert "prices" in result
        assert "parameters" in result

    def test_generates_correct_number_of_days(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that correct number of days is generated."""
        generate = data_tools["generate_price_series"]
        result = generate(symbols=["AAPL"], days=100, seed=42)

        assert len(result["dates"]) == 100
        assert len(result["prices"]["AAPL"]) == 100

    def test_uses_custom_initial_prices(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that custom initial prices are used."""
        generate = data_tools["generate_price_series"]
        result = generate(
            symbols=["AAPL", "GOOG"],
            days=10,
            initial_prices={"AAPL": 150.0, "GOOG": 100.0},
            seed=42,
        )

        # First price should be close to initial (GBM starts there)
        assert abs(result["prices"]["AAPL"][0] - 150.0) < 10
        assert abs(result["prices"]["GOOG"][0] - 100.0) < 10

    def test_reproducible_with_seed(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that same seed produces same results."""
        generate = data_tools["generate_price_series"]

        result1 = generate(symbols=["AAPL"], days=20, seed=42)
        result2 = generate(symbols=["AAPL"], days=20, seed=42)

        assert result1["prices"]["AAPL"] == result2["prices"]["AAPL"]

    def test_different_with_different_seeds(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that different seeds produce different results."""
        generate = data_tools["generate_price_series"]

        result1 = generate(symbols=["AAPL"], days=20, seed=42)
        result2 = generate(symbols=["AAPL"], days=20, seed=123)

        assert result1["prices"]["AAPL"] != result2["prices"]["AAPL"]

    def test_prices_are_positive(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that all generated prices are positive."""
        generate = data_tools["generate_price_series"]
        result = generate(symbols=["AAPL", "GOOG", "MSFT"], days=252, seed=42)

        for symbol in result["symbols"]:
            for price in result["prices"][symbol]:
                assert price > 0

    def test_custom_returns_and_volatilities(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test custom annual returns and volatilities."""
        generate = data_tools["generate_price_series"]
        result = generate(
            symbols=["HIGH", "LOW"],
            days=252,
            annual_returns={"HIGH": 0.20, "LOW": 0.05},
            annual_volatilities={"HIGH": 0.30, "LOW": 0.10},
            seed=42,
        )

        assert "HIGH" in result["prices"]
        assert "LOW" in result["prices"]
        # Both should have correct number of prices
        assert len(result["prices"]["HIGH"]) == 252
        assert len(result["prices"]["LOW"]) == 252


class TestGeneratePortfolioScenarios:
    """Tests for generate_portfolio_scenarios tool."""

    def test_generates_multiple_scenarios(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that multiple scenarios are generated."""
        generate = data_tools["generate_portfolio_scenarios"]
        result = generate(
            base_symbols=["AAPL", "GOOG"],
            num_scenarios=3,
            days=50,
            seed=42,
        )

        assert "scenarios" in result
        assert "summary" in result
        assert len(result["scenarios"]) == 3

    def test_scenario_structure(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that each scenario has correct structure."""
        generate = data_tools["generate_portfolio_scenarios"]
        result = generate(
            base_symbols=["AAPL", "GOOG"],
            num_scenarios=2,
            days=30,
            seed=42,
        )

        for scenario in result["scenarios"]:
            # Scenarios have name and parameters
            assert "name" in scenario
            assert "returns" in scenario
            assert "volatilities" in scenario
            assert "correlation_matrix" in scenario
            # Check symbols are present in returns
            assert "AAPL" in scenario["returns"]
            assert "GOOG" in scenario["returns"]

    def test_custom_return_range(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test custom return range."""
        generate = data_tools["generate_portfolio_scenarios"]
        result = generate(
            base_symbols=["AAPL"],
            num_scenarios=5,
            days=30,
            return_range=[0.05, 0.10],
            seed=42,
        )

        # All scenarios should have returns within specified range
        for scenario in result["scenarios"]:
            for _symbol, ret in scenario["returns"].items():
                assert 0.05 <= ret <= 0.10

    def test_custom_volatility_range(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test custom volatility range."""
        generate = data_tools["generate_portfolio_scenarios"]
        result = generate(
            base_symbols=["AAPL"],
            num_scenarios=5,
            days=30,
            volatility_range=[0.15, 0.25],
            seed=42,
        )

        # All scenarios should have volatilities within specified range
        for scenario in result["scenarios"]:
            for _symbol, vol in scenario["volatilities"].items():
                assert 0.15 <= vol <= 0.25


class TestGetSamplePortfolioData:
    """Tests for get_sample_portfolio_data tool."""

    def test_returns_complete_data(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that sample data includes all required fields."""
        get_sample = data_tools["get_sample_portfolio_data"]
        result = get_sample()

        # Sample data provides template info, not actual prices
        assert "symbols" in result
        assert "name" in result
        assert "description" in result
        assert "suggested_weights" in result
        assert "typical_annual_returns" in result
        assert "typical_annual_volatilities" in result
        assert "typical_correlations" in result
        assert "usage_example" in result

    def test_weights_sum_to_one(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that sample weights sum to 1."""
        get_sample = data_tools["get_sample_portfolio_data"]
        result = get_sample()

        total_weight = sum(result["suggested_weights"].values())
        assert abs(total_weight - 1.0) < 0.01

    def test_symbols_have_parameters(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that all symbols have return and volatility parameters."""
        get_sample = data_tools["get_sample_portfolio_data"]
        result = get_sample()

        for symbol in result["symbols"]:
            assert symbol in result["suggested_weights"]
            assert symbol in result["typical_annual_returns"]
            assert symbol in result["typical_annual_volatilities"]


class TestGetTrendingCoins:
    """Tests for get_trending_coins tool."""

    def test_returns_trending_data(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that trending coins returns data."""
        # Mock the API call to avoid network dependency
        mock_data = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "market_cap_rank": 1,
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "market_cap_rank": 2,
            },
        ]

        with patch("app.tools.data.get_trending_crypto", return_value=mock_data):
            get_trending = data_tools["get_trending_coins"]
            result = get_trending()

            assert "coins" in result
            assert len(result["coins"]) == 2
            assert result["coins"][0]["symbol"] == "btc"


class TestSearchCryptoCoins:
    """Tests for search_crypto_coins tool."""

    def test_search_returns_results(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that search returns results."""
        mock_results = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
            {"id": "bitcoin-cash", "symbol": "bch", "name": "Bitcoin Cash"},
        ]

        with patch("app.tools.data.search_crypto", return_value=mock_results):
            search = data_tools["search_crypto_coins"]
            result = search(query="bitcoin")

            # Actual structure uses "coins" not "results"
            assert "coins" in result
            assert len(result["coins"]) == 2
            assert "count" in result
            assert result["count"] == 2

    def test_search_empty_query(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test search with empty query."""
        search = data_tools["search_crypto_coins"]
        result = search(query="")

        # Empty query returns error
        assert "error" in result


class TestGetCryptoInfo:
    """Tests for get_crypto_info tool."""

    def test_returns_coin_info(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that coin info is returned."""
        mock_info = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 50000.0,
            "market_cap": 1000000000000,
            "price_change_24h": 1000.0,
            "price_change_percentage_24h": 2.0,
        }

        with patch("app.tools.data.get_crypto_coin_info", return_value=mock_info):
            get_info = data_tools["get_crypto_info"]
            result = get_info(symbol="BTC")

            assert "id" in result
            assert result["id"] == "bitcoin"
            assert "current_price" in result

    def test_unknown_symbol_returns_error(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that unknown symbol returns error."""
        # The function raises ValueError for unknown symbols
        with patch(
            "app.tools.data.get_crypto_coin_info",
            side_effect=ValueError("Coin not found"),
        ):
            get_info = data_tools["get_crypto_info"]
            result = get_info(symbol="UNKNOWNCOIN")

            assert "error" in result
            assert "suggestion" in result


class TestListCryptoSymbols:
    """Tests for list_crypto_symbols tool."""

    def test_returns_symbol_list(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that symbol list is returned."""
        mock_symbols = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
        }

        with patch(
            "app.tools.data.list_supported_crypto_symbols",
            return_value=mock_symbols,
        ):
            list_symbols = data_tools["list_crypto_symbols"]
            result = list_symbols()

            assert "symbols" in result
            assert len(result["symbols"]) == 3

    def test_symbols_have_mappings(
        self,
        data_tools: dict[str, Callable[..., Any]],
    ) -> None:
        """Test that symbols have CoinGecko ID mappings."""
        mock_symbols = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
        }

        with patch(
            "app.tools.data.list_supported_crypto_symbols",
            return_value=mock_symbols,
        ):
            list_symbols = data_tools["list_crypto_symbols"]
            result = list_symbols()

            assert "BTC" in result["symbols"]
            assert result["symbols"]["BTC"] == "bitcoin"
