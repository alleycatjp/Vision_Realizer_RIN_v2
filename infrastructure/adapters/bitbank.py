from __future__ import annotations
import requests, json, pathlib
DEFAULT_EXCHANGE = "bitbank"
from .base import BaseAdapter

_CONF = {}
cfg_path = pathlib.Path("config/exchange_config.json")
if cfg_path.exists():
    _CONF = json.load(cfg_path.open())

BASE_URL  = _CONF.get(DEFAULT_EXCHANGE, {}).get("rest_url",  "https://public.bitbank.cc")
TICK_PATH = _CONF.get(DEFAULT_EXCHANGE, {}).get("ticker_path", "/tickers")

class BitbankAdapter(BaseAdapter):
    """Bitbank 現物ティッカーを返す"""
    def fetch_tickers(self):
        url = f"{BASE_URL}{TICK_PATH}"
        for it in requests.get(url, timeout=10).json()["data"]:
            yield {
                "pair"  : it["symbol"].lower(),
                "volume": float(it["volume"]),
                "last"  : float(it["last"]),
            }

# backward-compat
Bitbank = BitbankAdapter
