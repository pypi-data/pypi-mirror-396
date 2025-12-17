"""Storage helpers for RefCache serialization of FinQuant portfolios.

This module provides functions to serialize and deserialize FinQuant Portfolio
objects for storage in RefCache, enabling persistent portfolio management.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from mcp_refcache import AccessPolicy, Permission

if TYPE_CHECKING:
    from finquant.portfolio import Portfolio
    from mcp_refcache import RefCache


class PortfolioSerializer:
    """Handles serialization and deserialization of FinQuant Portfolio objects.

    FinQuant Portfolio objects contain pandas DataFrames and other complex types
    that need to be converted to JSON-serializable formats for RefCache storage.
    """

    @staticmethod
    def serialize(portfolio: Portfolio, name: str) -> dict[str, Any]:
        """Serialize a FinQuant Portfolio to a JSON-compatible dictionary.

        Args:
            portfolio: The FinQuant Portfolio object to serialize.
            name: A unique name for this portfolio.

        Returns:
            Dictionary containing all portfolio data in JSON-serializable format.
        """
        # Serialize price data (main DataFrame)
        prices_data = {
            "index": portfolio.data.index.strftime("%Y-%m-%d").tolist(),
            "columns": portfolio.data.columns.tolist(),
            "values": portfolio.data.values.tolist(),
        }

        # Serialize allocation data
        allocation_data = {
            "columns": portfolio.portfolio.columns.tolist(),
            "values": portfolio.portfolio.values.tolist(),
        }

        # Extract stock information
        stocks_info = {}
        for symbol, stock in portfolio.stocks.items():
            stocks_info[symbol] = {
                "name": stock.name,
                "investmentinfo": (
                    stock.investmentinfo.to_dict()
                    if hasattr(stock, "investmentinfo")
                    and stock.investmentinfo is not None
                    else None
                ),
            }

        # Serialize computed metrics
        metrics = {
            "expected_return": float(portfolio.expected_return),
            "volatility": float(portfolio.volatility),
            "sharpe": float(portfolio.sharpe),
            "sortino": float(portfolio.sortino),
            "var": float(portfolio.var),
            "downside_risk": float(portfolio.downside_risk),
            "skew": portfolio.skew.to_dict() if hasattr(portfolio, "skew") else {},
            "kurtosis": (
                portfolio.kurtosis.to_dict() if hasattr(portfolio, "kurtosis") else {}
            ),
            "beta": float(portfolio.beta) if portfolio.beta is not None else None,
            "treynor": (
                float(portfolio.treynor) if portfolio.treynor is not None else None
            ),
        }

        # Build serialized structure
        serialized = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "prices": prices_data,
            "allocation": allocation_data,
            "stocks": stocks_info,
            "metrics": metrics,
            "settings": {
                "risk_free_rate": float(portfolio.risk_free_rate),
                "freq": int(portfolio.freq),
                "var_confidence_level": float(portfolio.var_confidence_level),
            },
        }

        return serialized

    @staticmethod
    def deserialize(data: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Deserialize stored portfolio data back to DataFrames.

        Args:
            data: The serialized portfolio dictionary.

        Returns:
            Tuple of (prices_df, allocation_df) that can be used to rebuild Portfolio.
        """
        # Reconstruct prices DataFrame
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Reconstruct allocation DataFrame
        allocation_df = pd.DataFrame(
            data=data["allocation"]["values"],
            columns=data["allocation"]["columns"],
        )

        return prices_df, allocation_df

    @staticmethod
    def get_summary(data: dict[str, Any]) -> dict[str, Any]:
        """Extract summary information from serialized portfolio data.

        Args:
            data: The serialized portfolio dictionary.

        Returns:
            Summary dictionary with key portfolio information.
        """
        return {
            "name": data["name"],
            "created_at": data["created_at"],
            "symbols": data["prices"]["columns"],
            "num_days": len(data["prices"]["index"]),
            "weights": dict(
                zip(
                    [row[1] for row in data["allocation"]["values"]],
                    [row[0] for row in data["allocation"]["values"]],
                    strict=False,
                )
            ),
            "metrics": data["metrics"],
            "settings": data["settings"],
        }


class PortfolioStore:
    """Manages portfolio storage in RefCache.

    Provides high-level operations for storing, retrieving, and managing
    portfolios using RefCache as the backend.
    """

    def __init__(self, cache: RefCache, namespace: str = "portfolios") -> None:
        """Initialize the portfolio store.

        Args:
            cache: RefCache instance to use for storage.
            namespace: Namespace for portfolio references.
        """
        self.cache = cache
        self.namespace = namespace
        self.serializer = PortfolioSerializer()
        # Track name -> ref_id mapping
        self._refs: dict[str, str] = {}

    def store(self, portfolio: Portfolio, name: str) -> str:
        """Store a portfolio in RefCache.

        Args:
            portfolio: The FinQuant Portfolio object to store.
            name: Unique name for this portfolio.

        Returns:
            The RefCache reference ID for the stored portfolio.
        """
        serialized = self.serializer.serialize(portfolio, name)
        # Use policy with FULL permissions for agents to allow delete operations
        policy = AccessPolicy(
            user_permissions=Permission.FULL,
            agent_permissions=Permission.FULL,
        )
        ref = self.cache.set(
            key=name,
            value=serialized,
            namespace=self.namespace,
            policy=policy,
        )
        # Track the ref_id for this name
        self._refs[name] = ref.ref_id
        return ref.ref_id

    def get(self, name: str) -> dict[str, Any] | None:
        """Retrieve a stored portfolio by name.

        Args:
            name: The portfolio name.

        Returns:
            The serialized portfolio data, or None if not found.
        """
        ref_id = self._refs.get(name)
        if ref_id is None:
            return None
        try:
            # Use resolve() to get the full data, not just preview
            return self.cache.resolve(ref_id)
        except KeyError:
            return None

    def get_by_ref(self, ref_id: str) -> dict[str, Any] | None:
        """Retrieve a stored portfolio by reference ID.

        Args:
            ref_id: The RefCache reference ID.

        Returns:
            The serialized portfolio data, or None if not found.
        """
        try:
            # Use resolve() to get the full data
            return self.cache.resolve(ref_id)
        except KeyError:
            return None

    def rebuild(self, name: str) -> Portfolio | None:
        """Rebuild a FinQuant Portfolio object from stored data.

        Args:
            name: The portfolio name.

        Returns:
            Reconstructed Portfolio object, or None if not found.
        """
        from finquant.portfolio import build_portfolio

        data = self.get(name)
        if data is None:
            return None

        prices_df, allocation_df = self.serializer.deserialize(data)

        # Rebuild using FinQuant's build_portfolio
        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)

        # Restore settings
        portfolio.risk_free_rate = data["settings"]["risk_free_rate"]
        portfolio.freq = data["settings"]["freq"]
        portfolio.var_confidence_level = data["settings"]["var_confidence_level"]

        return portfolio

    def list_portfolios(self) -> list[dict[str, Any]]:
        """List all stored portfolios with summary information.

        Returns:
            List of portfolio summaries.
        """
        summaries = []

        for portfolio_name, ref_id in self._refs.items():
            try:
                # Use resolve() to get the full data
                data = self.cache.resolve(ref_id)
                if data is not None:
                    summary = self.serializer.get_summary(data)
                    summary["ref_id"] = ref_id
                    summary["name"] = portfolio_name  # Ensure name from mapping is used
                    summaries.append(summary)
            except KeyError:
                # Ref no longer valid, skip
                continue

        return summaries

    def delete(self, name: str) -> bool:
        """Delete a stored portfolio.

        Args:
            name: The portfolio name.

        Returns:
            True if deleted, False if not found.
        """
        ref_id = self._refs.get(name)
        if ref_id is None:
            return False

        try:
            deleted = self.cache.delete(ref_id)
            if deleted:
                del self._refs[name]
            return deleted
        except KeyError:
            return False

    def exists(self, name: str) -> bool:
        """Check if a portfolio exists.

        Args:
            name: The portfolio name.

        Returns:
            True if the portfolio exists.
        """
        ref_id = self._refs.get(name)
        if ref_id is None:
            return False
        try:
            return self.cache.exists(ref_id)
        except KeyError:
            return False


def generate_synthetic_prices(
    symbols: list[str],
    days: int = 252,
    initial_prices: dict[str, float] | None = None,
    annual_drift: float = 0.05,
    annual_volatility: float = 0.20,
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate synthetic price series using Geometric Brownian Motion.

    This is useful for testing and demos without requiring external data sources.

    Args:
        symbols: List of asset symbols.
        days: Number of trading days to generate.
        initial_prices: Optional dict of initial prices per symbol.
            Defaults to 100.0 for all symbols.
        annual_drift: Annual drift (expected return). Default 5%.
        annual_volatility: Annual volatility. Default 20%.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with date index and price columns per symbol.
    """
    if seed is not None:
        np.random.seed(seed)

    if initial_prices is None:
        initial_prices = dict.fromkeys(symbols, 100.0)

    # Daily parameters from annual
    daily_drift = annual_drift / 252
    daily_volatility = annual_volatility / np.sqrt(252)

    # Generate date index (business days)
    start_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    dates = pd.bdate_range(start=start_date, periods=days)

    # Generate prices using GBM
    prices_data = {}
    for symbol in symbols:
        initial_price = initial_prices.get(symbol, 100.0)

        # Generate daily returns: r = drift + volatility * N(0,1)
        daily_returns = daily_drift + daily_volatility * np.random.randn(days)

        # Convert to prices: P(t) = P(0) * exp(sum of log returns)
        log_returns = np.log(1 + daily_returns)
        cumulative_log_returns = np.cumsum(log_returns)
        prices = initial_price * np.exp(cumulative_log_returns)

        prices_data[symbol] = prices

    return pd.DataFrame(prices_data, index=dates)
