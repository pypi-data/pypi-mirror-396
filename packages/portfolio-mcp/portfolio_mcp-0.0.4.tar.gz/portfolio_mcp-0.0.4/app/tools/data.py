"""Data generation and fetching tools for FinQuant MCP.

This module provides tools for:
- Generating synthetic financial data (GBM)
- Fetching real market data (Yahoo Finance, CoinGecko)
- Crypto-specific tools (search, trending, info)

Large results are cached using RefCache and returned as ref_id + preview
for efficient handling by LLM agents.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from app.data_sources import (
    get_crypto_coin_info,
    get_trending_crypto,
    list_supported_crypto_symbols,
    search_crypto,
)

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from mcp_refcache import RefCache

    from app.storage import PortfolioStore


def register_data_tools(
    mcp: FastMCP, store: PortfolioStore, cache: RefCache | None = None
) -> None:
    """Register data generation tools with the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        store: The portfolio store for caching generated data.
        cache: Optional RefCache instance for caching large results.
    """

    @mcp.tool
    def generate_price_series(
        symbols: list[str],
        days: int = 252,
        initial_prices: dict[str, float] | None = None,
        annual_returns: dict[str, float] | None = None,
        annual_volatilities: dict[str, float] | None = None,
        correlation_matrix: list[list[float]] | None = None,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Generate synthetic price series using Geometric Brownian Motion.

        Creates realistic-looking stock price data with customizable parameters
        for each asset. Supports correlated assets via a correlation matrix.

        Large results are cached and returned as a reference with preview.
        Use get_cached_result to paginate through the full price series.

        Args:
            symbols: List of asset symbols (e.g., ['GOOG', 'AMZN', 'AAPL']).
            days: Number of trading days to generate (default: 252, one year).
            initial_prices: Optional initial price per symbol.
                Defaults to 100.0 for all symbols.
            annual_returns: Optional expected annual return per symbol.
                Defaults to 0.08 (8%) for all symbols.
            annual_volatilities: Optional annual volatility per symbol.
                Defaults to 0.20 (20%) for all symbols.
            correlation_matrix: Optional correlation matrix for the assets.
                Should be a symmetric positive semi-definite matrix.
                Defaults to identity matrix (uncorrelated).
            seed: Random seed for reproducibility.

        Returns:
            Dictionary containing:
            - ref_id: Reference ID for accessing full cached data
            - symbols: List of symbols
            - preview: Sample of the price data
            - total_items: Total number of data points (days)
            - parameters: Generation parameters used
            - message: Instructions for pagination

        Example:
            ```
            # Generate 1 year of data for 3 tech stocks
            result = generate_price_series(
                symbols=["GOOG", "AMZN", "AAPL"],
                days=252,
                annual_returns={"GOOG": 0.12, "AMZN": 0.15, "AAPL": 0.10},
                annual_volatilities={"GOOG": 0.25, "AMZN": 0.30, "AAPL": 0.22},
                seed=42
            )

            # Use ref_id to paginate
            page2 = get_cached_result(ref_id=result["ref_id"], page=2)
            ```
        """
        if seed is not None:
            np.random.seed(seed)

        num_assets = len(symbols)

        # Set defaults for missing parameters
        if initial_prices is None:
            initial_prices = {}
        if annual_returns is None:
            annual_returns = {}
        if annual_volatilities is None:
            annual_volatilities = {}

        # Build parameter arrays
        prices_initial = np.array(
            [initial_prices.get(s, 100.0) for s in symbols], dtype=np.float64
        )
        returns_annual = np.array(
            [annual_returns.get(s, 0.08) for s in symbols], dtype=np.float64
        )
        vols_annual = np.array(
            [annual_volatilities.get(s, 0.20) for s in symbols], dtype=np.float64
        )

        # Build correlation matrix
        if correlation_matrix is not None:
            corr = np.array(correlation_matrix, dtype=np.float64)
        else:
            corr = np.eye(num_assets)

        # Convert annual to daily parameters
        daily_returns = returns_annual / 252
        daily_vols = vols_annual / np.sqrt(252)

        # Generate correlated random numbers using Cholesky decomposition
        cholesky = np.linalg.cholesky(corr)
        random_samples = np.random.randn(days, num_assets)
        correlated_samples = random_samples @ cholesky.T

        # Generate daily log returns
        daily_log_returns = (
            daily_returns - 0.5 * daily_vols**2
        ) + daily_vols * correlated_samples

        # Generate prices using GBM
        cumulative_log_returns = np.cumsum(daily_log_returns, axis=0)
        prices_matrix = prices_initial * np.exp(cumulative_log_returns)

        # Generate date index (business days ending today)
        end_date = pd.Timestamp.now().normalize()
        dates = pd.bdate_range(end=end_date, periods=days)

        # Build prices dict
        prices_dict = {
            symbol: prices_matrix[:, i].tolist() for i, symbol in enumerate(symbols)
        }
        dates_list = [d.strftime("%Y-%m-%d") for d in dates]

        # Build the full data structure
        full_data = {
            "symbols": symbols,
            "dates": dates_list,
            "prices": prices_dict,
            "parameters": {
                "days": days,
                "initial_prices": {s: prices_initial[i] for i, s in enumerate(symbols)},
                "annual_returns": {s: returns_annual[i] for i, s in enumerate(symbols)},
                "annual_volatilities": {
                    s: vols_annual[i] for i, s in enumerate(symbols)
                },
                "correlation_matrix": corr.tolist(),
                "seed": seed,
                "generated_at": datetime.now().isoformat(),
            },
        }

        # If cache is available, cache the result and return reference + preview
        if cache is not None:
            # Cache the full data
            cache_key = f"price_series_{'-'.join(symbols)}_{days}_{seed or 'random'}"
            ref = cache.set(
                key=cache_key,
                value=full_data,
                namespace="data",
                tool_name="generate_price_series",
            )

            # Get preview
            response = cache.get(ref.ref_id)

            return {
                "ref_id": ref.ref_id,
                "symbols": symbols,
                "total_items": days,
                "num_assets": num_assets,
                "date_range": {
                    "start": dates_list[0],
                    "end": dates_list[-1],
                },
                "preview": response.preview,
                "preview_strategy": response.preview_strategy.value,
                "parameters": full_data["parameters"],
                "message": f"Generated {days} days of prices for {num_assets} assets. Use get_cached_result(ref_id='{ref.ref_id}') to paginate.",
            }

        # Fallback: return full data if no cache available
        return full_data

    @mcp.tool
    def generate_portfolio_scenarios(
        base_symbols: list[str],
        num_scenarios: int = 5,
        days: int = 252,
        return_range: tuple[float, float] = (0.02, 0.15),
        volatility_range: tuple[float, float] = (0.10, 0.35),
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Generate multiple portfolio scenarios with varying parameters.

        Useful for testing optimization strategies across different
        market conditions.

        Large results are cached and returned as a reference with preview.
        Use get_cached_result to paginate through the full scenario data.

        Args:
            base_symbols: List of asset symbols for all scenarios.
            num_scenarios: Number of different scenarios to generate.
            days: Number of trading days per scenario.
            return_range: (min, max) annual return range for random generation.
            volatility_range: (min, max) annual volatility range.
            seed: Random seed for reproducibility.

        Returns:
            Dictionary containing:
            - ref_id: Reference ID for accessing full cached data
            - num_scenarios: Number of scenarios generated
            - preview: Sample of scenarios
            - summary: Summary statistics across scenarios
        """
        if seed is not None:
            np.random.seed(seed)

        scenarios = []
        for i in range(num_scenarios):
            # Generate random parameters for this scenario
            scenario_returns = {
                s: np.random.uniform(return_range[0], return_range[1])
                for s in base_symbols
            }
            scenario_vols = {
                s: np.random.uniform(volatility_range[0], volatility_range[1])
                for s in base_symbols
            }

            # Generate a random correlation structure
            # Create a random positive semi-definite correlation matrix
            num_assets = len(base_symbols)
            random_matrix = np.random.randn(num_assets, num_assets)
            cov_like = random_matrix @ random_matrix.T
            diag = np.sqrt(np.diag(cov_like))
            corr = cov_like / np.outer(diag, diag)

            # Generate prices for this scenario (get full data since no cache in inner call)
            scenario_data = generate_price_series(
                symbols=base_symbols,
                days=days,
                annual_returns=scenario_returns,
                annual_volatilities=scenario_vols,
                correlation_matrix=corr.tolist(),
                seed=None,  # Already seeded above
            )

            # If the inner call returned a ref_id, we need to extract the data
            # For scenarios, we store a summary not the full inner data
            scenarios.append(
                {
                    "scenario_id": i + 1,
                    "name": f"scenario_{i + 1}",
                    "returns": scenario_returns,
                    "volatilities": scenario_vols,
                    "correlation_matrix": corr.tolist(),
                    "data_ref_id": scenario_data.get(
                        "ref_id"
                    ),  # Reference to full data
                }
            )

        # Calculate summary statistics
        summary = {
            "num_scenarios": num_scenarios,
            "symbols": base_symbols,
            "days_per_scenario": days,
            "return_range": list(return_range),
            "volatility_range": list(volatility_range),
            "seed": seed,
            "generated_at": datetime.now().isoformat(),
        }

        full_result = {
            "scenarios": scenarios,
            "summary": summary,
        }

        # Cache if available
        if cache is not None:
            cache_key = (
                f"scenarios_{'-'.join(base_symbols)}_{num_scenarios}_{seed or 'random'}"
            )
            ref = cache.set(
                key=cache_key,
                value=full_result,
                namespace="data",
                tool_name="generate_portfolio_scenarios",
            )

            response = cache.get(ref.ref_id)

            return {
                "ref_id": ref.ref_id,
                "num_scenarios": num_scenarios,
                "symbols": base_symbols,
                "days_per_scenario": days,
                "preview": response.preview,
                "preview_strategy": response.preview_strategy.value,
                "summary": summary,
                "message": f"Generated {num_scenarios} scenarios. Use get_cached_result(ref_id='{ref.ref_id}') to access full data.",
            }

        return full_result

    @mcp.tool
    def get_sample_portfolio_data() -> dict[str, Any]:
        """Get pre-defined sample portfolio data for quick testing.

        Returns sample data for a diversified portfolio with realistic
        parameters based on historical market behavior.

        Returns:
            Dictionary with sample portfolio data ready for use with
            create_portfolio().
        """
        # Define a diversified sample portfolio
        sample = {
            "name": "sample_diversified",
            "description": "A diversified sample portfolio for testing",
            "symbols": ["TECH", "HEALTH", "FINANCE", "ENERGY", "CONSUMER"],
            "suggested_weights": {
                "TECH": 0.25,
                "HEALTH": 0.20,
                "FINANCE": 0.20,
                "ENERGY": 0.15,
                "CONSUMER": 0.20,
            },
            "typical_annual_returns": {
                "TECH": 0.12,
                "HEALTH": 0.09,
                "FINANCE": 0.08,
                "ENERGY": 0.06,
                "CONSUMER": 0.07,
            },
            "typical_annual_volatilities": {
                "TECH": 0.28,
                "HEALTH": 0.18,
                "FINANCE": 0.22,
                "ENERGY": 0.30,
                "CONSUMER": 0.15,
            },
            "typical_correlations": [
                [1.00, 0.35, 0.45, 0.20, 0.40],  # TECH
                [0.35, 1.00, 0.30, 0.15, 0.35],  # HEALTH
                [0.45, 0.30, 1.00, 0.40, 0.50],  # FINANCE
                [0.20, 0.15, 0.40, 1.00, 0.25],  # ENERGY
                [0.40, 0.35, 0.50, 0.25, 1.00],  # CONSUMER
            ],
            "usage_example": """
# Generate price data
prices = generate_price_series(
    symbols=sample['symbols'],
    annual_returns=sample['typical_annual_returns'],
    annual_volatilities=sample['typical_annual_volatilities'],
    correlation_matrix=sample['typical_correlations'],
    seed=42
)

# Create portfolio
portfolio = create_portfolio(
    name='my_portfolio',
    symbols=sample['symbols'],
    weights=sample['suggested_weights'],
    prices=prices['prices'],
    dates=prices['dates']
)
""",
        }

        return sample

    @mcp.tool
    def get_trending_coins() -> dict[str, Any]:
        """Get trending cryptocurrencies from CoinGecko.

        Returns a list of coins that are trending in the last 24 hours,
        useful for discovering popular assets to analyze.

        Returns:
            Dictionary containing:
            - coins: List of trending coin info (id, name, symbol, rank)
            - fetched_at: ISO timestamp

        Example:
            ```
            result = get_trending_coins()
            for coin in result['coins']:
                print(f"{coin['name']} ({coin['symbol']})")
            ```
        """
        try:
            coins = get_trending_crypto()
            return {
                "coins": coins,
                "count": len(coins),
                "fetched_at": datetime.now().isoformat(),
            }
        except ValueError as error:
            return {
                "error": str(error),
                "suggestion": "CoinGecko API may be rate-limited. Try again later.",
            }

    @mcp.tool
    def search_crypto_coins(query: str) -> dict[str, Any]:
        """Search for cryptocurrencies on CoinGecko.

        Find coins by name, symbol, or keyword. Useful for discovering
        coin IDs to use with create_portfolio.

        Args:
            query: Search query (e.g., 'bitcoin', 'defi', 'layer 2').

        Returns:
            Dictionary containing:
            - coins: List of matching coins (id, name, symbol, market_cap_rank)
            - count: Number of results
            - fetched_at: ISO timestamp

        Example:
            ```
            # Search for DeFi coins
            result = search_crypto_coins(query="defi")
            for coin in result['coins']:
                print(f"{coin['name']} ({coin['symbol']}) - Rank: {coin['market_cap_rank']}")
            ```
        """
        if not query or len(query.strip()) == 0:
            return {"error": "Query cannot be empty"}

        try:
            coins = search_crypto(query.strip())
            return {
                "query": query,
                "coins": coins,
                "count": len(coins),
                "fetched_at": datetime.now().isoformat(),
            }
        except ValueError as error:
            return {
                "error": str(error),
                "suggestion": "CoinGecko API may be rate-limited. Try again later.",
            }

    @mcp.tool
    def get_crypto_info(symbol: str) -> dict[str, Any]:
        """Get detailed information about a cryptocurrency.

        Retrieves current price, market cap, volume, and 24h changes.

        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH', 'SOL') or CoinGecko ID.

        Returns:
            Dictionary containing coin information:
            - id, name, symbol
            - current_price, market_cap, total_volume
            - high_24h, low_24h, price_change_24h
            - market_cap_rank, categories

        Example:
            ```
            result = get_crypto_info(symbol="BTC")
            print(f"Bitcoin: ${result['current_price']:,.2f}")
            print(f"24h change: {result['price_change_percentage_24h']:.2f}%")
            ```
        """
        from app.data_sources import CRYPTO_SYMBOL_TO_ID

        # Map symbol to CoinGecko ID
        coin_id = CRYPTO_SYMBOL_TO_ID.get(symbol.upper(), symbol.lower())

        try:
            info = get_crypto_coin_info(coin_id)
            info["fetched_at"] = datetime.now().isoformat()
            return info
        except ValueError as error:
            return {
                "error": str(error),
                "suggestion": f"Try searching with search_crypto_coins(query='{symbol}')",
            }

    @mcp.tool
    def list_crypto_symbols() -> dict[str, Any]:
        """List supported cryptocurrency symbols and their CoinGecko IDs.

        Returns the mapping of common crypto symbols (like BTC, ETH) to
        their CoinGecko API identifiers.

        Returns:
            Dictionary containing:
            - symbols: Dict mapping symbol to CoinGecko ID
            - count: Number of supported symbols
            - usage: How to use with create_portfolio

        Example:
            ```
            result = list_crypto_symbols()
            print(f"Supported: {list(result['symbols'].keys())[:10]}...")
            ```
        """
        symbols = list_supported_crypto_symbols()
        return {
            "symbols": symbols,
            "count": len(symbols),
            "usage": "Use these symbols with create_portfolio(symbols=[...], source='crypto')",
            "example_portfolio": "create_portfolio(name='crypto', symbols=['BTC', 'ETH', 'SOL'], source='crypto')",
        }
