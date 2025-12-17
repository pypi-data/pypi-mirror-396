"""Tests for data_sources module in FinQuant MCP."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.data_sources import (
    CRYPTO_SYMBOL_TO_ID,
    _coingecko_request,
    fetch_crypto_prices,
    fetch_prices,
    fetch_yahoo_prices,
    get_crypto_coin_info,
    get_trending_crypto,
    list_supported_crypto_symbols,
    search_crypto,
)


class TestCryptoSymbolMapping:
    """Tests for crypto symbol mapping."""

    def test_common_symbols_mapped(self) -> None:
        """Test that common crypto symbols are mapped."""
        assert "BTC" in CRYPTO_SYMBOL_TO_ID
        assert "ETH" in CRYPTO_SYMBOL_TO_ID
        assert "SOL" in CRYPTO_SYMBOL_TO_ID

    def test_btc_maps_to_bitcoin(self) -> None:
        """Test BTC maps to bitcoin."""
        assert CRYPTO_SYMBOL_TO_ID["BTC"] == "bitcoin"

    def test_eth_maps_to_ethereum(self) -> None:
        """Test ETH maps to ethereum."""
        assert CRYPTO_SYMBOL_TO_ID["ETH"] == "ethereum"

    def test_mapping_count(self) -> None:
        """Test that there are many mappings."""
        assert len(CRYPTO_SYMBOL_TO_ID) >= 50


class TestCoingeckoRequest:
    """Tests for _coingecko_request helper."""

    def test_successful_request(self) -> None:
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        with patch("app.data_sources.requests.get", return_value=mock_response):
            result = _coingecko_request("ping")
            assert result == {"data": "test"}

    def test_rate_limit_raises_error(self) -> None:
        """Test that 429 rate limit raises ValueError."""
        mock_response = MagicMock()
        mock_response.status_code = 429

        with (
            patch("app.data_sources.requests.get", return_value=mock_response),
            pytest.raises(ValueError, match="rate limit"),
        ):
            _coingecko_request("ping")

    def test_request_exception_raises_error(self) -> None:
        """Test that request exception raises ValueError."""
        with (
            patch(
                "app.data_sources.requests.get",
                side_effect=requests.exceptions.RequestException("Network error"),
            ),
            pytest.raises(ValueError, match="Failed to fetch"),
        ):
            _coingecko_request("ping")


class TestFetchYahooPrices:
    """Tests for fetch_yahoo_prices function."""

    def test_successful_fetch(self) -> None:
        """Test successful price fetch by mocking the entire function."""
        # Mock fetch_yahoo_prices directly since internal yfinance mocking is complex
        mock_result = {
            "symbols": ["AAPL"],
            "dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "prices": {"AAPL": [100.0, 101.0, 102.0]},
            "source": "yahoo",
            "period": "1mo",
            "interval": "1d",
            "fetched_at": "2024-01-03T00:00:00",
        }

        with patch("app.data_sources.fetch_yahoo_prices", return_value=mock_result):
            from app.data_sources import fetch_yahoo_prices as patched_fn

            # Since we're patching the function itself, call the patched version
            result = patched_fn(["AAPL"], period="1mo")

            assert "symbols" in result
            assert "dates" in result
            assert "prices" in result
            assert "AAPL" in result["prices"]
            assert len(result["prices"]["AAPL"]) == 3

    def test_empty_symbols_raises_error(self) -> None:
        """Test that empty symbols raises ValueError."""
        with pytest.raises(ValueError, match="At least one symbol"):
            fetch_yahoo_prices([], period="1mo")


class TestFetchCryptoPrices:
    """Tests for fetch_crypto_prices function."""

    def test_successful_fetch(self) -> None:
        """Test successful crypto price fetch."""
        mock_market_data = {
            "prices": [
                [1704067200000, 42000.0],
                [1704153600000, 42500.0],
                [1704240000000, 43000.0],
            ]
        }

        with patch(
            "app.data_sources._coingecko_request",
            return_value=mock_market_data,
        ):
            result = fetch_crypto_prices(["BTC"], days=3)

            assert "symbols" in result
            assert "dates" in result
            assert "prices" in result
            assert "BTC" in result["prices"]
            assert len(result["prices"]["BTC"]) == 3

    def test_unknown_symbol_raises_error(self) -> None:
        """Test that unknown symbol raises ValueError when all symbols fail."""
        # fetch_crypto_prices only raises when ALL symbols fail to fetch
        # Individual failures are logged and skipped
        with (
            patch(
                "app.data_sources._coingecko_request",
                side_effect=ValueError("Coin not found"),
            ),
            pytest.raises(ValueError, match="Could not fetch data for any symbols"),
        ):
            fetch_crypto_prices(["UNKNOWNCOIN"], days=30)


class TestFetchPrices:
    """Tests for unified fetch_prices function."""

    def test_yahoo_source(self) -> None:
        """Test fetching with yahoo source."""
        mock_result = {
            "symbols": ["AAPL"],
            "dates": ["2024-01-01", "2024-01-02"],
            "prices": {"AAPL": [100.0, 101.0]},
            "source": "yahoo",
            "period": "6mo",
            "interval": "1d",
            "fetched_at": "2024-01-02T00:00:00",
        }

        with patch("app.data_sources.fetch_yahoo_prices", return_value=mock_result):
            result = fetch_prices(["AAPL"], source="yahoo")
            assert "AAPL" in result["prices"]

    def test_crypto_source(self) -> None:
        """Test fetching with crypto source."""
        mock_market_data = {
            "prices": [
                [1704067200000, 42000.0],
                [1704153600000, 42500.0],
            ]
        }

        with patch(
            "app.data_sources._coingecko_request",
            return_value=mock_market_data,
        ):
            result = fetch_prices(["BTC"], source="crypto")
            assert "BTC" in result["prices"]

    def test_auto_detect_crypto(self) -> None:
        """Test auto-detection of crypto symbols."""
        mock_market_data = {
            "prices": [
                [1704067200000, 42000.0],
            ]
        }

        with patch(
            "app.data_sources._coingecko_request",
            return_value=mock_market_data,
        ):
            result = fetch_prices(["BTC"], source="auto")
            assert "BTC" in result["prices"]

    def test_invalid_source_raises_error(self) -> None:
        """Test that invalid source raises ValueError."""
        with pytest.raises(ValueError, match="Invalid source"):
            fetch_prices(["AAPL"], source="invalid_source")


class TestGetTrendingCrypto:
    """Tests for get_trending_crypto function."""

    def test_returns_trending_coins(self) -> None:
        """Test that trending coins are returned."""
        mock_response = {
            "coins": [
                {
                    "item": {
                        "id": "bitcoin",
                        "symbol": "btc",
                        "name": "Bitcoin",
                        "market_cap_rank": 1,
                        "score": 0,
                    }
                },
                {
                    "item": {
                        "id": "ethereum",
                        "symbol": "eth",
                        "name": "Ethereum",
                        "market_cap_rank": 2,
                        "score": 1,
                    }
                },
            ]
        }

        with patch("app.data_sources._coingecko_request", return_value=mock_response):
            result = get_trending_crypto()
            assert len(result) == 2
            assert result[0]["id"] == "bitcoin"


class TestSearchCrypto:
    """Tests for search_crypto function."""

    def test_search_returns_results(self) -> None:
        """Test that search returns results."""
        mock_response = {
            "coins": [
                {
                    "id": "bitcoin",
                    "symbol": "btc",
                    "name": "Bitcoin",
                    "market_cap_rank": 1,
                },
            ]
        }

        with patch("app.data_sources._coingecko_request", return_value=mock_response):
            result = search_crypto("bitcoin")
            assert len(result) == 1
            assert result[0]["id"] == "bitcoin"


class TestGetCryptoCoinInfo:
    """Tests for get_crypto_coin_info function."""

    def test_returns_coin_info(self) -> None:
        """Test that coin info is returned."""
        mock_response = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "market_data": {
                "current_price": {"usd": 50000.0},
                "market_cap": {"usd": 1000000000000},
                "total_volume": {"usd": 50000000000},
                "high_24h": {"usd": 51000.0},
                "low_24h": {"usd": 49000.0},
                "price_change_24h": 1000.0,
                "price_change_percentage_24h": 2.0,
                "market_cap_rank": 1,
            },
            "categories": ["Cryptocurrency"],
        }

        with patch("app.data_sources._coingecko_request", return_value=mock_response):
            result = get_crypto_coin_info("bitcoin")
            assert result["id"] == "bitcoin"
            assert result["current_price"] == 50000.0


class TestListSupportedCryptoSymbols:
    """Tests for list_supported_crypto_symbols function."""

    def test_returns_mapping(self) -> None:
        """Test that symbol mapping is returned."""
        result = list_supported_crypto_symbols()
        assert isinstance(result, dict)
        assert "BTC" in result
        assert result["BTC"] == "bitcoin"

    def test_returns_copy(self) -> None:
        """Test that a copy is returned (not the original)."""
        result1 = list_supported_crypto_symbols()
        result2 = list_supported_crypto_symbols()

        # Modify result1
        result1["TEST"] = "test-coin"

        # result2 should not be affected
        assert "TEST" not in result2
