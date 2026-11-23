"""Unit tests for interchangeable analysis strategies."""

import pytest

from src.services.analysis_strategy import TrendStrategy, VolatilityStrategy


def test_trend_strategy_calculates_change_and_direction():
    result = TrendStrategy().analyze([100, 110])
    assert result["percentage_change"] == pytest.approx(10)
    assert result["direction"] == 1


def test_trend_strategy_handles_insufficient_and_zero_starting_price():
    strategy = TrendStrategy()
    assert strategy.analyze([])["percentage_change"] == 0
    assert strategy.analyze([0, 10])["direction"] == 0


def test_volatility_strategy_calculates_volatility_and_moving_average():
    result = VolatilityStrategy(window=2).analyze([100, 110, 121])
    assert result["volatility"] == pytest.approx(0)
    assert result["moving_average"] == pytest.approx(115.5)


def test_volatility_strategy_handles_empty_prices_and_invalid_window():
    assert VolatilityStrategy().analyze([])["moving_average"] == 0
    with pytest.raises(ValueError):
        VolatilityStrategy(window=0)
