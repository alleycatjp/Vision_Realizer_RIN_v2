#!/usr/bin/env python3
"""
📄 tools/grid_search.py – WIN / cooldown 対応版
"""
from __future__ import annotations

import argparse, itertools, json, csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List

import yaml

from tools.backtest import backtest, load_prices, parse_iso  # backtest は WIN/cooldown 対応済
from infrastructure.config_loader import get_paths, get_pair_config

PATHS = get_paths()
PRICE_DIR   = Path(PATHS["price_data_dir"]).resolve()
PARAMS_YML  = Path("config/params.yaml")
RESULTS_DIR = Path("logs")

# ───────────────────────────────────────────────

def load_param_space(pair: str) -> Dict[str, List[Any]]:
    if not PARAMS_YML.exists():
        return {
            "WIN": [20, 40],
            "cooldown_tick": [0, 3],
            "tp_pct": [0.4, 0.6],
            "sl_pct": [0.15, 0.2],
        }
    with PARAMS_YML.open() as fp:
        data = yaml.safe_load(fp)
    return data.get(pair.upper(), data.get(pair, {}))


def param_product(space: Dict[str, List[Any]]):
    keys, vals = zip(*space.items())
    for combo in itertools.product(*vals):
        yield dict(zip(keys, combo))

# ───────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Grid search (WIN/cooldown 対応)")
    ap.add_argument("--pair", required=True)
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--criteria", default="win_rate>=25 and final_nav_jpy>0")
    return ap.parse_args()

# ───────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    now = datetime.now(timezone.utc)
    dt_to   = now
    dt_from = dt_to - timedelta(days=args.days)

    space = load_param_space(args.pair)
    rows  = load_prices(args.pair, dt_from, dt_to)

    results: List[Dict[str, Any]] = []
    for params in param_product(space):
        res = backtest(
            args.pair,
            rows,
            tp=params.get("tp_pct", 0.4),
            sl=params.get("sl_pct", 0.2),
            win=params.get("WIN", 20),
            cooldown=params.get("cooldown_tick", 0),
        )
        if not res:
            continue
        res.update(params)
        if eval(args.criteria, {}, res):
            results.append(res)

    results.sort(key=lambda x: x["final_nav_jpy"], reverse=True)

    RESULTS_DIR.mkdir(exist_ok=True)
    csv_path = RESULTS_DIR / f"grid_search_{now.strftime('%Y%m%d_%H%M%S')}.csv"
    with csv_path.open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=results[0].keys() if results else [])
        writer.writeheader()
        writer.writerows(results)

    print(json.dumps(results[: args.top], indent=2, ensure_ascii=False))
    print(f"[INFO] Saved {len(results)} rows → {csv_path}")


if __name__ == "__main__":
    main()
