"""Module documentation follows."""

"""Centralized path & filename constants."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
USER_DATA_DIR = ROOT / "user_data"
PRICE_DATA_DIR = USER_DATA_DIR / "price_data"

MARKET_CONFIG = CONFIG_DIR / "market_config.json"
PARAMS_CONFIG = CONFIG_DIR / "params.json"

