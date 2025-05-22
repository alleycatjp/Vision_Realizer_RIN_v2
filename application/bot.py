"""シンプル Bot – 価格 CSV → 戦略判定 → decision_log 出力"""
from __future__ import annotations
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping
from infrastructure.config_loader import get_paths, get_pair_config
from infrastructure.file_logger import log_decision, log_warning
from application.strategy_executor import evaluate_strategy
from domain.market_state import detect_market_state

PATHS = get_paths()
PATHS = PATHS
import json, os
PAIR_STATUS = json.load(open(os.path.join("config", "pair_status.json")))
PRICE_DIR = Path(PATHS["price_data_dir"]).resolve()

def latest_csv(pair: str):
    """PRICE_DIR 配下から <pair>.csv の最新ファイルを返す（無ければ None）"""
    hits = sorted(PRICE_DIR.rglob(f"{pair}.csv"),
                  key=lambda p: p.stat().st_mtime,
                  reverse=True)
    return hits[0] if hits else None

def run_bot() -> None:
    for pair, st in PAIR_STATUS.items():
        if isinstance(st, int): st = {"manual_enabled": bool(st)}
        if not st.get("manual_enabled", True):
            continue
        csv = latest_csv(pair)
        if csv is None:
            log_warning(f"[{pair}] CSV not found")
            continue

        df = pd.read_csv(csv, names=["ts", "close"])
        df["close"]=pd.to_numeric(df["close"], errors="coerce"); df.dropna(inplace=True)
        if len(df) < 30:
            log_decision({"timestamp": datetime.utcnow().isoformat(),
                          "exchange": csv.parent.name,
                          "pair": pair,
                          "market": "insufficient",
                          "strategy": "skip",
                          "action": "none",
                          "score": 0})
            continue

        market = detect_market_state(df)
        if market == "undecided":
            market = "range"
        res = evaluate_strategy(pair, df, market, params={})
        entry: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "exchange":  csv.parent.name,
            "pair":      pair,
            "market":    market,
            **res,
        }
        log_decision(entry)
        print(f"[{entry['exchange']}_{pair}] {entry['strategy']} {entry['action']} {entry['score']}")

if __name__ == "__main__":
    run_bot()
