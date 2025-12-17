"""Pydantic models for FinQuant MCP input/output data structures.

This module defines the data models used for tool inputs and outputs,
ensuring type safety and clear documentation for the MCP interface.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PortfolioAllocation(BaseModel):
    """Represents a single stock allocation in a portfolio."""

    symbol: str = Field(description="Stock symbol (e.g., 'GOOG', 'AMZN')")
    weight: float = Field(
        description="Allocation weight (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )


class PortfolioCreate(BaseModel):
    """Input model for creating a new portfolio."""

    name: str = Field(
        description="Unique name for the portfolio (e.g., 'stocks', 'crypto')"
    )
    symbols: list[str] = Field(
        description="List of stock/asset symbols",
        min_length=1,
    )
    weights: dict[str, float] | None = Field(
        default=None,
        description="Optional allocation weights per symbol. If None, equal weights are used.",
    )
    prices: dict[str, list[float]] | None = Field(
        default=None,
        description="Optional price data per symbol. If None, synthetic data is generated.",
    )
    days: int = Field(
        default=252,
        description="Number of trading days for synthetic data generation",
        ge=10,
        le=2520,
    )
    risk_free_rate: float = Field(
        default=0.02,
        description="Risk-free rate for Sharpe ratio calculations",
        ge=0.0,
        le=0.5,
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for reproducible synthetic data generation",
    )


class PortfolioInfo(BaseModel):
    """Summary information about a stored portfolio."""

    name: str = Field(description="Portfolio name")
    ref_id: str = Field(description="RefCache reference ID")
    symbols: list[str] = Field(description="List of symbols in the portfolio")
    weights: dict[str, float] = Field(description="Current allocation weights")
    num_days: int = Field(description="Number of trading days in the data")
    created_at: str = Field(description="ISO timestamp when portfolio was created")


class PortfolioMetrics(BaseModel):
    """Comprehensive portfolio metrics."""

    expected_return: float = Field(description="Expected annualized return")
    volatility: float = Field(description="Annualized volatility (standard deviation)")
    sharpe_ratio: float = Field(description="Sharpe ratio (risk-adjusted return)")
    sortino_ratio: float = Field(description="Sortino ratio (downside risk-adjusted)")
    value_at_risk: float = Field(description="Value at Risk (95% confidence)")
    downside_risk: float = Field(description="Downside deviation")
    skewness: dict[str, float] = Field(description="Skewness per stock")
    kurtosis: dict[str, float] = Field(description="Kurtosis per stock")
    beta: float | None = Field(
        default=None, description="Portfolio beta (if market index provided)"
    )
    treynor_ratio: float | None = Field(
        default=None, description="Treynor ratio (if beta available)"
    )


class ReturnsData(BaseModel):
    """Returns data for a portfolio."""

    return_type: str = Field(
        description="Type of returns: 'daily', 'log', or 'cumulative'"
    )
    dates: list[str] = Field(description="List of date strings (ISO format)")
    returns: dict[str, list[float]] = Field(description="Returns per symbol")
    portfolio_returns: list[float] = Field(description="Weighted portfolio returns")


class OptimizationResult(BaseModel):
    """Result of portfolio optimization."""

    method: str = Field(description="Optimization method used")
    optimal_weights: dict[str, float] = Field(description="Optimal allocation weights")
    expected_return: float = Field(description="Expected return of optimal portfolio")
    volatility: float = Field(description="Volatility of optimal portfolio")
    sharpe_ratio: float = Field(description="Sharpe ratio of optimal portfolio")
    original_weights: dict[str, float] = Field(description="Original portfolio weights")
    improvement: dict[str, float] = Field(
        description="Improvement metrics (return_change, volatility_change, sharpe_change)"
    )


class MonteCarloResult(BaseModel):
    """Result of Monte Carlo simulation."""

    num_trials: int = Field(description="Number of simulation trials")
    min_volatility_portfolio: dict[str, Any] = Field(
        description="Portfolio with minimum volatility"
    )
    max_sharpe_portfolio: dict[str, Any] = Field(
        description="Portfolio with maximum Sharpe ratio"
    )
    simulation_ref: str = Field(
        description="RefCache reference to full simulation data (paginated)"
    )


class EfficientFrontierData(BaseModel):
    """Data points for plotting the efficient frontier."""

    frontier_points: list[dict[str, float]] = Field(
        description="List of {volatility, expected_return} points on the frontier"
    )
    optimal_sharpe: dict[str, float] = Field(
        description="Optimal Sharpe ratio portfolio point"
    )
    optimal_min_volatility: dict[str, float] = Field(
        description="Minimum volatility portfolio point"
    )
    individual_stocks: list[dict[str, Any]] = Field(
        description="Individual stock positions {symbol, volatility, expected_return}"
    )


class PriceSeriesData(BaseModel):
    """Generated or fetched price series data."""

    symbols: list[str] = Field(description="List of symbols")
    dates: list[str] = Field(description="List of date strings (ISO format)")
    prices: dict[str, list[float]] = Field(description="Price series per symbol")
    parameters: dict[str, Any] = Field(
        description="Generation parameters (drift, volatility, seed, etc.)"
    )


class PortfolioComparison(BaseModel):
    """Comparison of multiple portfolios."""

    portfolios: list[str] = Field(description="List of portfolio names compared")
    metrics: dict[str, PortfolioMetrics] = Field(description="Metrics per portfolio")
    rankings: dict[str, list[str]] = Field(
        description="Rankings by metric (e.g., 'sharpe_ratio': ['crypto', 'stocks', 'metals'])"
    )
