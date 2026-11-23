"""Typed market asset entity independent of external APIs."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CryptoAsset:
    """Represents one cryptocurrency and its latest market snapshot.

    This domain entity keeps API details out of the presentation and service layers.
    """

    asset_id: str
    name: str
    symbol: str
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    change_24h: Optional[float] = None
    image: Optional[str] = None
