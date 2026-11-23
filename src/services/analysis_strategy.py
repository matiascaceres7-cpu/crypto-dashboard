"""Analysis strategy interface and deterministic market strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Sequence


class AnalysisStrategy(ABC):
    """Strategy-pattern contract for interchangeable price analyses."""

    @abstractmethod
    def analyze(self, prices: Sequence[float]) -> Dict[str, float]:
        """Calculate a named set of metrics from an ordered price sequence."""


class TrendStrategy(AnalysisStrategy):
    """Calculate percentage movement and direction over the supplied history."""

    def analyze(self, prices: Sequence[float]) -> Dict[str, float]:
        """Return total percentage change, using zero for insufficient data."""
        values = [float(price) for price in prices if price is not None]
        if len(values) < 2 or values[0] == 0:
            return {"percentage_change": 0.0, "direction": 0.0}
        change = (values[-1] / values[0] - 1) * 100
        return {"percentage_change": change, "direction": 1.0 if change > 0 else -1.0}


class VolatilityStrategy(AnalysisStrategy):
    """Calculate population volatility and the latest simple moving average."""

    def __init__(self, window: int = 7) -> None:
        if window < 1:
            raise ValueError("window must be greater than zero")
        self.window = window

    def analyze(self, prices: Sequence[float]) -> Dict[str, float]:
        """Return standard deviation of returns and moving average of prices."""
        values = [float(price) for price in prices if price is not None]
        if len(values) < 2:
            return {"volatility": 0.0, "moving_average": values[-1] if values else 0.0}
        returns = [
            (current / previous - 1) * 100
            for previous, current in zip(values, values[1:])
            if previous != 0
        ]
        mean_return = sum(returns) / len(returns) if returns else 0.0
        variance = (
            sum((item - mean_return) ** 2 for item in returns) / len(returns)
            if returns
            else 0.0
        )
        window = values[-self.window :]
        return {
            "volatility": variance ** 0.5,
            "moving_average": sum(window) / len(window),
        }
