"""Tests for Pydantic models in FinQuant MCP."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import (
    EfficientFrontierData,
    MonteCarloResult,
    OptimizationResult,
    PortfolioAllocation,
    PortfolioComparison,
    PortfolioCreate,
    PortfolioInfo,
    PortfolioMetrics,
    PriceSeriesData,
    ReturnsData,
)


class TestPortfolioAllocation:
    """Tests for PortfolioAllocation model."""

    def test_valid_allocation(self) -> None:
        """Test creating a valid allocation."""
        allocation = PortfolioAllocation(symbol="AAPL", weight=0.5)
        assert allocation.symbol == "AAPL"
        assert allocation.weight == 0.5

    def test_weight_boundaries(self) -> None:
        """Test weight at boundaries."""
        allocation_zero = PortfolioAllocation(symbol="AAPL", weight=0.0)
        assert allocation_zero.weight == 0.0

        allocation_one = PortfolioAllocation(symbol="AAPL", weight=1.0)
        assert allocation_one.weight == 1.0

    def test_weight_below_zero_fails(self) -> None:
        """Test that weight below 0 fails validation."""
        with pytest.raises(ValidationError):
            PortfolioAllocation(symbol="AAPL", weight=-0.1)

    def test_weight_above_one_fails(self) -> None:
        """Test that weight above 1 fails validation."""
        with pytest.raises(ValidationError):
            PortfolioAllocation(symbol="AAPL", weight=1.1)


class TestPortfolioCreate:
    """Tests for PortfolioCreate model."""

    def test_minimal_valid_create(self) -> None:
        """Test creating with minimal required fields."""
        create = PortfolioCreate(name="test", symbols=["AAPL"])
        assert create.name == "test"
        assert create.symbols == ["AAPL"]
        assert create.weights is None
        assert create.prices is None
        assert create.days == 252
        assert create.risk_free_rate == 0.02
        assert create.seed is None

    def test_full_create(self) -> None:
        """Test creating with all fields."""
        create = PortfolioCreate(
            name="test",
            symbols=["AAPL", "GOOG"],
            weights={"AAPL": 0.6, "GOOG": 0.4},
            prices={"AAPL": [100, 101, 102], "GOOG": [200, 201, 202]},
            days=100,
            risk_free_rate=0.03,
            seed=42,
        )
        assert create.name == "test"
        assert len(create.symbols) == 2
        assert create.weights["AAPL"] == 0.6
        assert create.days == 100
        assert create.seed == 42

    def test_empty_symbols_fails(self) -> None:
        """Test that empty symbols list fails validation."""
        with pytest.raises(ValidationError):
            PortfolioCreate(name="test", symbols=[])

    def test_days_below_minimum_fails(self) -> None:
        """Test that days below 10 fails validation."""
        with pytest.raises(ValidationError):
            PortfolioCreate(name="test", symbols=["AAPL"], days=5)

    def test_days_above_maximum_fails(self) -> None:
        """Test that days above 2520 fails validation."""
        with pytest.raises(ValidationError):
            PortfolioCreate(name="test", symbols=["AAPL"], days=3000)

    def test_risk_free_rate_negative_fails(self) -> None:
        """Test that negative risk-free rate fails validation."""
        with pytest.raises(ValidationError):
            PortfolioCreate(name="test", symbols=["AAPL"], risk_free_rate=-0.01)

    def test_risk_free_rate_too_high_fails(self) -> None:
        """Test that risk-free rate above 0.5 fails validation."""
        with pytest.raises(ValidationError):
            PortfolioCreate(name="test", symbols=["AAPL"], risk_free_rate=0.6)


class TestPortfolioInfo:
    """Tests for PortfolioInfo model."""

    def test_valid_info(self) -> None:
        """Test creating valid portfolio info."""
        info = PortfolioInfo(
            name="test",
            ref_id="cache:abc123",
            symbols=["AAPL", "GOOG"],
            weights={"AAPL": 0.5, "GOOG": 0.5},
            num_days=252,
            created_at="2024-01-01T00:00:00",
        )
        assert info.name == "test"
        assert info.ref_id == "cache:abc123"
        assert len(info.symbols) == 2


class TestPortfolioMetrics:
    """Tests for PortfolioMetrics model."""

    def test_valid_metrics(self) -> None:
        """Test creating valid metrics."""
        metrics = PortfolioMetrics(
            expected_return=0.10,
            volatility=0.20,
            sharpe_ratio=0.40,
            sortino_ratio=0.60,
            value_at_risk=0.05,
            downside_risk=0.15,
            skewness={"AAPL": -0.1, "GOOG": 0.2},
            kurtosis={"AAPL": 3.0, "GOOG": 2.5},
        )
        assert metrics.expected_return == 0.10
        assert metrics.sharpe_ratio == 0.40
        assert metrics.beta is None
        assert metrics.treynor_ratio is None

    def test_with_optional_fields(self) -> None:
        """Test metrics with optional beta and treynor."""
        metrics = PortfolioMetrics(
            expected_return=0.10,
            volatility=0.20,
            sharpe_ratio=0.40,
            sortino_ratio=0.60,
            value_at_risk=0.05,
            downside_risk=0.15,
            skewness={},
            kurtosis={},
            beta=1.2,
            treynor_ratio=0.08,
        )
        assert metrics.beta == 1.2
        assert metrics.treynor_ratio == 0.08


class TestReturnsData:
    """Tests for ReturnsData model."""

    def test_valid_returns(self) -> None:
        """Test creating valid returns data."""
        returns = ReturnsData(
            return_type="daily",
            dates=["2024-01-01", "2024-01-02"],
            returns={"AAPL": [0.01, -0.02], "GOOG": [0.02, 0.01]},
            portfolio_returns=[0.015, -0.005],
        )
        assert returns.return_type == "daily"
        assert len(returns.dates) == 2
        assert len(returns.portfolio_returns) == 2


class TestOptimizationResult:
    """Tests for OptimizationResult model."""

    def test_valid_result(self) -> None:
        """Test creating valid optimization result."""
        result = OptimizationResult(
            method="max_sharpe",
            optimal_weights={"AAPL": 0.6, "GOOG": 0.4},
            expected_return=0.12,
            volatility=0.18,
            sharpe_ratio=0.56,
            original_weights={"AAPL": 0.5, "GOOG": 0.5},
            improvement={
                "return_change": 0.02,
                "volatility_change": -0.02,
                "sharpe_change": 0.10,
            },
        )
        assert result.method == "max_sharpe"
        assert result.optimal_weights["AAPL"] == 0.6
        assert result.sharpe_ratio == 0.56


class TestMonteCarloResult:
    """Tests for MonteCarloResult model."""

    def test_valid_result(self) -> None:
        """Test creating valid Monte Carlo result."""
        result = MonteCarloResult(
            num_trials=5000,
            min_volatility_portfolio={
                "weights": {"AAPL": 0.3, "GOOG": 0.7},
                "volatility": 0.15,
            },
            max_sharpe_portfolio={
                "weights": {"AAPL": 0.8, "GOOG": 0.2},
                "sharpe_ratio": 0.60,
            },
            simulation_ref="cache:simdata123",
        )
        assert result.num_trials == 5000
        assert "weights" in result.min_volatility_portfolio


class TestEfficientFrontierData:
    """Tests for EfficientFrontierData model."""

    def test_valid_frontier(self) -> None:
        """Test creating valid efficient frontier data."""
        # Note: optimal_sharpe and optimal_min_volatility are dict[str, float]
        # so all values must be floats (no nested dicts)
        frontier = EfficientFrontierData(
            frontier_points=[
                {"volatility": 0.10, "expected_return": 0.05},
                {"volatility": 0.15, "expected_return": 0.08},
                {"volatility": 0.20, "expected_return": 0.10},
            ],
            optimal_sharpe={
                "volatility": 0.15,
                "expected_return": 0.08,
                "sharpe": 0.53,
            },
            optimal_min_volatility={
                "volatility": 0.10,
                "expected_return": 0.05,
            },
            individual_stocks=[
                {"symbol": "AAPL", "volatility": 0.25, "expected_return": 0.12},
                {"symbol": "GOOG", "volatility": 0.28, "expected_return": 0.10},
            ],
        )
        assert len(frontier.frontier_points) == 3
        assert len(frontier.individual_stocks) == 2


class TestPriceSeriesData:
    """Tests for PriceSeriesData model."""

    def test_valid_price_series(self) -> None:
        """Test creating valid price series data."""
        data = PriceSeriesData(
            symbols=["AAPL", "GOOG"],
            dates=["2024-01-01", "2024-01-02", "2024-01-03"],
            prices={
                "AAPL": [150.0, 151.0, 152.0],
                "GOOG": [100.0, 101.0, 99.0],
            },
            parameters={
                "days": 3,
                "seed": 42,
                "annual_returns": {"AAPL": 0.08, "GOOG": 0.10},
            },
        )
        assert len(data.symbols) == 2
        assert len(data.dates) == 3
        assert len(data.prices["AAPL"]) == 3


class TestPortfolioComparison:
    """Tests for PortfolioComparison model."""

    def test_valid_comparison(self) -> None:
        """Test creating valid portfolio comparison."""
        metrics_a = PortfolioMetrics(
            expected_return=0.10,
            volatility=0.20,
            sharpe_ratio=0.40,
            sortino_ratio=0.60,
            value_at_risk=0.05,
            downside_risk=0.15,
            skewness={},
            kurtosis={},
        )
        metrics_b = PortfolioMetrics(
            expected_return=0.12,
            volatility=0.25,
            sharpe_ratio=0.40,
            sortino_ratio=0.50,
            value_at_risk=0.07,
            downside_risk=0.18,
            skewness={},
            kurtosis={},
        )
        comparison = PortfolioComparison(
            portfolios=["stocks", "crypto"],
            metrics={"stocks": metrics_a, "crypto": metrics_b},
            rankings={
                "expected_return": ["crypto", "stocks"],
                "sharpe_ratio": ["stocks", "crypto"],
            },
        )
        assert len(comparison.portfolios) == 2
        assert comparison.metrics["stocks"].expected_return == 0.10
        assert comparison.rankings["expected_return"][0] == "crypto"
