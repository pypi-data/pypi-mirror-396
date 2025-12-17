"""Tests for the storage module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest
from finquant.portfolio import Portfolio

from app.storage import (
    PortfolioSerializer,
    PortfolioStore,
    generate_synthetic_prices,
)

if TYPE_CHECKING:
    from mcp_refcache import RefCache


class TestGenerateSyntheticPrices:
    """Tests for generate_synthetic_prices function."""

    def test_generates_correct_number_of_days(self) -> None:
        """Should generate the specified number of days."""
        symbols = ["AAPL", "GOOG"]
        days = 100
        result = generate_synthetic_prices(symbols=symbols, days=days)

        assert len(result) == days
        for symbol in symbols:
            assert symbol in result.columns

    def test_uses_initial_prices(self) -> None:
        """Should start from specified initial prices."""
        symbols = ["AAPL", "GOOG"]
        initial_prices = {"AAPL": 150.0, "GOOG": 2800.0}
        result = generate_synthetic_prices(
            symbols=symbols,
            days=100,
            initial_prices=initial_prices,
            seed=42,
        )

        # First price should be close to initial (within one day's movement)
        assert result["AAPL"].iloc[0] == pytest.approx(initial_prices["AAPL"], rel=0.1)
        assert result["GOOG"].iloc[0] == pytest.approx(initial_prices["GOOG"], rel=0.1)

    def test_reproducible_with_seed(self) -> None:
        """Should produce same results with same seed."""
        symbols = ["AAPL", "GOOG"]
        result1 = generate_synthetic_prices(symbols=symbols, days=50, seed=42)
        result2 = generate_synthetic_prices(symbols=symbols, days=50, seed=42)

        pd.testing.assert_frame_equal(result1, result2)

    def test_different_with_different_seeds(self) -> None:
        """Should produce different results with different seeds."""
        symbols = ["AAPL"]
        result1 = generate_synthetic_prices(symbols=symbols, days=50, seed=42)
        result2 = generate_synthetic_prices(symbols=symbols, days=50, seed=123)

        assert not result1.equals(result2)

    def test_returns_dataframe_with_date_index(self) -> None:
        """Should return DataFrame with DatetimeIndex."""
        result = generate_synthetic_prices(symbols=["AAPL"], days=50)

        assert isinstance(result.index, pd.DatetimeIndex)

    def test_prices_are_positive(self) -> None:
        """All generated prices should be positive."""
        result = generate_synthetic_prices(symbols=["AAPL", "GOOG", "AMZN"], days=500)

        assert (result > 0).all().all()


class TestPortfolioSerializer:
    """Tests for PortfolioSerializer class."""

    def test_serialize_creates_valid_structure(
        self, finquant_portfolio: Portfolio
    ) -> None:
        """Serialization should create a complete data structure."""
        serialized = PortfolioSerializer.serialize(finquant_portfolio, "test")

        assert serialized["name"] == "test"
        assert "created_at" in serialized
        assert "prices" in serialized
        assert "allocation" in serialized
        assert "stocks" in serialized
        assert "metrics" in serialized
        assert "settings" in serialized

    def test_serialize_prices_structure(self, finquant_portfolio: Portfolio) -> None:
        """Prices should be serialized with index, columns, and values."""
        serialized = PortfolioSerializer.serialize(finquant_portfolio, "test")

        prices = serialized["prices"]
        assert "index" in prices
        assert "columns" in prices
        assert "values" in prices
        assert isinstance(prices["index"], list)
        assert isinstance(prices["columns"], list)
        assert isinstance(prices["values"], list)

    def test_serialize_metrics(self, finquant_portfolio: Portfolio) -> None:
        """Metrics should be properly serialized."""
        serialized = PortfolioSerializer.serialize(finquant_portfolio, "test")

        metrics = serialized["metrics"]
        assert "expected_return" in metrics
        assert "volatility" in metrics
        assert "sharpe" in metrics
        assert "sortino" in metrics
        assert "var" in metrics
        assert "downside_risk" in metrics

        # Check that metrics are floats (not numpy types)
        assert isinstance(metrics["expected_return"], float)
        assert isinstance(metrics["volatility"], float)

    def test_deserialize_reconstructs_dataframes(
        self, finquant_portfolio: Portfolio
    ) -> None:
        """Deserialization should reconstruct valid DataFrames."""
        serialized = PortfolioSerializer.serialize(finquant_portfolio, "test")
        prices_df, allocation_df = PortfolioSerializer.deserialize(serialized)

        assert isinstance(prices_df, pd.DataFrame)
        assert isinstance(allocation_df, pd.DataFrame)
        assert len(prices_df) == len(finquant_portfolio.data)
        assert list(prices_df.columns) == list(finquant_portfolio.data.columns)

    def test_get_summary(self, finquant_portfolio: Portfolio) -> None:
        """Summary should contain key portfolio information."""
        serialized = PortfolioSerializer.serialize(finquant_portfolio, "test")
        summary = PortfolioSerializer.get_summary(serialized)

        assert summary["name"] == "test"
        assert "created_at" in summary
        assert "symbols" in summary
        assert "num_days" in summary
        assert "weights" in summary
        assert "metrics" in summary


class TestPortfolioStore:
    """Tests for PortfolioStore class."""

    def test_store_and_get(
        self, store: PortfolioStore, finquant_portfolio: Portfolio
    ) -> None:
        """Should store and retrieve a portfolio."""
        ref_id = store.store(finquant_portfolio, "test_pf")

        # ref_id format is cache_name:hash, not namespace:key
        assert ref_id.startswith("test_finquant:")

        data = store.get("test_pf")
        assert data is not None
        assert data["name"] == "test_pf"

    def test_get_nonexistent_returns_none(self, store: PortfolioStore) -> None:
        """Getting a non-existent portfolio should return None."""
        result = store.get("nonexistent")
        assert result is None

    def test_exists(self, store: PortfolioStore, finquant_portfolio: Portfolio) -> None:
        """Should correctly report portfolio existence."""
        assert not store.exists("test_pf")

        store.store(finquant_portfolio, "test_pf")

        assert store.exists("test_pf")

    def test_delete(self, cache: RefCache, finquant_portfolio: Portfolio) -> None:
        """Should delete a stored portfolio."""

        # Create store with a policy that allows delete
        store = PortfolioStore(cache=cache, namespace="test_portfolios")

        store.store(finquant_portfolio, "test_pf")
        assert store.exists("test_pf")

        deleted = store.delete("test_pf")

        assert deleted
        assert not store.exists("test_pf")

    def test_delete_nonexistent_returns_false(self, store: PortfolioStore) -> None:
        """Deleting a non-existent portfolio should return False."""
        deleted = store.delete("nonexistent")
        assert not deleted

    def test_list_portfolios(
        self, store: PortfolioStore, finquant_portfolio: Portfolio
    ) -> None:
        """Should list all stored portfolios."""
        # Store multiple portfolios
        store.store(finquant_portfolio, "pf1")
        store.store(finquant_portfolio, "pf2")

        portfolios = store.list_portfolios()

        assert len(portfolios) == 2
        names = [p["name"] for p in portfolios]
        assert "pf1" in names
        assert "pf2" in names

    def test_rebuild_portfolio(
        self, store: PortfolioStore, finquant_portfolio: Portfolio
    ) -> None:
        """Should rebuild a FinQuant Portfolio from stored data."""
        store.store(finquant_portfolio, "test_pf")

        rebuilt = store.rebuild("test_pf")

        assert rebuilt is not None
        assert isinstance(rebuilt, Portfolio)
        assert len(rebuilt.data) == len(finquant_portfolio.data)
        # Metrics should be approximately equal
        assert rebuilt.expected_return == pytest.approx(
            finquant_portfolio.expected_return, rel=0.01
        )
        assert rebuilt.volatility == pytest.approx(
            finquant_portfolio.volatility, rel=0.01
        )

    def test_rebuild_nonexistent_returns_none(self, store: PortfolioStore) -> None:
        """Rebuilding a non-existent portfolio should return None."""
        result = store.rebuild("nonexistent")
        assert result is None

    def test_get_by_ref(
        self, store: PortfolioStore, finquant_portfolio: Portfolio
    ) -> None:
        """Should retrieve portfolio by full ref_id."""
        ref_id = store.store(finquant_portfolio, "test_pf")

        data = store.get_by_ref(ref_id)

        assert data is not None
        assert data["name"] == "test_pf"
