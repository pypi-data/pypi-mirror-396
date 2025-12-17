"""Data sources for fetching real market data.

This module provides functions to fetch real price data from:
- Yahoo Finance (stocks, ETFs, and crypto via yfinance)
- CoinGecko API (crypto with more detailed data)

The data is returned in a format compatible with create_portfolio.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)

# CoinGecko API base URL (free, no API key required)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Common crypto symbol to CoinGecko ID mapping
CRYPTO_SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "XLM": "stellar",
    "ALGO": "algorand",
    "VET": "vechain",
    "FIL": "filecoin",
    "AAVE": "aave",
    "MKR": "maker",
    "COMP": "compound-governance-token",
    "SNX": "synthetix-network-token",
    "CRV": "curve-dao-token",
    "SUSHI": "sushi",
    "YFI": "yearn-finance",
    "ONE": "harmony",
    "FTM": "fantom",
    "NEAR": "near",
    "ICP": "internet-computer",
    "SAND": "the-sandbox",
    "MANA": "decentraland",
    "AXS": "axie-infinity",
    "ENJ": "enjincoin",
    "CHZ": "chiliz",
    "THETA": "theta-token",
    "XTZ": "tezos",
    "EOS": "eos",
    "TRX": "tron",
    "NEO": "neo",
    "IOTA": "iota",
    "XMR": "monero",
    "DASH": "dash",
    "ZEC": "zcash",
    "ETC": "ethereum-classic",
    "WAVES": "waves",
    "ZIL": "zilliqa",
    "HBAR": "hedera-hashgraph",
    "ENS": "ethereum-name-service",
    "APE": "apecoin",
    "LDO": "lido-dao",
    "OP": "optimism",
    "ARB": "arbitrum",
    "SUI": "sui",
    "SEI": "sei-network",
    "TIA": "celestia",
    "JUP": "jupiter-exchange-solana",
    "PEPE": "pepe",
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "FLOKI": "floki",
}


def _coingecko_request(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make a rate-limited request to CoinGecko API.

    Args:
        endpoint: API endpoint (without base URL).
        params: Query parameters.

    Returns:
        JSON response as dictionary.

    Raises:
        ValueError: If rate limited or request fails.
    """
    url = f"{COINGECKO_API_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 429:
            logger.warning("CoinGecko rate limit hit")
            raise ValueError(
                "CoinGecko rate limit exceeded. Try again in a minute or use fewer symbols."
            )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        logger.error(f"CoinGecko request failed: {error}")
        raise ValueError(f"Failed to fetch crypto data: {error}") from error


def fetch_yahoo_prices(
    symbols: list[str],
    period: str = "1y",
    interval: str = "1d",
) -> dict[str, Any]:
    """Fetch price data from Yahoo Finance.

    Works for stocks, ETFs, and crypto (using -USD suffix).

    Args:
        symbols: List of ticker symbols (e.g., ['AAPL', 'GOOG', 'BTC-USD']).
        period: Data period. Valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max.
        interval: Data interval. Valid values: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo.

    Returns:
        Dictionary containing:
        - symbols: List of symbols
        - dates: List of date strings (ISO format)
        - prices: Dict mapping symbol to list of prices
        - source: "yahoo"
        - period: The period used
        - fetched_at: ISO timestamp

    Raises:
        ValueError: If symbols are invalid or data cannot be fetched.
    """
    import yfinance as yf

    logger.info(f"Fetching Yahoo Finance data for {symbols}, period={period}")

    if not symbols:
        raise ValueError("At least one symbol is required")

    try:
        # Download data for all symbols at once
        data = yf.download(
            tickers=symbols,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,  # Use adjusted close
        )

        if data.empty:
            raise ValueError(f"No data returned for symbols: {symbols}")

        # Handle single vs multiple symbols (yfinance returns different formats)
        if len(symbols) == 1:
            # Single symbol: data is a DataFrame with columns like 'Close', 'Open', etc.
            prices_df = data[["Close"]].rename(columns={"Close": symbols[0]})
        else:
            # Multiple symbols: data has MultiIndex columns like ('Close', 'AAPL')
            if "Close" in data.columns.get_level_values(0):
                prices_df = data["Close"]
            else:
                # Fallback for adjusted data
                prices_df = data.xs("Close", axis=1, level=0)

        # Drop any rows with NaN (missing data)
        prices_df = prices_df.dropna()

        if prices_df.empty:
            raise ValueError(f"No valid price data for symbols: {symbols}")

        # Convert to our format
        dates = [d.strftime("%Y-%m-%d") for d in prices_df.index]
        prices = {
            symbol: prices_df[symbol].tolist()
            for symbol in symbols
            if symbol in prices_df.columns
        }

        # Check if any symbols are missing
        missing = [s for s in symbols if s not in prices]
        if missing:
            logger.warning(f"Missing data for symbols: {missing}")
            if not prices:
                raise ValueError(f"No data available for any symbols: {symbols}")

        return {
            "symbols": list(prices.keys()),
            "dates": dates,
            "prices": prices,
            "source": "yahoo",
            "period": period,
            "interval": interval,
            "fetched_at": datetime.now().isoformat(),
        }

    except Exception as error:
        logger.error(f"Yahoo Finance fetch failed: {error}")
        raise ValueError(f"Failed to fetch Yahoo Finance data: {error}") from error


def fetch_crypto_prices(
    symbols: list[str],
    days: int = 365,
    vs_currency: str = "usd",
) -> dict[str, Any]:
    """Fetch cryptocurrency price data from CoinGecko.

    Args:
        symbols: List of crypto symbols (e.g., ['BTC', 'ETH', 'SOL']).
            Will be mapped to CoinGecko IDs automatically.
        days: Number of days of historical data (1-365).
        vs_currency: Currency to get prices in (e.g., 'usd', 'eur').

    Returns:
        Dictionary containing:
        - symbols: List of symbols
        - dates: List of date strings (ISO format)
        - prices: Dict mapping symbol to list of prices
        - source: "coingecko"
        - vs_currency: The currency used
        - fetched_at: ISO timestamp

    Raises:
        ValueError: If symbols are invalid or data cannot be fetched.
    """
    logger.info(f"Fetching CoinGecko data for {symbols}, days={days}")

    if not symbols:
        raise ValueError("At least one symbol is required")

    days = min(max(1, days), 365)  # Clamp to valid range

    prices_data: dict[str, list[float]] = {}
    dates_set: set[str] = set()
    all_timestamps: dict[str, list[tuple[int, float]]] = {}

    for symbol in symbols:
        # Map symbol to CoinGecko ID
        coin_id = CRYPTO_SYMBOL_TO_ID.get(symbol.upper())
        if coin_id is None:
            # Try using the symbol as-is (lowercase)
            coin_id = symbol.lower()
            logger.warning(
                f"Unknown crypto symbol '{symbol}', trying as CoinGecko ID: {coin_id}"
            )

        try:
            data = _coingecko_request(
                f"coins/{coin_id}/market_chart",
                params={"vs_currency": vs_currency, "days": days},
            )

            # Extract price data (list of [timestamp, price])
            raw_prices = data.get("prices", [])
            if not raw_prices:
                logger.warning(f"No price data for {symbol}")
                continue

            all_timestamps[symbol] = raw_prices

            # Collect dates
            for timestamp, _ in raw_prices:
                date_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
                dates_set.add(date_str)

        except ValueError as error:
            logger.error(f"Failed to fetch {symbol}: {error}")
            continue

    if not all_timestamps:
        raise ValueError(f"Could not fetch data for any symbols: {symbols}")

    # Convert to daily prices (CoinGecko returns hourly for recent data)
    # Group by date and take the last price of each day
    sorted_dates = sorted(dates_set)

    for symbol, raw_prices in all_timestamps.items():
        # Group prices by date
        daily_prices: dict[str, float] = {}
        for timestamp, price in raw_prices:
            date_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
            daily_prices[date_str] = price  # Last price of the day wins

        # Build aligned price list
        symbol_prices = []
        for date_str in sorted_dates:
            if date_str in daily_prices:
                symbol_prices.append(daily_prices[date_str])
            else:
                # Fill missing with previous value (forward fill)
                if symbol_prices:
                    symbol_prices.append(symbol_prices[-1])
                else:
                    symbol_prices.append(0.0)  # Shouldn't happen

        prices_data[symbol] = symbol_prices

    return {
        "symbols": list(prices_data.keys()),
        "dates": sorted_dates,
        "prices": prices_data,
        "source": "coingecko",
        "vs_currency": vs_currency,
        "days": days,
        "fetched_at": datetime.now().isoformat(),
    }


def fetch_prices(
    symbols: list[str],
    source: str = "auto",
    period: str = "1y",
    days: int = 365,
) -> dict[str, Any]:
    """Unified price fetching with automatic source detection.

    Args:
        symbols: List of ticker/crypto symbols.
        source: Data source. Options:
            - "auto": Auto-detect based on symbols (default)
            - "yahoo": Force Yahoo Finance
            - "crypto": Force CoinGecko
        period: Period for Yahoo Finance (e.g., '1y', '6mo', '3mo').
        days: Number of days for CoinGecko.

    Returns:
        Dictionary with symbols, dates, prices, and metadata.

    Raises:
        ValueError: If source is invalid or data cannot be fetched.
    """
    if source == "auto":
        # Auto-detect: if any symbol is in crypto mapping, use crypto
        # If symbols look like crypto pairs (XXX-USD), use yahoo
        is_crypto = any(s.upper() in CRYPTO_SYMBOL_TO_ID for s in symbols)
        has_usd_suffix = any("-USD" in s.upper() for s in symbols)

        source = "crypto" if is_crypto and not has_usd_suffix else "yahoo"

    if source == "yahoo":
        return fetch_yahoo_prices(symbols, period=period)
    elif source == "crypto":
        return fetch_crypto_prices(symbols, days=days)
    else:
        raise ValueError(f"Invalid source: {source}. Use 'auto', 'yahoo', or 'crypto'.")


def convert_to_portfolio_format(
    data: dict[str, Any],
) -> tuple[pd.DataFrame, list[str]]:
    """Convert fetched data to FinQuant portfolio format.

    Args:
        data: Data from fetch_prices or similar.

    Returns:
        Tuple of (prices_df, symbols).
    """
    dates = pd.to_datetime(data["dates"])
    prices_df = pd.DataFrame(data["prices"], index=dates)
    symbols = data["symbols"]
    return prices_df, symbols


def get_crypto_coin_info(coin_id: str) -> dict[str, Any]:
    """Get detailed information about a cryptocurrency.

    Args:
        coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum').

    Returns:
        Dictionary with coin information.
    """
    data = _coingecko_request(
        f"coins/{coin_id}",
        params={
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
        },
    )

    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "symbol": data.get("symbol"),
        "current_price": data.get("market_data", {})
        .get("current_price", {})
        .get("usd"),
        "market_cap": data.get("market_data", {}).get("market_cap", {}).get("usd"),
        "total_volume": data.get("market_data", {}).get("total_volume", {}).get("usd"),
        "high_24h": data.get("market_data", {}).get("high_24h", {}).get("usd"),
        "low_24h": data.get("market_data", {}).get("low_24h", {}).get("usd"),
        "price_change_24h": data.get("market_data", {}).get("price_change_24h"),
        "price_change_percentage_24h": data.get("market_data", {}).get(
            "price_change_percentage_24h"
        ),
        "market_cap_rank": data.get("market_cap_rank"),
        "categories": data.get("categories"),
    }


def get_trending_crypto() -> list[dict[str, Any]]:
    """Get trending cryptocurrencies from CoinGecko.

    Returns:
        List of trending coin information.
    """
    data = _coingecko_request("search/trending")

    return [
        {
            "id": coin["item"]["id"],
            "name": coin["item"]["name"],
            "symbol": coin["item"]["symbol"],
            "market_cap_rank": coin["item"]["market_cap_rank"],
            "score": coin["item"]["score"],
        }
        for coin in data.get("coins", [])
    ]


def search_crypto(query: str) -> list[dict[str, Any]]:
    """Search for cryptocurrencies on CoinGecko.

    Args:
        query: Search query (e.g., 'bitcoin', 'defi').

    Returns:
        List of matching coins.
    """
    data = _coingecko_request("search", params={"query": query})

    return [
        {
            "id": coin["id"],
            "name": coin["name"],
            "symbol": coin["symbol"],
            "market_cap_rank": coin.get("market_cap_rank"),
        }
        for coin in data.get("coins", [])[:20]  # Limit to top 20
    ]


def list_supported_crypto_symbols() -> dict[str, str]:
    """Get the list of supported crypto symbol mappings.

    Returns:
        Dictionary mapping symbols to CoinGecko IDs.
    """
    return CRYPTO_SYMBOL_TO_ID.copy()
