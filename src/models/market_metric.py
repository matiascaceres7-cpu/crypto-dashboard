"""Typed point-in-time market metric."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MarketMetric:
    """Represents a calculated named metric and its optional numeric value."""

    name: str
    value: Optional[float]
    unit: str = ""
