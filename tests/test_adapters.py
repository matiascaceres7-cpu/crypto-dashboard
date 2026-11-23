"""Adapter behavior tests, with all HTTP requests mocked for offline execution."""

from unittest.mock import MagicMock, patch

import requests

from src.adapters.coingecko_adapter import CoinGeckoAdapter


def test_market_payload_is_converted_to_domain_asset():
    response = MagicMock()
    response.json.return_value = [
        {
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "btc",
            "current_price": 65000,
            "market_cap": 1_000_000,
            "price_change_percentage_24h": 1.5,
            "image": "https://example.test/btc.png",
        }
    ]
    with patch("src.adapters.coingecko_adapter.requests.get", return_value=response):
        assets = CoinGeckoAdapter(api_key="secret").get_market_assets()
    assert len(assets) == 1
    assert assets[0].asset_id == "bitcoin"
    assert assets[0].current_price == 65000.0


def test_null_and_invalid_market_values_are_safe():
    response = MagicMock()
    response.json.return_value = [{"id": "coin", "current_price": None}]
    with patch("src.adapters.coingecko_adapter.requests.get", return_value=response):
        assets = CoinGeckoAdapter().get_market_assets()
    assert assets[0].current_price is None
    assert assets[0].change_24h is None


def test_empty_or_malformed_market_response_returns_empty_list():
    response = MagicMock()
    response.json.return_value = {"unexpected": "shape"}
    with patch("src.adapters.coingecko_adapter.requests.get", return_value=response):
        assert CoinGeckoAdapter().get_market_assets() == []


def test_connection_error_returns_empty_list():
    with patch(
        "src.adapters.coingecko_adapter.requests.get",
        side_effect=requests.ConnectionError("offline"),
    ):
        assert CoinGeckoAdapter().get_market_assets() == []


def test_history_payload_converts_timestamp_and_skips_null_rows():
    response = MagicMock()
    response.json.return_value = {"prices": [[1_700_000_000_000, 10], [None, None]]}
    with patch("src.adapters.coingecko_adapter.requests.get", return_value=response):
        points = CoinGeckoAdapter().get_price_history("sample", 7)
    assert len(points) == 1
    assert points[0].price == 10.0


def test_invalid_history_days_and_empty_history_are_safe():
    adapter = CoinGeckoAdapter()
    assert adapter.get_price_history("bitcoin", 0) == []
    response = MagicMock()
    response.json.return_value = {"prices": []}
    with patch("src.adapters.coingecko_adapter.requests.get", return_value=response):
        assert adapter.get_price_history("bitcoin", 7) == []
