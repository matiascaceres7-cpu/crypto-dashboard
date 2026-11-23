"""Market application service coordinating providers and analytical strategies."""

from typing import List, Optional, Sequence, Type

import pandas as pd

from src.adapters.crypto_data_provider import CryptoDataProvider
from src.models import CryptoAsset, PricePoint
from src.services.analysis_strategy import AnalysisStrategy


class CryptoMarketService:
    """Orchestrates market access and calculations without depending on Streamlit.

    The service follows SRP by owning market use cases, and DIP by receiving an
    abstract provider. Strategies are injected to make analysis replaceable.
    """

    def __init__(
        self,
        provider: CryptoDataProvider,
        strategies: Optional[Sequence[AnalysisStrategy]] = None,
    ) -> None:
        self.provider = provider
        self.strategies = list(strategies or [])

    def get_market_assets(self) -> List[CryptoAsset]:
        """Return the provider's normalized market assets."""
        return self.provider.get_market_assets()

    def get_price_history(self, asset_id: str, days: int) -> List[PricePoint]:
        """Return ordered historical price points for one asset."""
        return self.provider.get_price_history(asset_id, days)

    def market_dataframe(self) -> Optional[pd.DataFrame]:
        """Build the legacy dashboard table from domain assets."""
        assets = self.get_market_assets()
        if not assets:
            return None
        rows = [
            {
                "id": asset.asset_id,
                "name": asset.name,
                "symbol": asset.symbol,
                "current_price": asset.current_price,
                "market_cap": asset.market_cap,
                "price_change_percentage_24h": asset.change_24h,
                "image": asset.image,
            }
            for asset in assets
        ]
        return pd.DataFrame(rows)

    def history_dataframe(self, asset_id: str, days: int) -> Optional[pd.DataFrame]:
        """Build the dashboard's legacy Fecha/Precio history table."""
        points = self.get_price_history(asset_id, days)
        if not points:
            return None
        return pd.DataFrame(
            [{"Fecha": point.timestamp, "Precio": point.price} for point in points]
        )

    def analyze(self, prices: Sequence[float]) -> List[dict]:
        """Run each configured strategy and return named metric dictionaries."""
        return [strategy.analyze(prices) for strategy in self.strategies]

    @staticmethod
    def calculate_technical_indicators(history: pd.DataFrame) -> pd.DataFrame:
        """Return sorted history augmented with MA7, MA30, RSI, and period return."""
        if history is None or history.empty:
            return pd.DataFrame(columns=["Fecha", "Precio", "MA7", "MA30", "RSI"])
        result = history.copy().dropna(subset=["Fecha", "Precio"])
        result["Fecha"] = pd.to_datetime(result["Fecha"], errors="coerce")
        result["Precio"] = pd.to_numeric(result["Precio"], errors="coerce")
        result = result.dropna(subset=["Fecha", "Precio"]).sort_values("Fecha")
        result = result.reset_index(drop=True)
        result["MA7"] = result["Precio"].rolling(7, min_periods=1).mean()
        result["MA30"] = result["Precio"].rolling(30, min_periods=1).mean()
        delta = result["Precio"].diff()
        gains = delta.clip(lower=0).rolling(14, min_periods=14).mean()
        losses = (-delta.clip(upper=0)).rolling(14, min_periods=14).mean()
        result["RSI"] = 100 - 100 / (1 + gains / losses.replace(0, float("nan")))
        return result
