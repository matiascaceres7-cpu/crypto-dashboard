"""Compatibility facade preserving the original app.py data API."""

import os
from typing import Optional

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.adapters.coingecko_adapter import CoinGeckoAdapter
from src.services.analysis_strategy import TrendStrategy, VolatilityStrategy
from src.services.market_service import CryptoMarketService

load_dotenv()


def _create_service() -> CryptoMarketService:
    """Create a request-scoped service using Streamlit secrets when available."""
    try:
        secret_key = st.secrets.get("COINGECKO_API_KEY")
    except Exception:
        secret_key = None
    api_key = secret_key or os.getenv("COINGECKO_API_KEY")
    provider = CoinGeckoAdapter(api_key=api_key)
    return CryptoMarketService(
        provider,
        strategies=[TrendStrategy(), VolatilityStrategy()],
    )


def obtener_top_criptos() -> Optional[pd.DataFrame]:
    """Return top cryptocurrencies using the existing dashboard data contract."""
    return _create_service().market_dataframe()


def obtener_historico_activo(
    coin_id: str = "bitcoin", days: int = 30
) -> Optional[pd.DataFrame]:
    """Return history with the existing Fecha and Precio column names."""
    return _create_service().history_dataframe(coin_id, days)
