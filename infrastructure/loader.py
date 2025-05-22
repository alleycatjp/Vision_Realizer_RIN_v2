from infrastructure import DEFAULT_EXCHANGE
import os
DEFAULT_EXCHANGE = os.getenv("RIN_EXCHANGE", DEFAULT_EXCHANGE)

import os
# !/usr/bin/env python3
"""Module documentation follows."""

import csv
import pathlib
from datetime import datetime
from typing import Iterable, Dict, Any

from infrastructure.config_loader import load_paths

# ────────────────────────────────
# ディレクトリ設定
# ────────────────────────────────
_paths = load_paths()                      # config/paths.json を読む
_DATA_ROOT = pathlib.Path(_paths["price_data_dir"])  # ex) user_data/price_data

def _ensure_dir(p: pathlib.Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

# ────────────────────────────────
# パブリック I/F
# ────────────────────────────────
def save(ticks: Iterable[Dict[str, Any]]) -> None:
    """
    ticks: {
        "exchange": os.getenv("EXCHANGE", DEFAULT_EXCHANGE),
        "pair":     "btc_jpy",
        "timestamp": 1747399999000,   # ms
        "close":   15134000.0
    }
    """
    for t in ticks:
        exch = t["exchange"]
        pair = t["pair"]

        csv_path = _DATA_ROOT / exch / f"{pair}.csv"
        _ensure_dir(csv_path)

        is_new = not csv_path.exists()
        with csv_path.open("a", newline="") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(["timestamp", "price"])

            ts_iso = (
                datetime.utcfromtimestamp(t["timestamp"] / 1000)
                .isoformat(timespec="seconds") + "Z"
            )
            w.writerow([ts_iso, t["close"]])
