"""Provider port used to invert the service's dependency on external APIs."""

from abc import ABC, abstractmethod
from typing import List

from src.models import CryptoAsset, PricePoint


class CryptoDataProvider(ABC):
    """Abstract provider contract implementing DIP for market data access.

    Services depend on this interface rather than a vendor SDK or HTTP client.
    """

    @abstractmethod
    def get_market_assets(self) -> List[CryptoAsset]:
        """Return normalized market assets, or an empty list when unavailable."""

    @abstractmethod
    def get_price_history(self, asset_id: str, days: int) -> List[PricePoint]:
        """Return normalized historical price observations."""
