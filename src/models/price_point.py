"""Historical cryptocurrency price domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PricePoint:
    """Represents a price observation at a particular timestamp."""

    timestamp: datetime
    price: float
