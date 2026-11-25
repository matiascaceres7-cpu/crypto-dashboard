"""Service-level unit and integration tests using an isolated mock provider."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd
import pytest  # <-- 1. Importamos pytest

from src.models import CryptoAsset, PricePoint
from src.services.analysis_strategy import TrendStrategy
from src.services.market_service import CryptoMarketService


def test_service_builds_legacy_market_and_history_dataframes():
    provider = MagicMock()
    provider.get_market_assets.return_value = [
        CryptoAsset("bitcoin", "Bitcoin", "btc", 10, 1000, 2.5)
    ]
    provider.get_price_history.return_value = [PricePoint(datetime(2024, 1, 1), 10)]
    service = CryptoMarketService(provider)
    market = service.market_dataframe()
    history = service.history_dataframe("bitcoin", 7)
    assert market.iloc[0]["id"] == "bitcoin"
    assert market.iloc[0]["price_change_percentage_24h"] == 2.5
    assert list(history.columns) == ["Fecha", "Precio"]


def test_empty_provider_results_preserve_legacy_none_contract():
    provider = MagicMock()
    provider.get_market_assets.return_value = []
    provider.get_price_history.return_value = []
    service = CryptoMarketService(provider)
    assert service.market_dataframe() is None
    assert service.history_dataframe("bitcoin", 7) is None


def test_service_invokes_configured_strategy_and_indicator_calculation():
    provider = MagicMock()
    service = CryptoMarketService(provider, strategies=[TrendStrategy()])
    assert service.analyze([100, 105])[0]["percentage_change"] == pytest.approx(5)
    history = pd.DataFrame(
        {"Fecha": [datetime(2024, 1, 1), datetime(2024, 1, 2)], "Precio": [10, 12]}
    )
    result = service.calculate_technical_indicators(history)
    assert list(result["MA7"]) == [10, 11]
    assert list(result["MA30"]) == [10, 11]
