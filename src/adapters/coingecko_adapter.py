"""CoinGecko HTTP adapter translating vendor payloads into domain entities."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from src.adapters.crypto_data_provider import CryptoDataProvider
from src.models import CryptoAsset, PricePoint

BASE_URL = "https://api.coingecko.com/api/v3"


def _optional_float(value: Any) -> Optional[float]:
    """Convert API numeric values safely, treating null/malformed data as missing."""
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


class CoinGeckoAdapter(CryptoDataProvider):
    """CoinGecko implementation of the Adapter pattern and provider port.

    It isolates HTTP concerns and translates raw vendor dictionaries into domain
    models, so the rest of the application remains independent of CoinGecko.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: int = 20) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["x-cg-demo-api-key"] = self.api_key
        return headers

    def get_market_assets(self) -> List[CryptoAsset]:
        """Fetch top market assets, returning an empty list on API failures."""
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
            "sparkline": "false",
        }
        try:
            response = requests.get(
                f"{BASE_URL}/coins/markets",
                headers=self._headers(),
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError, TypeError):
            return []
        if not isinstance(payload, list):
            return []
        assets = []
        for row in payload:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            assets.append(
                CryptoAsset(
                    asset_id=str(row["id"]),
                    name=str(row.get("name") or "Activo"),
                    symbol=str(row.get("symbol") or ""),
                    current_price=_optional_float(row.get("current_price")),
                    market_cap=_optional_float(row.get("market_cap")),
                    change_24h=_optional_float(
                        row.get("price_change_percentage_24h")
                    ),
                    image=row.get("image"),
                )
            )
        return assets

    def get_price_history(self, asset_id: str, days: int) -> List[PricePoint]:
        """Fetch and normalize historical prices; invalid/empty payloads are safe."""
        try:
            requested_days = int(days)
            if requested_days < 1 or not asset_id:
                return []
            response = requests.get(
                f"{BASE_URL}/coins/{asset_id}/market_chart",
                headers=self._headers(),
                params={
                    "vs_currency": "usd",
                    "days": requested_days,
                    "interval": "daily",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError, TypeError):
            return []
        if not isinstance(payload, dict) or not isinstance(payload.get("prices"), list):
            return []
        points = []
        for item in payload["prices"]:
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            try:
                timestamp = datetime.utcfromtimestamp(float(item[0]) / 1000)
                price = float(item[1])
            except (TypeError, ValueError, OverflowError, OSError):
                continue
            points.append(PricePoint(timestamp=timestamp, price=price))
        return points
