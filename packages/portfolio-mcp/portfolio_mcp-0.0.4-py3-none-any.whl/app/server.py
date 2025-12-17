"""portfolio-mcp Server - Portfolio analysis with mcp-refcache.

This module creates and configures the FastMCP server for portfolio
analysis, optimization, and management.

Features:
- Portfolio management (create, read, update, delete)
- Portfolio analysis (returns, volatility, Sharpe ratio, correlations)
- Portfolio optimization (Efficient Frontier, Monte Carlo simulation)
- Real market data from Yahoo Finance and CoinGecko
- Synthetic data generation (GBM price series)
- Reference-based caching for large results

Usage:
    # Run with typer CLI
    uvx portfolio-mcp stdio           # Local CLI mode
    uvx portfolio-mcp streamable-http # Remote/Docker mode

    # Or with uv
    uv run portfolio-mcp stdio
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from mcp_refcache import CacheResponse, PreviewConfig, PreviewStrategy, RefCache
from mcp_refcache.fastmcp import cache_instructions

from app import __version__
from app.storage import PortfolioStore
from app.tools.analysis import register_analysis_tools
from app.tools.data import register_data_tools
from app.tools.optimization import register_optimization_tools
from app.tools.portfolio import register_portfolio_tools

# =============================================================================
# Initialize FastMCP Server
# =============================================================================

mcp = FastMCP(
    name="portfolio-mcp",
    # nosec B608 - This is not SQL, just a long documentation string
    instructions=f"""A financial portfolio management server with reference-based caching.

Supports real market data from Yahoo Finance (stocks, ETFs) and CoinGecko (crypto).

## Portfolio Management Tools
- create_portfolio: Create portfolio from real market data or synthetic data
  - source="yahoo": Fetch stocks/ETFs from Yahoo Finance (e.g., AAPL, MSFT, SPY)
  - source="crypto": Fetch crypto from CoinGecko (e.g., BTC, ETH, SOL)
  - source="synthetic": Generate GBM simulated data (default)
- get_portfolio: Get detailed information about a stored portfolio
- list_portfolios: List all stored portfolios
- delete_portfolio: Delete a stored portfolio
- update_portfolio_weights: Update allocation weights
- clone_portfolio: Clone a portfolio with optional new weights

## Analysis Tools
- get_portfolio_metrics: Get comprehensive metrics (return, volatility, Sharpe, etc.)
- get_returns: Get daily, log, or cumulative returns
- get_correlation_matrix: Get asset correlation matrix
- get_covariance_matrix: Get asset covariance matrix
- compare_portfolios: Compare multiple portfolios side by side
- get_individual_stock_metrics: Get metrics for each stock separately
- get_drawdown_analysis: Analyze portfolio drawdowns

## Optimization Tools
- optimize_portfolio: Optimize weights using Efficient Frontier
- run_monte_carlo: Run Monte Carlo simulation for optimization
- get_efficient_frontier: Get frontier data points for visualization
- apply_optimization: Apply optimization and update portfolio weights

## Data & Crypto Tools
- generate_price_series: Generate synthetic price data using GBM
- generate_portfolio_scenarios: Generate multiple scenarios for testing
- get_sample_portfolio_data: Get pre-defined sample portfolio data
- get_trending_coins: Get trending cryptocurrencies from CoinGecko
- search_crypto_coins: Search for cryptocurrencies by name/symbol
- get_crypto_info: Get detailed crypto info (price, market cap, 24h change)
- list_crypto_symbols: List supported crypto symbols (BTC, ETH, SOL, etc.)

## Cache Tools
- get_cached_result: Retrieve cached data with pagination support

{cache_instructions()}

## Typical Workflows

### Stock Portfolio
1. create_portfolio(name="stocks", symbols=["AAPL", "MSFT", "GOOG"], source="yahoo")
2. get_portfolio_metrics(name="stocks")
3. optimize_portfolio(name="stocks", method="max_sharpe")
4. apply_optimization(name="stocks", method="max_sharpe")

### Crypto Portfolio
1. get_trending_coins() or search_crypto_coins(query="defi")
2. create_portfolio(name="crypto", symbols=["BTC", "ETH", "SOL"], source="crypto")
3. get_portfolio_metrics(name="crypto")
4. optimize_portfolio(name="crypto", method="min_volatility")

### Compare Strategies
1. Create multiple portfolios with different allocations
2. compare_portfolios(names=["portfolio1", "portfolio2"])

### Working with Large Results
1. Tools returning large data (e.g., generate_price_series, get_returns) return a ref_id + preview
2. Use get_cached_result(ref_id=..., page=1) to paginate through results
3. Pass ref_id to other tools that accept cached references
""",
)

# =============================================================================
# Initialize RefCache
# =============================================================================

cache = RefCache(
    name="portfolio-mcp",
    default_ttl=3600,  # 1 hour TTL
    preview_config=PreviewConfig(
        max_size=500,
        default_strategy=PreviewStrategy.SAMPLE,
    ),
)

# =============================================================================
# Initialize Portfolio Store
# =============================================================================

store = PortfolioStore(cache=cache, namespace="portfolios")

# =============================================================================
# Register Tools (pass cache to tool modules for caching large results)
# =============================================================================

register_portfolio_tools(mcp, store)
register_analysis_tools(mcp, store, cache)
register_optimization_tools(mcp, store, cache)
register_data_tools(mcp, store, cache)

# =============================================================================
# Cache Retrieval Tool
# =============================================================================


@mcp.tool
def get_cached_result(
    ref_id: str,
    page: int | None = None,
    page_size: int | None = None,
) -> dict[str, Any]:
    """Retrieve a cached result, optionally with pagination.

    Use this to:
    - Get a preview of a cached value
    - Paginate through large sequences, price series, or returns data
    - Access specific pages of a cached result

    Args:
        ref_id: The reference ID returned by tools (e.g., from generate_price_series).
        page: Page number (1-indexed). If not provided, returns the default preview.
        page_size: Items per page. Default varies by data type (typically 50).

    Returns:
        Dictionary containing:
        - ref_id: The reference ID
        - preview: The data for the current page/preview
        - preview_strategy: How the preview was generated (sample, truncate, paginate)
        - total_items: Total number of items in the full dataset
        - page: Current page number (if paginated)
        - total_pages: Total pages available (if paginated)

    Example:
        ```
        # Generate large price series (returns ref_id + preview)
        result = generate_price_series(symbols=["AAPL", "GOOG"], days=500)

        # Get page 2 of the cached data
        page2 = get_cached_result(ref_id=result["ref_id"], page=2, page_size=50)

        # Get page 5
        page5 = get_cached_result(ref_id=result["ref_id"], page=5)
        ```
    """
    try:
        # Get with pagination if specified
        response: CacheResponse = cache.get(
            ref_id,
            page=page,
            page_size=page_size,
            actor="agent",  # Agent access - respects permissions
        )

        result: dict[str, Any] = {
            "ref_id": ref_id,
            "preview": response.preview,
            "preview_strategy": response.preview_strategy.value,
            "total_items": response.total_items,
        }

        # Add pagination info if applicable
        if response.page is not None:
            result["page"] = response.page
            result["total_pages"] = response.total_pages

        # Add size info
        if response.original_size:
            result["original_size"] = response.original_size
            result["preview_size"] = response.preview_size

        return result

    except PermissionError as error:
        return {
            "error": "Permission denied",
            "message": str(error),
            "ref_id": ref_id,
        }
    except KeyError:
        return {
            "error": "Not found",
            "message": f"Reference '{ref_id}' not found or expired",
            "ref_id": ref_id,
        }


# =============================================================================
# Health Check
# =============================================================================


@mcp.tool
def health_check() -> dict[str, Any]:
    """Check server health status.

    Returns server health information including cache status
    and number of stored portfolios.

    Returns:
        Health status information.
    """
    portfolios = store.list_portfolios()

    # Detect variant: dev uses 0.0.0-dev, pypi has real version
    # (Docker uses installed package so shows real version too)
    variant = "dev" if __version__ == "0.0.0-dev" else "installed"

    return {
        "status": "healthy",
        "server": "portfolio-mcp",
        "version": __version__,
        "variant": variant,
        "cache": cache.name,
        "portfolios_stored": len(portfolios),
    }
