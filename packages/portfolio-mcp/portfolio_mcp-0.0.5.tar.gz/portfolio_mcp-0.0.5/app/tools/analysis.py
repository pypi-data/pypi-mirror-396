"""Analysis tools for FinQuant MCP.

This module provides tools for analyzing portfolios, computing metrics,
calculating returns, and comparing multiple portfolios.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from finquant.returns import cumulative_returns, daily_log_returns, daily_returns

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from mcp_refcache import RefCache

    from app.storage import PortfolioStore


def register_analysis_tools(
    mcp: FastMCP, store: PortfolioStore, cache: RefCache
) -> None:
    """Register analysis tools with the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        store: The portfolio store for persistence.
        cache: The RefCache instance for caching large results.
    """

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def get_portfolio_metrics(name: str) -> dict[str, Any]:
        """Get comprehensive metrics for a portfolio.

        Calculates and returns all key portfolio metrics including
        risk-adjusted returns, volatility measures, and risk metrics.

        Args:
            name: The portfolio name.

        Returns:
            Dictionary containing:
            - expected_return: Annualized expected return
            - volatility: Annualized volatility (standard deviation)
            - sharpe_ratio: Risk-adjusted return (Sharpe)
            - sortino_ratio: Downside risk-adjusted return (Sortino)
            - value_at_risk: VaR at 95% confidence
            - downside_risk: Target downside deviation
            - skewness: Skewness per stock
            - kurtosis: Kurtosis per stock
            - beta: Portfolio beta (if market index available)
            - treynor_ratio: Treynor ratio (if beta available)

        Example:
            ```
            metrics = get_portfolio_metrics(name="tech_stocks")
            print(f"Expected Return: {metrics['expected_return']:.2%}")
            print(f"Volatility: {metrics['volatility']:.2%}")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
                "suggestion": "Use list_portfolios() to see available portfolios",
            }

        metrics = data["metrics"]

        # Format skewness and kurtosis for readability
        skewness = {}
        kurtosis = {}
        if metrics.get("skew"):
            for key, value in metrics["skew"].items():
                # Handle both index-based and column-based keys
                if isinstance(value, dict):
                    skewness.update(value)
                else:
                    skewness[str(key)] = value

        if metrics.get("kurtosis"):
            for key, value in metrics["kurtosis"].items():
                if isinstance(value, dict):
                    kurtosis.update(value)
                else:
                    kurtosis[str(key)] = value

        return {
            "portfolio_name": name,
            "expected_return": metrics["expected_return"],
            "volatility": metrics["volatility"],
            "sharpe_ratio": metrics["sharpe"],
            "sortino_ratio": metrics["sortino"],
            "value_at_risk": metrics["var"],
            "downside_risk": metrics["downside_risk"],
            "skewness": skewness,
            "kurtosis": kurtosis,
            "beta": metrics.get("beta"),
            "treynor_ratio": metrics.get("treynor"),
            "settings": data["settings"],
        }

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def get_returns(
        name: str,
        return_type: str = "daily",
        as_percentage: bool = True,
    ) -> dict[str, Any]:
        """Get returns data for a portfolio.

        Calculates different types of returns from the portfolio's
        price data.

        Args:
            name: The portfolio name.
            return_type: Type of returns to calculate:
                - "daily": Daily percentage returns
                - "log": Daily log returns
                - "cumulative": Cumulative returns from start
            as_percentage: If True, multiply by 100 for percentage display.

        Returns:
            Dictionary containing:
            - return_type: The type of returns calculated
            - dates: List of date strings
            - returns: Dict of returns per symbol
            - portfolio_returns: Weighted portfolio returns
            - statistics: Summary statistics (mean, std, min, max)

        Example:
            ```
            # Get daily returns
            result = get_returns(name="tech_stocks", return_type="daily")

            # Get cumulative returns for growth chart
            result = get_returns(name="tech_stocks", return_type="cumulative")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Rebuild price DataFrame
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Calculate returns based on type
        if return_type == "daily":
            returns_df = daily_returns(prices_df)
        elif return_type == "log":
            returns_df = daily_log_returns(prices_df)
        elif return_type == "cumulative":
            returns_df = cumulative_returns(prices_df)
        else:
            return {
                "error": f"Invalid return_type: {return_type}",
                "valid_types": ["daily", "log", "cumulative"],
            }

        # Drop NaN rows
        returns_df = returns_df.dropna()

        # Get weights for portfolio returns
        weights = {}
        for row in data["allocation"]["values"]:
            weights[row[1]] = row[0] / 100.0

        weights_array = np.array([weights[col] for col in returns_df.columns])

        # Calculate weighted portfolio returns
        portfolio_returns = (returns_df.values @ weights_array).tolist()

        # Apply percentage multiplier if requested
        multiplier = 100.0 if as_percentage else 1.0

        # Build returns dict
        returns_dict = {}
        for col in returns_df.columns:
            returns_dict[col] = (returns_df[col] * multiplier).tolist()

        # Calculate statistics
        stats = {}
        for col in returns_df.columns:
            col_returns = returns_df[col]
            stats[col] = {
                "mean": float(col_returns.mean() * multiplier),
                "std": float(col_returns.std() * multiplier),
                "min": float(col_returns.min() * multiplier),
                "max": float(col_returns.max() * multiplier),
            }

        # Portfolio statistics
        portfolio_series = pd.Series(portfolio_returns)
        stats["portfolio"] = {
            "mean": float(portfolio_series.mean() * multiplier),
            "std": float(portfolio_series.std() * multiplier),
            "min": float(portfolio_series.min() * multiplier),
            "max": float(portfolio_series.max() * multiplier),
        }

        return {
            "portfolio_name": name,
            "return_type": return_type,
            "as_percentage": as_percentage,
            "dates": returns_df.index.strftime("%Y-%m-%d").tolist(),
            "returns": returns_dict,
            "portfolio_returns": [r * multiplier for r in portfolio_returns],
            "statistics": stats,
            "num_observations": len(returns_df),
        }

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def get_correlation_matrix(name: str) -> dict[str, Any]:
        """Get the correlation matrix for portfolio assets.

        Calculates pairwise correlations between all assets in the
        portfolio based on daily returns.

        Args:
            name: The portfolio name.

        Returns:
            Dictionary containing:
            - symbols: List of symbols
            - correlation_matrix: 2D correlation matrix
            - correlations: Readable format with symbol pairs

        Example:
            ```
            result = get_correlation_matrix(name="tech_stocks")
            # Check correlation between GOOG and AMZN
            corr = result['correlations']['GOOG']['AMZN']
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Rebuild price DataFrame
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Calculate daily returns
        returns_df = daily_returns(prices_df).dropna()

        # Calculate correlation matrix
        corr_matrix = returns_df.corr()

        # Build readable correlations dict
        correlations = {}
        symbols = corr_matrix.columns.tolist()
        for symbol in symbols:
            correlations[symbol] = {}
            for other in symbols:
                correlations[symbol][other] = float(corr_matrix.loc[symbol, other])

        return {
            "portfolio_name": name,
            "symbols": symbols,
            "correlation_matrix": corr_matrix.values.tolist(),
            "correlations": correlations,
        }

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def get_covariance_matrix(name: str, annualized: bool = True) -> dict[str, Any]:
        """Get the covariance matrix for portfolio assets.

        Calculates pairwise covariances between all assets in the
        portfolio based on daily returns.

        Args:
            name: The portfolio name.
            annualized: If True, annualize the covariance (multiply by 252).

        Returns:
            Dictionary containing:
            - symbols: List of symbols
            - covariance_matrix: 2D covariance matrix
            - variances: Individual asset variances (diagonal)

        Example:
            ```
            result = get_covariance_matrix(name="tech_stocks")
            print(f"GOOG variance: {result['variances']['GOOG']}")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Rebuild price DataFrame
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Calculate daily returns
        returns_df = daily_returns(prices_df).dropna()

        # Calculate covariance matrix
        cov_matrix = returns_df.cov()

        # Annualize if requested
        if annualized:
            cov_matrix = cov_matrix * 252

        # Extract variances
        symbols = cov_matrix.columns.tolist()
        variances = {
            symbol: float(cov_matrix.loc[symbol, symbol]) for symbol in symbols
        }

        return {
            "portfolio_name": name,
            "symbols": symbols,
            "annualized": annualized,
            "covariance_matrix": cov_matrix.values.tolist(),
            "variances": variances,
        }

    @mcp.tool
    def compare_portfolios(names: list[str]) -> dict[str, Any]:
        """Compare multiple portfolios side by side.

        Retrieves metrics for multiple portfolios and ranks them
        by key performance indicators.

        Args:
            names: List of portfolio names to compare.

        Returns:
            Dictionary containing:
            - portfolios: Dict of metrics per portfolio
            - rankings: Rankings by each metric
            - best_by_metric: Best portfolio for each metric

        Example:
            ```
            result = compare_portfolios(
                names=["stocks", "crypto", "metals"]
            )
            print(f"Best Sharpe: {result['best_by_metric']['sharpe_ratio']}")
            ```
        """
        if len(names) < 2:
            return {
                "error": "Need at least 2 portfolios to compare",
            }

        # Collect metrics for all portfolios
        portfolios_data = {}
        errors = []

        for name in names:
            data = store.get(name)
            if data is None:
                errors.append(f"Portfolio '{name}' not found")
                continue
            portfolios_data[name] = data["metrics"]

        if errors:
            return {
                "error": "Some portfolios not found",
                "details": errors,
                "found": list(portfolios_data.keys()),
            }

        # Build comparison structure
        portfolios = {}
        for name, metrics in portfolios_data.items():
            portfolios[name] = {
                "expected_return": metrics["expected_return"],
                "volatility": metrics["volatility"],
                "sharpe_ratio": metrics["sharpe"],
                "sortino_ratio": metrics["sortino"],
                "value_at_risk": metrics["var"],
                "downside_risk": metrics["downside_risk"],
            }

        # Create rankings
        metrics_to_rank = [
            ("expected_return", True),  # Higher is better
            ("volatility", False),  # Lower is better
            ("sharpe_ratio", True),
            ("sortino_ratio", True),
            ("value_at_risk", False),  # Lower (less negative) is better
            ("downside_risk", False),
        ]

        rankings = {}
        best_by_metric = {}

        for metric, higher_is_better in metrics_to_rank:
            sorted_names = sorted(
                portfolios_data.keys(),
                key=lambda n: portfolios[n][metric],
                reverse=higher_is_better,
            )
            rankings[metric] = sorted_names
            best_by_metric[metric] = sorted_names[0]

        return {
            "portfolios": portfolios,
            "rankings": rankings,
            "best_by_metric": best_by_metric,
            "num_portfolios": len(portfolios),
        }

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def get_individual_stock_metrics(name: str) -> dict[str, Any]:
        """Get metrics for each individual stock in a portfolio.

        Calculates return and volatility metrics for each stock
        separately, useful for identifying best/worst performers.

        Args:
            name: The portfolio name.

        Returns:
            Dictionary containing metrics per stock:
            - mean_return: Average daily return (annualized)
            - volatility: Standard deviation (annualized)
            - sharpe_ratio: Individual Sharpe ratio
            - weight: Current allocation weight

        Example:
            ```
            result = get_individual_stock_metrics(name="tech_stocks")
            for symbol, metrics in result['stocks'].items():
                print(f"{symbol}: Return={metrics['mean_return']:.2%}")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Rebuild price DataFrame
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Calculate daily returns
        returns_df = daily_returns(prices_df).dropna()

        # Get weights
        weights = {}
        for row in data["allocation"]["values"]:
            weights[row[1]] = row[0] / 100.0

        risk_free_rate = data["settings"]["risk_free_rate"]

        # Calculate metrics per stock
        stocks = {}
        for symbol in returns_df.columns:
            daily_mean = returns_df[symbol].mean()
            daily_std = returns_df[symbol].std()

            annual_return = daily_mean * 252
            annual_vol = daily_std * np.sqrt(252)

            sharpe = (
                (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else 0
            )

            stocks[symbol] = {
                "mean_return": float(annual_return),
                "volatility": float(annual_vol),
                "sharpe_ratio": float(sharpe),
                "weight": weights.get(symbol, 0),
                "daily_mean": float(daily_mean),
                "daily_std": float(daily_std),
            }

        # Sort by Sharpe ratio
        sorted_stocks = sorted(
            stocks.items(), key=lambda x: x[1]["sharpe_ratio"], reverse=True
        )

        return {
            "portfolio_name": name,
            "stocks": stocks,
            "ranking_by_sharpe": [s[0] for s in sorted_stocks],
            "best_performer": sorted_stocks[0][0] if sorted_stocks else None,
            "worst_performer": sorted_stocks[-1][0] if sorted_stocks else None,
            "risk_free_rate": risk_free_rate,
        }

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def get_drawdown_analysis(name: str) -> dict[str, Any]:
        """Analyze portfolio drawdowns.

        Calculates maximum drawdown and drawdown periods for the
        portfolio, useful for risk assessment.

        Args:
            name: The portfolio name.

        Returns:
            Dictionary containing:
            - max_drawdown: Maximum drawdown percentage
            - max_drawdown_period: Start and end dates of max drawdown
            - current_drawdown: Current drawdown from peak
            - recovery_needed: Percentage gain needed to recover

        Example:
            ```
            result = get_drawdown_analysis(name="tech_stocks")
            print(f"Max Drawdown: {result['max_drawdown']:.2%}")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Rebuild price DataFrame
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Get weights
        weights = {}
        for row in data["allocation"]["values"]:
            weights[row[1]] = row[0] / 100.0

        weights_array = np.array([weights[col] for col in prices_df.columns])

        # Calculate portfolio value series (weighted)
        # Normalize prices to start at 1
        normalized = prices_df / prices_df.iloc[0]
        portfolio_value = normalized.values @ weights_array

        # Calculate running maximum
        running_max = np.maximum.accumulate(portfolio_value)

        # Calculate drawdown
        drawdown = (portfolio_value - running_max) / running_max

        # Find maximum drawdown
        max_dd_idx = np.argmin(drawdown)
        max_drawdown = float(drawdown[max_dd_idx])

        # Find the peak before max drawdown
        peak_idx = np.argmax(portfolio_value[: max_dd_idx + 1])

        # Find recovery point (if any)
        recovery_idx = None
        for i in range(max_dd_idx, len(portfolio_value)):
            if portfolio_value[i] >= portfolio_value[peak_idx]:
                recovery_idx = i
                break

        dates = prices_df.index

        return {
            "portfolio_name": name,
            "max_drawdown": max_drawdown,
            "max_drawdown_percentage": f"{max_drawdown * 100:.2f}%",
            "max_drawdown_period": {
                "peak_date": dates[peak_idx].strftime("%Y-%m-%d"),
                "trough_date": dates[max_dd_idx].strftime("%Y-%m-%d"),
                "recovery_date": (
                    dates[recovery_idx].strftime("%Y-%m-%d")
                    if recovery_idx
                    else "Not recovered"
                ),
                "days_to_trough": max_dd_idx - peak_idx,
                "days_to_recovery": (
                    recovery_idx - max_dd_idx if recovery_idx else None
                ),
            },
            "current_drawdown": float(drawdown[-1]),
            "current_drawdown_percentage": f"{drawdown[-1] * 100:.2f}%",
            "recovery_needed": (
                float(-drawdown[-1] / (1 + drawdown[-1])) if drawdown[-1] < 0 else 0
            ),
            "drawdown_series": {
                "dates": dates.strftime("%Y-%m-%d").tolist(),
                "values": drawdown.tolist(),
            },
        }
