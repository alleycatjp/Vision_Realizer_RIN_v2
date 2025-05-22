#!/usr/bin/env python3
"""
📄 tools/backtest.py – TP/SL + WIN / cooldown 対応版
-------------------------------------------------
• CSV 価格データを読み込み、strategy_executor でシグナル生成
• trade_executor.simulate で TP / SL 判定、NAV を更新
• WIN 幅と cooldown_tick を CLI から可変指定
"""
from __future__ import annotations

import argparse, csv, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, List, Dict, Optional

import pandas as pd

from application.strategy_executor import evaluate_strategy
from domain.market_state import detect_market_state
from infrastructure.config_loader import get_paths, get_pair_config
from trade_executor import simulate

# ───────────────────────────────────────────────
PATHS = get_paths()
PRICE_DIR = Path(PATHS["price_data_dir"]).resolve()
START_NAV  = 1_000_000
MIN_ROWS   = 30     # データ不足スキップ基準

# ───────────────────────────────────────────────
# 便利関数

def parse_iso(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_prices(pair: str, dt_from: datetime, dt_to: datetime) -> List[Dict[str, Any]]:
    csv_path = PRICE_DIR / "bitbank" / f"{pair}.csv"
    if not csv_path.exists():
        print(f"[WARN] {pair}: csv not found → skip")
        return []
    rows: List[Dict[str, Any]] = []
    with csv_path.open() as fp:
        rdr = csv.DictReader(fp)
        for r in rdr:
            ts = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).astimezone(timezone.utc)
            if dt_from <= ts <= dt_to:
                rows.append({"ts": ts, "price": float(r["price"])})
    return rows

# ───────────────────────────────────────────────
# バックテスト本体

def backtest(
    pair: str,
    rows: List[Mapping[str, Any]],
    *,
    tp: float,
    sl: float,
    win: int,
    cooldown: int,
) -> Optional[Dict[str, Any]]:
    if len(rows) < max(MIN_ROWS, win):
        print(f"[WARN] {pair}: rows<{max(MIN_ROWS, win)} → skip")
        return None

    nav = START_NAV
    wins = losses = trades = 0
    last_trade_idx = -cooldown - 1  # 初回エントリー許可

    for i in range(win, len(rows)):
        # クールダウン判定
        if i - last_trade_idx <= cooldown:
            continue

        window = rows[i - win : i + 1]
        closes = [x["price"] for x in window]
        df     = pd.DataFrame({"close": closes})

        market = detect_market_state(closes)
        signal = evaluate_strategy(pair, df, market, params={})["action"]
        price  = rows[i]["price"]

        if signal in ("buy", "sell"):
            price_path = [r["price"] for r in rows[i : i + win]]
            if len(price_path) < 2:
                break
            _, _, pnl = simulate(price, signal, price_path, tp_pct=tp, sl_pct=sl)
            nav *= 1 + pnl
            trades += 1
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            last_trade_idx = i

    return {
        "pair": pair,
        "trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(100 * wins / trades, 2) if trades else 0.0,
        "final_nav_jpy": round(nav),
        "start_price": rows[0]["price"],
        "end_price": rows[-1]["price"],
        "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
    }

# ───────────────────────────────────────────────
# CLI

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Backtester (TP/SL + WIN/cooldown)")
    ap.add_argument("--pairs", required=True, help="btc_jpy,eth_jpy …")
    ap.add_argument("--from", dest="dt_from", help="ISO start UTC")
    ap.add_argument("--to", dest="dt_to", help="ISO end UTC (default=now)")
    ap.add_argument("--days", type=int, help="past N days shortcut")
    ap.add_argument("--tp", type=float, default=0.4, help="TP %")
    ap.add_argument("--sl", type=float, default=0.2, help="SL %")
    ap.add_argument("--win", type=int, default=20, help="window size (tick)")
    ap.add_argument("--cooldown", type=int, default=0, help="cooldown tick")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    now  = datetime.now(timezone.utc)
    dt_to   = parse_iso(args.dt_to) if args.dt_to else now
    dt_from = dt_to - timedelta(days=args.days) if args.days else parse_iso(args.dt_from)

    results = []
    for p in (x.strip() for x in args.pairs.split(",") if x.strip()):
        rows = load_prices(p, dt_from, dt_to)
        summary = backtest(
            p,
            rows,
            tp=args.tp,
            sl=args.sl,
            win=args.win,
            cooldown=args.cooldown,
        )
        if summary:
            results.append(summary)

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
