"""Optimization tools for FinQuant MCP.

This module provides tools for portfolio optimization including
Efficient Frontier analysis and Monte Carlo simulation.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from finquant.efficient_frontier import EfficientFrontier
from finquant.monte_carlo import MonteCarloOpt
from finquant.portfolio import build_portfolio
from finquant.returns import daily_returns

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from mcp_refcache import RefCache

    from app.storage import PortfolioStore


def register_optimization_tools(
    mcp: FastMCP, store: PortfolioStore, cache: RefCache
) -> None:
    """Register optimization tools with the FastMCP server.

    Args:
        mcp: The FastMCP server instance.
        store: The portfolio store for persistence.
        cache: The RefCache instance for caching large results.
    """

    def _optimize_portfolio_impl(
        name: str,
        method: str = "max_sharpe",
        target_return: float | None = None,
        target_volatility: float | None = None,
    ) -> dict[str, Any]:
        """Internal implementation for portfolio optimization.

        This is extracted so it can be called by both optimize_portfolio tool
        and apply_optimization tool without going through the MCP tool wrapper.
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Validate method
        valid_methods = [
            "max_sharpe",
            "min_volatility",
            "efficient_return",
            "efficient_volatility",
        ]
        if method not in valid_methods:
            return {
                "error": f"Invalid method: {method}",
                "valid_methods": valid_methods,
            }

        # Validate target parameters
        if method == "efficient_return" and target_return is None:
            return {
                "error": "target_return is required for 'efficient_return' method",
            }
        if method == "efficient_volatility" and target_volatility is None:
            return {
                "error": "target_volatility is required for 'efficient_volatility' method",
            }

        # Rebuild portfolio
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )
        allocation_df = pd.DataFrame(
            data=data["allocation"]["values"],
            columns=data["allocation"]["columns"],
        )
        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = data["settings"]["risk_free_rate"]

        # Store original metrics
        original_metrics = {
            "expected_return": float(portfolio.expected_return),
            "volatility": float(portfolio.volatility),
            "sharpe_ratio": float(portfolio.sharpe),
        }

        # Get weights
        original_weights = {}
        for row in data["allocation"]["values"]:
            original_weights[row[1]] = row[0] / 100.0

        # Calculate returns for EfficientFrontier
        returns_df = daily_returns(prices_df).dropna()
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()

        # Create EfficientFrontier
        ef = EfficientFrontier(
            mean_returns=mean_returns,
            cov_matrix=cov_matrix,
            risk_free_rate=portfolio.risk_free_rate,
            freq=portfolio.freq,
        )

        # Perform optimization based on method
        try:
            if method == "max_sharpe":
                opt_weights = ef.maximum_sharpe_ratio()
            elif method == "min_volatility":
                opt_weights = ef.minimum_volatility()
            elif method == "efficient_return":
                opt_weights = ef.efficient_return(target_return)
            elif method == "efficient_volatility":
                opt_weights = ef.efficient_volatility(target_volatility)
            else:
                return {"error": f"Unknown method: {method}"}
        except Exception as e:
            return {
                "error": f"Optimization failed: {e!s}",
                "suggestion": "Try adjusting target values or using a different method",
            }

        # Calculate optimal portfolio metrics
        # opt_weights is a DataFrame with symbols as index and 'Allocation' column
        opt_weights_array = np.array(
            [opt_weights.loc[col, "Allocation"] for col in prices_df.columns]
        )
        opt_return = float(np.sum(mean_returns * opt_weights_array) * 252)
        opt_vol = float(
            np.sqrt(
                np.dot(opt_weights_array.T, np.dot(cov_matrix * 252, opt_weights_array))
            )
        )
        opt_sharpe = (opt_return - portfolio.risk_free_rate) / opt_vol

        # Build optimal weights dict
        optimal_weights = {
            symbol: float(opt_weights.loc[symbol, "Allocation"])
            for symbol in prices_df.columns
        }

        # Calculate improvement
        improvement = {
            "return_change": opt_return - original_metrics["expected_return"],
            "volatility_change": opt_vol - original_metrics["volatility"],
            "sharpe_ratio_change": opt_sharpe - original_metrics["sharpe_ratio"],
        }

        return {
            "portfolio_name": name,
            "method": method,
            "optimal_weights": optimal_weights,
            "expected_return": opt_return,
            "volatility": opt_vol,
            "sharpe_ratio": opt_sharpe,
            "original": {
                "weights": original_weights,
                "expected_return": original_metrics["expected_return"],
                "volatility": original_metrics["volatility"],
                "sharpe_ratio": original_metrics["sharpe_ratio"],
            },
            "improvement": improvement,
            "target": {
                "return": target_return,
                "volatility": target_volatility,
            },
            "optimized_at": datetime.now().isoformat(),
        }

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def optimize_portfolio(
        name: str,
        method: str = "max_sharpe",
        target_return: float | None = None,
        target_volatility: float | None = None,
    ) -> dict[str, Any]:
        """Optimize portfolio weights using Efficient Frontier.

        Finds optimal portfolio weights based on the specified optimization
        method. Uses numerical optimization (scipy) to find the solution.

        Args:
            name: The portfolio name.
            method: Optimization method:
                - "max_sharpe": Maximize Sharpe ratio (default)
                - "min_volatility": Minimize portfolio volatility
                - "efficient_return": Minimize volatility for target return
                - "efficient_volatility": Maximize return for target volatility
            target_return: Required for "efficient_return" method.
                The target annualized return to achieve.
            target_volatility: Required for "efficient_volatility" method.
                The target annualized volatility.

        Returns:
            Dictionary containing:
            - method: Optimization method used
            - optimal_weights: Dict of optimal weights per symbol
            - expected_return: Expected return of optimal portfolio
            - volatility: Volatility of optimal portfolio
            - sharpe_ratio: Sharpe ratio of optimal portfolio
            - original: Original portfolio metrics for comparison
            - improvement: Improvement over original portfolio

        Example:
            ```
            # Maximize Sharpe ratio
            result = optimize_portfolio(name="tech_stocks", method="max_sharpe")

            # Minimize volatility
            result = optimize_portfolio(name="tech_stocks", method="min_volatility")

            # Target 15% return with minimum volatility
            result = optimize_portfolio(
                name="tech_stocks",
                method="efficient_return",
                target_return=0.15
            )
            ```
        """
        return _optimize_portfolio_impl(
            name=name,
            method=method,
            target_return=target_return,
            target_volatility=target_volatility,
        )

    @mcp.tool
    def run_monte_carlo(
        name: str,
        num_trials: int = 5000,
    ) -> dict[str, Any]:
        """Run Monte Carlo simulation to find optimal portfolios.

        Generates random portfolio weight combinations and evaluates
        their risk/return characteristics to find optimal allocations.

        Note: This is computationally intensive. For large num_trials,
        consider using the Efficient Frontier method instead which
        provides mathematically optimal solutions.

        Args:
            name: The portfolio name.
            num_trials: Number of random portfolios to generate (default: 5000).

        Returns:
            Dictionary containing:
            - num_trials: Number of simulations run
            - min_volatility_portfolio: Portfolio with minimum volatility
            - max_sharpe_portfolio: Portfolio with maximum Sharpe ratio
            - simulation_stats: Statistics about the simulation
            - sample_portfolios: Sample of generated portfolios

        Example:
            ```
            result = run_monte_carlo(name="tech_stocks", num_trials=10000)
            best = result['max_sharpe_portfolio']
            print(f"Best Sharpe: {best['sharpe_ratio']:.2f}")
            print(f"Optimal weights: {best['weights']}")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        # Limit trials for performance
        if num_trials > 50000:
            return {
                "error": "num_trials exceeds maximum of 50000",
                "suggestion": "Use smaller num_trials or use optimize_portfolio() for exact solution",
            }

        # Rebuild portfolio
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )
        allocation_df = pd.DataFrame(
            data=data["allocation"]["values"],
            columns=data["allocation"]["columns"],
        )
        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = data["settings"]["risk_free_rate"]

        # Calculate returns
        returns_df = daily_returns(prices_df).dropna()

        # Get initial weights
        initial_weights = np.array(
            [row[0] / 100.0 for row in data["allocation"]["values"]]
        )

        # Run Monte Carlo optimization
        mc = MonteCarloOpt(
            returns=returns_df,
            num_trials=num_trials,
            risk_free_rate=portfolio.risk_free_rate,
            freq=portfolio.freq,
            initial_weights=initial_weights,
        )

        opt_weights, opt_results = mc.optimisation()

        # Extract results
        symbols = prices_df.columns.tolist()

        min_vol_weights = opt_weights.loc["Min Volatility"].to_dict()
        max_sharpe_weights = opt_weights.loc["Max Sharpe Ratio"].to_dict()

        min_vol_results = opt_results.loc["Min Volatility"].to_dict()
        max_sharpe_results = opt_results.loc["Max Sharpe Ratio"].to_dict()

        # Get simulation statistics
        sim_returns = mc.df_results["Expected Return"]
        sim_volatility = mc.df_results["Volatility"]
        sim_sharpe = mc.df_results["Sharpe Ratio"]

        # Sample portfolios for visualization (take every nth)
        sample_size = min(100, num_trials)
        step = max(1, num_trials // sample_size)
        sample_portfolios = []
        for i in range(0, num_trials, step):
            if len(sample_portfolios) >= sample_size:
                break
            sample_portfolios.append(
                {
                    "expected_return": float(mc.df_results.iloc[i]["Expected Return"]),
                    "volatility": float(mc.df_results.iloc[i]["Volatility"]),
                    "sharpe_ratio": float(mc.df_results.iloc[i]["Sharpe Ratio"]),
                }
            )

        return {
            "portfolio_name": name,
            "num_trials": num_trials,
            "min_volatility_portfolio": {
                "weights": {s: float(min_vol_weights[s]) for s in symbols},
                "expected_return": float(min_vol_results["Expected Return"]),
                "volatility": float(min_vol_results["Volatility"]),
                "sharpe_ratio": float(min_vol_results["Sharpe Ratio"]),
            },
            "max_sharpe_portfolio": {
                "weights": {s: float(max_sharpe_weights[s]) for s in symbols},
                "expected_return": float(max_sharpe_results["Expected Return"]),
                "volatility": float(max_sharpe_results["Volatility"]),
                "sharpe_ratio": float(max_sharpe_results["Sharpe Ratio"]),
            },
            "simulation_stats": {
                "return_range": [float(sim_returns.min()), float(sim_returns.max())],
                "volatility_range": [
                    float(sim_volatility.min()),
                    float(sim_volatility.max()),
                ],
                "sharpe_range": [float(sim_sharpe.min()), float(sim_sharpe.max())],
                "return_mean": float(sim_returns.mean()),
                "volatility_mean": float(sim_volatility.mean()),
                "sharpe_mean": float(sim_sharpe.mean()),
            },
            "sample_portfolios": sample_portfolios,
            "completed_at": datetime.now().isoformat(),
        }

    @mcp.tool
    @cache.cached(
        namespace="public",
        ttl=None,  # Deterministic - infinite TTL
    )
    def get_efficient_frontier(
        name: str,
        num_points: int = 50,
    ) -> dict[str, Any]:
        """Generate efficient frontier data points for visualization.

        Calculates points along the efficient frontier, which represents
        the set of optimal portfolios offering the highest expected return
        for a given level of risk.

        Args:
            name: The portfolio name.
            num_points: Number of points to generate along the frontier.

        Returns:
            Dictionary containing:
            - frontier_points: List of {volatility, expected_return} points
            - optimal_sharpe: Maximum Sharpe ratio portfolio
            - optimal_min_volatility: Minimum volatility portfolio
            - individual_stocks: Individual stock positions
            - current_portfolio: Current portfolio position

        Example:
            ```
            result = get_efficient_frontier(name="tech_stocks", num_points=100)

            # Plot the frontier
            for point in result['frontier_points']:
                print(f"Vol: {point['volatility']:.2%}, Return: {point['expected_return']:.2%}")
            ```
        """
        data = store.get(name)
        if data is None:
            return {
                "error": f"Portfolio '{name}' not found",
            }

        if num_points < 10 or num_points > 500:
            return {
                "error": "num_points must be between 10 and 500",
            }

        # Rebuild portfolio
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Calculate returns
        returns_df = daily_returns(prices_df).dropna()
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()

        risk_free_rate = data["settings"]["risk_free_rate"]
        freq = data["settings"]["freq"]

        # Create EfficientFrontier
        ef = EfficientFrontier(
            mean_returns=mean_returns,
            cov_matrix=cov_matrix,
            risk_free_rate=risk_free_rate,
            freq=freq,
        )

        # Get optimal portfolios (returns DataFrame with symbol index and 'Allocation' column)
        min_vol_weights_df = ef.minimum_volatility()
        max_sharpe_weights_df = ef.maximum_sharpe_ratio()

        # Calculate metrics for optimal portfolios
        symbols = prices_df.columns.tolist()

        def weights_df_to_dict(weights_df: pd.DataFrame) -> dict:
            """Convert EfficientFrontier weights DataFrame to dict."""
            return {
                symbol: float(weights_df.loc[symbol, "Allocation"])
                for symbol in symbols
            }

        def calc_metrics(weights_dict: dict) -> dict:
            w = np.array([weights_dict[s] for s in symbols])
            ret = float(np.sum(mean_returns * w) * freq)
            vol = float(np.sqrt(np.dot(w.T, np.dot(cov_matrix * freq, w))))
            sharpe = (ret - risk_free_rate) / vol if vol > 0 else 0
            return {
                "expected_return": ret,
                "volatility": vol,
                "sharpe_ratio": sharpe,
                "weights": {s: float(weights_dict[s]) for s in symbols},
            }

        min_vol_metrics = calc_metrics(weights_df_to_dict(min_vol_weights_df))
        max_sharpe_metrics = calc_metrics(weights_df_to_dict(max_sharpe_weights_df))

        # Generate frontier points
        # Get return range
        min_return = min_vol_metrics["expected_return"]
        max_return = max_sharpe_metrics["expected_return"] * 1.2  # Extend a bit

        # Generate points
        frontier_points = []
        target_returns = np.linspace(min_return, max_return, num_points)

        for target in target_returns:
            try:
                weights_df = ef.efficient_return(target)
                metrics = calc_metrics(weights_df_to_dict(weights_df))
                frontier_points.append(
                    {
                        "volatility": metrics["volatility"],
                        "expected_return": metrics["expected_return"],
                        "sharpe_ratio": metrics["sharpe_ratio"],
                    }
                )
            except Exception:
                # Skip points that can't be solved
                continue

        # Calculate individual stock positions
        individual_stocks = []
        for i, symbol in enumerate(symbols):
            stock_return = float(mean_returns.iloc[i] * freq)
            stock_vol = float(np.sqrt(cov_matrix.iloc[i, i] * freq))
            individual_stocks.append(
                {
                    "symbol": symbol,
                    "volatility": stock_vol,
                    "expected_return": stock_return,
                }
            )

        # Current portfolio position
        current_weights = {}
        for row in data["allocation"]["values"]:
            current_weights[row[1]] = row[0] / 100.0
        current_metrics = calc_metrics(current_weights)

        return {
            "portfolio_name": name,
            "num_points": len(frontier_points),
            "frontier_points": frontier_points,
            "optimal_sharpe": max_sharpe_metrics,
            "optimal_min_volatility": min_vol_metrics,
            "individual_stocks": individual_stocks,
            "current_portfolio": current_metrics,
            "risk_free_rate": risk_free_rate,
            "generated_at": datetime.now().isoformat(),
        }

    @mcp.tool
    def apply_optimization(
        name: str,
        method: str = "max_sharpe",
        target_return: float | None = None,
        target_volatility: float | None = None,
    ) -> dict[str, Any]:
        """Apply optimization and update portfolio weights.

        Optimizes the portfolio using the specified method and updates
        the stored portfolio with the new optimal weights.

        Args:
            name: The portfolio name.
            method: Optimization method (same as optimize_portfolio).
            target_return: Target return for "efficient_return" method.
            target_volatility: Target volatility for "efficient_volatility" method.

        Returns:
            Updated portfolio information with new weights and metrics.

        Example:
            ```
            result = apply_optimization(name="tech_stocks", method="max_sharpe")
            print(f"New Sharpe: {result['new_metrics']['sharpe_ratio']:.2f}")
            ```
        """
        # First, run optimization using internal implementation
        opt_result = _optimize_portfolio_impl(
            name=name,
            method=method,
            target_return=target_return,
            target_volatility=target_volatility,
        )

        if "error" in opt_result:
            return opt_result

        # Get portfolio data
        data = store.get(name)
        if data is None:
            return {"error": f"Portfolio '{name}' not found"}

        # Rebuild with new weights
        prices_df = pd.DataFrame(
            data=data["prices"]["values"],
            index=pd.to_datetime(data["prices"]["index"]),
            columns=data["prices"]["columns"],
        )

        # Create new allocation DataFrame
        optimal_weights = opt_result["optimal_weights"]
        symbols = prices_df.columns.tolist()
        allocation_data = [
            {"Allocation": optimal_weights[s] * 100, "Name": s} for s in symbols
        ]
        allocation_df = pd.DataFrame(allocation_data)

        # Rebuild portfolio
        portfolio = build_portfolio(data=prices_df, pf_allocation=allocation_df)
        portfolio.risk_free_rate = data["settings"]["risk_free_rate"]

        # Update store
        store.delete(name)
        ref_id = store.store(portfolio, name)

        return {
            "portfolio_name": name,
            "ref_id": ref_id,
            "method": method,
            "old_weights": opt_result["original"]["weights"],
            "new_weights": optimal_weights,
            "old_metrics": {
                "expected_return": opt_result["original"]["expected_return"],
                "volatility": opt_result["original"]["volatility"],
                "sharpe_ratio": opt_result["original"]["sharpe_ratio"],
            },
            "new_metrics": {
                "expected_return": float(portfolio.expected_return),
                "volatility": float(portfolio.volatility),
                "sharpe_ratio": float(portfolio.sharpe),
            },
            "improvement": opt_result["improvement"],
            "applied_at": datetime.now().isoformat(),
        }
