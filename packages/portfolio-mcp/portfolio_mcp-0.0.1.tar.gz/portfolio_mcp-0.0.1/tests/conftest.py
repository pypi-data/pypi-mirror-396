"""Pytest configuration and fixtures for portfolio-mcp tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import pytest
from finquant.portfolio import build_portfolio
from mcp_refcache import PreviewConfig, PreviewStrategy, RefCache, SizeMode

from app.storage import PortfolioStore

if TYPE_CHECKING:
    from collections.abc import Generator


def unwrap_cached(
    result: dict[str, Any], cache: RefCache | None = None
) -> dict[str, Any]:
    """Unwrap a @cache.cached() response to get the underlying value.

    The @cache.cached() decorator returns:
    - Small results: {"ref_id": ..., "value": <original>, "is_complete": True, ...}
    - Large results: {"ref_id": ..., "preview": <sample>, "is_complete": False, ...}

    This helper extracts the full value for test assertions.
    When is_complete is False and a cache is provided, it resolves the full value.

    Args:
        result: The cached response dict.
        cache: Optional RefCache instance to resolve incomplete results.

    Returns:
        The full underlying value.
    """
    if "value" in result:
        return result["value"]
    elif "preview" in result:
        # If incomplete and we have a cache, resolve the full value
        if not result.get("is_complete", True) and cache is not None:
            ref_id = result.get("ref_id")
            if ref_id:
                return cache.resolve(ref_id)
        return result["preview"]
    else:
        # Not a cached response, return as-is (e.g., error responses)
        return result


@pytest.fixture
def cache() -> Generator[RefCache, None, None]:
    """Create a fresh RefCache instance for testing."""
    test_cache = RefCache(
        name="test_finquant",
        default_ttl=3600,
        preview_config=PreviewConfig(
            size_mode=SizeMode.TOKEN,
            max_size=2048,  # Token-based, large enough to avoid sampling in tests
            default_strategy=PreviewStrategy.SAMPLE,
        ),
    )
    yield test_cache
    # Cleanup after test
    test_cache.clear()


@pytest.fixture
def store(cache: RefCache) -> PortfolioStore:
    """Create a PortfolioStore with test cache."""
    return PortfolioStore(cache=cache, namespace="test_portfolios")


@pytest.fixture
def sample_prices() -> dict[str, list[float]]:
    """Generate sample price data for testing."""
    np.random.seed(42)
    days = 100

    symbols = ["AAPL", "GOOG", "AMZN"]
    prices = {}

    for symbol in symbols:
        # Generate GBM prices
        initial_price = 100.0
        daily_returns = 0.0003 + 0.02 * np.random.randn(days)
        log_returns = np.log(1 + daily_returns)
        cumulative = np.cumsum(log_returns)
        prices[symbol] = (initial_price * np.exp(cumulative)).tolist()

    return prices


@pytest.fixture
def sample_dates() -> list[str]:
    """Generate sample dates for testing."""
    dates = pd.bdate_range(end=pd.Timestamp.now().normalize(), periods=100)
    return [d.strftime("%Y-%m-%d") for d in dates]


@pytest.fixture
def sample_weights() -> dict[str, float]:
    """Sample portfolio weights."""
    return {"AAPL": 0.4, "GOOG": 0.35, "AMZN": 0.25}


@pytest.fixture
def sample_portfolio_data(
    sample_prices: dict[str, list[float]],
    sample_dates: list[str],
    sample_weights: dict[str, float],
) -> dict[str, Any]:
    """Complete sample portfolio data."""
    return {
        "name": "test_portfolio",
        "symbols": list(sample_prices.keys()),
        "prices": sample_prices,
        "dates": sample_dates,
        "weights": sample_weights,
    }


@pytest.fixture
def finquant_portfolio(
    sample_prices: dict[str, list[float]],
    sample_dates: list[str],
    sample_weights: dict[str, float],
) -> Any:
    """Create a FinQuant Portfolio object for testing."""
    # Build DataFrame with explicit float64 dtype
    date_index = pd.to_datetime(sample_dates)
    prices_df = pd.DataFrame(sample_prices, index=date_index).astype(np.float64)

    # Build allocation DataFrame with explicit types
    symbols = list(sample_prices.keys())
    allocation_data = []
    for s in symbols:
        allocation_data.append(
            {
                "Allocation": np.float64(sample_weights[s] * 100),
                "Name": s,
            }
        )
    allocation_df = pd.DataFrame(allocation_data)
    # Ensure Allocation column is float64
    allocation_df["Allocation"] = allocation_df["Allocation"].astype(np.float64)

    # Build portfolio
    portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
    portfolio.risk_free_rate = 0.02

    return portfolio


@pytest.fixture
def stored_portfolio(
    store: PortfolioStore,
    finquant_portfolio: Any,
) -> tuple[str, str]:
    """Store a portfolio and return (name, ref_id)."""
    name = "stored_test_portfolio"
    ref_id = store.store(finquant_portfolio, name)
    return name, ref_id
