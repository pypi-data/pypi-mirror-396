"""Portfolio CRUD tools for FinQuant MCP.

This module provides tools for creating, reading, updating, and deleting
portfolios using RefCache for persistent storage.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import pandas as pd
from finquant.portfolio import build_portfolio

from app.data_sources import fetch_prices

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from app.storage import PortfolioStore

# Type alias for source parameter
SourceType = Literal["synthetic", "yahoo", "crypto"]


def register_portfolio_tools(mcp: FastMCP, store: PortfolioStore) -> None:
    """Register portfolio CRUD tools with the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        store: The portfolio store for persistence.
    """

    def _create_portfolio_impl(
        name: str,
        symbols: list[str],
        weights: dict[str, float] | None = None,
        prices: dict[str, list[float]] | None = None,
        dates: list[str] | None = None,
        days: int = 252,
        risk_free_rate: float = 0.02,
        seed: int | None = None,
        source: str = "synthetic",
        period: str = "1y",
    ) -> dict[str, Any]:
        """Internal implementation for portfolio creation.

        This is extracted so it can be called by both create_portfolio tool
        and clone_portfolio tool without going through the MCP tool wrapper.

        Args:
            name: Unique name for the portfolio.
            symbols: List of asset symbols.
            weights: Optional allocation weights per symbol. Must sum to 1.0.
            prices: Optional price data per symbol as dict of lists.
            dates: Optional list of date strings (ISO format) for price data.
            days: Number of trading days for synthetic data.
            risk_free_rate: Risk-free rate for calculations.
            seed: Random seed for synthetic data generation.
            source: Data source for prices:
                - "synthetic": Generate GBM data (default)
                - "yahoo": Fetch from Yahoo Finance (stocks, ETFs, crypto with -USD suffix)
                - "crypto": Fetch from CoinGecko (crypto symbols like BTC, ETH)
            period: Period for Yahoo Finance data (e.g., '1y', '6mo', '3mo').

        Returns:
            Dictionary containing portfolio info or error.
        """
        # Check if portfolio already exists
        if store.exists(name):
            return {
                "error": f"Portfolio '{name}' already exists. Use update_portfolio or delete it first.",
                "suggestion": f"Try: delete_portfolio(name='{name}') first, or use a different name.",
            }

        # Determine data source
        data_source = source.lower() if source else "synthetic"

        if prices is not None:
            # User provided prices directly
            if dates is None:
                return {
                    "error": "dates parameter is required when providing price data",
                }
            if len(dates) == 0:
                return {"error": "dates list cannot be empty"}

            # Validate all symbols have price data
            for symbol in symbols:
                if symbol not in prices:
                    return {
                        "error": f"Missing price data for symbol '{symbol}'",
                    }
                if len(prices[symbol]) != len(dates):
                    return {
                        "error": f"Price data length mismatch for '{symbol}': "
                        f"got {len(prices[symbol])}, expected {len(dates)}",
                    }

        elif data_source in ("yahoo", "crypto"):
            # Fetch real market data
            try:
                fetched = fetch_prices(
                    symbols=symbols,
                    source=data_source,
                    period=period,
                    days=days,
                )
                prices = fetched["prices"]
                dates = fetched["dates"]
                symbols = fetched["symbols"]  # May be filtered if some failed
            except ValueError as error:
                return {
                    "error": f"Failed to fetch market data: {error}",
                    "suggestion": "Check symbol names or try source='synthetic' for testing",
                }

        else:
            # Generate synthetic prices using GBM
            if seed is not None:
                np.random.seed(seed)

            # Default parameters for synthetic data
            initial_prices = dict.fromkeys(symbols, 100.0)
            annual_drift = 0.08
            annual_volatility = 0.20

            daily_drift = annual_drift / 252
            daily_volatility = annual_volatility / np.sqrt(252)

            # Generate date index
            end_date = pd.Timestamp.now().normalize()
            date_index = pd.bdate_range(end=end_date, periods=days)

            # Generate prices
            prices_dict = {}
            for symbol in symbols:
                daily_returns = daily_drift + daily_volatility * np.random.randn(days)
                log_returns = np.log(1 + daily_returns)
                cumulative = np.cumsum(log_returns)
                prices_dict[symbol] = (
                    initial_prices[symbol] * np.exp(cumulative)
                ).tolist()

            prices = prices_dict
            dates = [d.strftime("%Y-%m-%d") for d in date_index]

        # Build DataFrame from prices with explicit float64 dtype
        date_index = pd.to_datetime(dates)
        prices_df = pd.DataFrame(prices, index=date_index).astype(np.float64)

        # Build allocation DataFrame
        if weights is None:
            # Equal weights
            equal_weight = 1.0 / len(symbols)
            weights = dict.fromkeys(symbols, equal_weight)
        else:
            # Validate weights
            weight_sum = sum(weights.values())
            if not np.isclose(weight_sum, 1.0, atol=0.01):
                return {
                    "error": f"Weights must sum to 1.0, got {weight_sum:.4f}",
                    "suggestion": "Normalize your weights or check for missing symbols",
                }

            # Ensure all symbols have weights
            for symbol in symbols:
                if symbol not in weights:
                    return {
                        "error": f"Missing weight for symbol '{symbol}'",
                    }

        # Create allocation DataFrame for FinQuant with explicit float64 dtype
        allocation_data = [
            {"Allocation": np.float64(weights[s] * 100), "Name": s} for s in symbols
        ]
        allocation_df = pd.DataFrame(allocation_data)
        allocation_df["Allocation"] = allocation_df["Allocation"].astype(np.float64)

        # Build FinQuant portfolio
        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = risk_free_rate

        # Store in RefCache
        ref_id = store.store(portfolio, name)

        # Return portfolio info
        return {
            "name": name,
            "ref_id": ref_id,
            "symbols": symbols,
            "weights": weights,
            "num_days": len(dates),
            "date_range": {"start": dates[0], "end": dates[-1]},
            "metrics": {
                "expected_return": float(portfolio.expected_return),
                "volatility": float(portfolio.volatility),
                "sharpe_ratio": float(portfolio.sharpe),
                "sortino_ratio": float(portfolio.sortino),
                "value_at_risk": float(portfolio.var),
            },
            "settings": {
                "risk_free_rate": risk_free_rate,
            },
            "source": data_source,
            "created_at": datetime.now().isoformat(),
        }

    @mcp.tool
    def create_portfolio(
        name: str,
        symbols: list[str],
        weights: dict[str, float] | None = None,
        prices: dict[str, list[float]] | None = None,
        dates: list[str] | None = None,
        days: int = 252,
        risk_free_rate: float = 0.02,
        seed: int | None = None,
        source: str = "synthetic",
        period: str = "1y",
    ) -> dict[str, Any]:
        """Create a new portfolio and store it in RefCache.

        Creates a portfolio from real market data, provided data, or synthetic
        data. The portfolio is stored persistently and can be retrieved,
        analyzed, and optimized.

        Args:
            name: Unique name for the portfolio (e.g., 'stocks', 'crypto').
            symbols: List of asset symbols.
                - For stocks/ETFs: ['AAPL', 'GOOG', 'MSFT', 'SPY']
                - For crypto via Yahoo: ['BTC-USD', 'ETH-USD']
                - For crypto via CoinGecko: ['BTC', 'ETH', 'SOL']
            weights: Optional allocation weights per symbol.
                Must sum to 1.0. If None, equal weights are used.
            prices: Optional price data per symbol as dict of lists.
                If provided, overrides source parameter.
            dates: Optional list of date strings (ISO format) for price data.
                Required if prices is provided.
            days: Number of trading days for synthetic data (default: 252).
            risk_free_rate: Risk-free rate for calculations (default: 0.02).
            seed: Random seed for synthetic data generation.
            source: Data source for prices (default: "synthetic"):
                - "synthetic": Generate GBM simulated data
                - "yahoo": Fetch from Yahoo Finance (stocks, ETFs, crypto)
                - "crypto": Fetch from CoinGecko API (crypto only)
            period: Period for market data (default: "1y").
                Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

        Returns:
            Dictionary containing:
            - name: Portfolio name
            - ref_id: RefCache reference ID for retrieval
            - symbols: List of symbols in the portfolio
            - weights: Allocation weights
            - metrics: Initial portfolio metrics (return, volatility, sharpe)
            - source: Data source used
            - created_at: ISO timestamp

        Example:
            ```
            # Create portfolio with real stock data
            result = create_portfolio(
                name="tech_stocks",
                symbols=["AAPL", "GOOG", "MSFT"],
                source="yahoo",
                period="1y"
            )

            # Create crypto portfolio from CoinGecko
            result = create_portfolio(
                name="crypto_portfolio",
                symbols=["BTC", "ETH", "SOL"],
                source="crypto"
            )

            # Create portfolio with synthetic data (for testing)
            result = create_portfolio(
                name="test_portfolio",
                symbols=["A", "B", "C"],
                source="synthetic",
                seed=42
            )
            ```
        """
        return _create_portfolio_impl(
            name=name,
            symbols=symbols,
            weights=weights,
            prices=prices,
            dates=dates,
            days=days,
            risk_free_rate=risk_free_rate,
            seed=seed,
            source=source,
            period=period,
        )

    @mcp.tool
    def get_portfolio(name: str) -> dict[str, Any]:
        """Get detailed information about a stored portfolio.

        Retrieves comprehensive information about a portfolio including
        its allocation, metrics, and settings.

        Args:
            name: The portfolio name.

        Returns:
            Dictionary containing full portfolio details, or error if not found.

        Example:
            ```
            info = get_portfolio(name="tech_stocks")
            print(f"Sharpe Ratio: {info['metrics']['sharpe_ratio']}")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
                "suggestion": "Use list_portfolios() to see available portfolios",
            }

        # Return summary with metrics
        summary = store.serializer.get_summary(data)
        summary["ref_id"] = f"{store.namespace}:{name}"

        return summary

    @mcp.tool
    def list_portfolios() -> dict[str, Any]:
        """List all stored portfolios with summary information.

        Returns a list of all portfolios in the store with their
        key metrics and metadata.

        Returns:
            Dictionary containing:
            - portfolios: List of portfolio summaries
            - count: Number of portfolios

        Example:
            ```
            result = list_portfolios()
            for pf in result['portfolios']:
                print(f"{pf['name']}: Sharpe={pf['metrics']['sharpe']:.2f}")
            ```
        """
        portfolios = store.list_portfolios()

        return {
            "portfolios": portfolios,
            "count": len(portfolios),
        }

    @mcp.tool
    def delete_portfolio(name: str) -> dict[str, Any]:
        """Delete a stored portfolio.

        Permanently removes a portfolio from storage.

        Args:
            name: The portfolio name to delete.

        Returns:
            Dictionary with deletion status.

        Example:
            ```
            result = delete_portfolio(name="old_portfolio")
            if result['deleted']:
                print("Portfolio deleted successfully")
            ```
        """
        if not store.exists(name):
            return {
                "deleted": False,
                "error": f"Portfolio '{name}' not found",
            }

        deleted = store.delete(name)

        return {
            "deleted": deleted,
            "name": name,
            "message": f"Portfolio '{name}' deleted successfully"
            if deleted
            else "Deletion failed",
        }

    @mcp.tool
    def update_portfolio_weights(
        name: str,
        weights: dict[str, float],
    ) -> dict[str, Any]:
        """Update the allocation weights of an existing portfolio.

        Changes the weight distribution across assets in a portfolio
        and recalculates all metrics.

        Args:
            name: The portfolio name.
            weights: New allocation weights per symbol. Must sum to 1.0.

        Returns:
            Updated portfolio information with new metrics.

        Example:
            ```
            result = update_portfolio_weights(
                name="tech_stocks",
                weights={"GOOG": 0.5, "AMZN": 0.3, "AAPL": 0.2}
            )
            print(f"New Sharpe: {result['metrics']['sharpe_ratio']}")
            ```
        """
        # Get existing portfolio data
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Validate weights
        symbols = data["prices"]["columns"]
        weight_sum = sum(weights.values())
        if not np.isclose(weight_sum, 1.0, atol=0.01):
            return {
                "error": f"Weights must sum to 1.0, got {weight_sum:.4f}",
            }

        for symbol in symbols:
            if symbol not in weights:
                return {
                    "error": f"Missing weight for symbol '{symbol}'",
                    "symbols_required": symbols,
                }

        # Rebuild portfolio with new weights
        prices_df, _ = store.serializer.deserialize(data)

        # Create new allocation DataFrame
        allocation_data = [{"Allocation": weights[s] * 100, "Name": s} for s in symbols]
        allocation_df = pd.DataFrame(allocation_data)

        # Rebuild portfolio
        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = data["settings"]["risk_free_rate"]

        # Store updated portfolio
        store.delete(name)
        ref_id = store.store(portfolio, name)

        return {
            "name": name,
            "ref_id": ref_id,
            "symbols": symbols,
            "old_weights": data["allocation"],
            "new_weights": weights,
            "metrics": {
                "expected_return": float(portfolio.expected_return),
                "volatility": float(portfolio.volatility),
                "sharpe_ratio": float(portfolio.sharpe),
                "sortino_ratio": float(portfolio.sortino),
                "value_at_risk": float(portfolio.var),
            },
            "updated_at": datetime.now().isoformat(),
        }

    @mcp.tool
    def clone_portfolio(
        source_name: str,
        new_name: str,
        new_weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Clone an existing portfolio, optionally with new weights.

        Creates a copy of a portfolio, useful for testing different
        allocation strategies on the same underlying assets.

        Args:
            source_name: The name of the portfolio to clone.
            new_name: The name for the cloned portfolio.
            new_weights: Optional new weights. If None, uses source weights.

        Returns:
            New portfolio information.

        Example:
            ```
            # Clone with same weights
            result = clone_portfolio(
                source_name="tech_stocks",
                new_name="tech_stocks_v2"
            )

            # Clone with different weights
            result = clone_portfolio(
                source_name="tech_stocks",
                new_name="tech_aggressive",
                new_weights={"GOOG": 0.6, "AMZN": 0.3, "AAPL": 0.1}
            )
            ```
        """
        # Check source exists
        data = store.get(source_name)
        if data is None:
            return {
                "error": f"Source portfolio '{source_name}' not found",
            }

        # Check target doesn't exist
        if store.exists(new_name):
            return {
                "error": f"Portfolio '{new_name}' already exists",
            }

        # Get symbols and prices
        symbols = data["prices"]["columns"]
        dates = data["prices"]["index"]

        # Build prices dict
        prices_dict = {}
        for i, symbol in enumerate(symbols):
            prices_dict[symbol] = [row[i] for row in data["prices"]["values"]]

        # Use existing weights if new_weights not provided
        if new_weights is None:
            new_weights = {}
            for row in data["allocation"]["values"]:
                new_weights[row[1]] = row[0] / 100.0  # Convert from percentage

        # Create new portfolio using internal implementation
        return _create_portfolio_impl(
            name=new_name,
            symbols=symbols,
            weights=new_weights,
            prices=prices_dict,
            dates=dates,
            risk_free_rate=data["settings"]["risk_free_rate"],
        )
