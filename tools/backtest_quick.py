"""
tools/backtest_quick.py  ―― “負けないスキャル” ざっくり検証
・指定ペアの CSV を読み込み
・market_state → 戦術切替 → action 判定
・1 回の売買あたり +0.05%／-0.10% で簡易損益を算出
・結果サマリーを print だけ（グラフは出さない簡易版）
"""
from pathlib import Path
import pandas as pd
import argparse, sys, json
from datetime import datetime
from application.strategy_executor import evaluate_strategy
from domain.market_state     import detect_market_state
from infrastructure.config_loader import get_paths, get_pair_config

PATHS = get_paths()
paths = PATHS
price_root = Path(paths["price_data_dir"])

def backtest(pair: str):
    csv = price_root / "bitbank" / f"{pair}.csv"
    if not csv.exists():
        print(f"[WARN] price CSV not found: {csv}", file=sys.stderr)
        return
    df = pd.read_csv(csv, names=["ts","close"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df.dropna(inplace=True)

    cash, pos, wins, losses = 1_000_000, 0, 0, 0   # 円建て仮想資金
    for i in range(30, len(df)):
        window = df.iloc[i-30:i]            # 直近 30 本で market_state
        market = detect_market_state(window)
        res = evaluate_strategy(pair, window, market, params={})

        price = df.iloc[i]["close"]
        if res["action"] == "buy" and cash > 0:
            pos  = cash / price
            cash = 0
        elif res["action"] == "sell" and pos > 0:
            cash = pos * price
            pos  = 0
            # 超簡易： market==bear なら損、else 利確 とする
            if market == "bear":
                cash *= 0.999   # -0.1%
                losses += 1
            else:
                cash *= 1.0005  # +0.05%
                wins   += 1

    nav = cash + pos * df.iloc[-1]["close"]
    print(json.dumps({
        "pair": pair,
        "trades": wins+losses,
        "wins": wins,
        "losses": losses,
        "final_nav_jpy": round(nav),
        "start_price": float(df.iloc[0]["close"]),
        "end_price":   float(df.iloc[-1]["close"]),
        "timestamp":   datetime.utcnow().isoformat(timespec="seconds")
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--pair", default="btc_jpy", help="e.g. btc_jpy")
    args = p.parse_args()
    backtest(args.pair)
