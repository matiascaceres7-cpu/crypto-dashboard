import os
from typing import Optional

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.coingecko.com/api/v3"


def _get_api_key() -> Optional[str]:
    """Return the CoinGecko key from Streamlit secrets or environment variables."""
    try:
        secret_key = st.secrets.get("COINGECKO_API_KEY")
    except Exception:
        # Streamlit secrets may be unavailable when running locally or in tests.
        secret_key = None
    return secret_key or os.getenv("COINGECKO_API_KEY")


def _get_headers() -> dict[str, str]:
    headers = {"accept": "application/json"}
    api_key = _get_api_key()
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    return headers


def obtener_top_criptos() -> Optional[pd.DataFrame]:
    """Fetch the top 250 cryptocurrencies and return the dashboard columns."""
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
            headers=_get_headers(),
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or not data:
            return None

        df = pd.DataFrame(data)
        columns = [
            "id",
            "name",
            "symbol",
            "current_price",
            "market_cap",
            "price_change_percentage_24h",
            "image",
        ]
        # Keep the dataframe schema stable even if the API omits optional fields.
        for column in columns:
            if column not in df.columns:
                df[column] = None
        df = df[columns]
        df["price_change_percentage_24h"] = pd.to_numeric(
            df["price_change_percentage_24h"], errors="coerce"
        )
        return df
    except (requests.RequestException, ValueError, TypeError) as exc:
        print(f"Error al consultar CoinGecko: {exc}")
        return None


def obtener_historico_activo(
    coin_id: str = "bitcoin", days: int = 30
) -> Optional[pd.DataFrame]:
    """Fetch historical USD prices and return a dataframe with Fecha and Precio."""
    try:
        days = int(days)
        if days < 1:
            raise ValueError("days debe ser un entero positivo")

        response = requests.get(
            f"{BASE_URL}/coins/{coin_id}/market_chart",
            headers=_get_headers(),
            params={"vs_currency": "usd", "days": days, "interval": "daily"},
            timeout=20,
        )
        response.raise_for_status()
        prices = response.json().get("prices", [])
        if not prices:
            return None

        df = pd.DataFrame(prices, columns=["timestamp", "Precio"])
        df["Fecha"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
        df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce")
        return df[["Fecha", "Precio"]].dropna().reset_index(drop=True)
    except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
        print(f"Error al consultar el histórico de CoinGecko: {exc}")
        return None
