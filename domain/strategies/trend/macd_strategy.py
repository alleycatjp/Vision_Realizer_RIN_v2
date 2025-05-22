"""Module documentation follows."""

from __future__ import annotations  # ← ★ ここが最初の実行文

import pandas as pd

# ─────────────────────────────────────
# 詳細版 : dict を返す
# ─────────────────────────────────────
def evaluate_macd(pair: str, price_data: pd.DataFrame) -> dict:
    """MACD 戦略によるエントリー判定処理。"""
    # 入力検証
    if (
        price_data is None
        or ("close" not in price_data.columns and "price" not in price_data.columns)
        or len(price_data) < 35
    ):
        return {"strategy": "macd", "action": "hold", "score": 0.0, "macd": None, "signal": None}

    series = price_data_close if "close" in price_data.columns else price_data["price"]

    # MACD 計算
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    if len(macd_line) < 2:
        return {"strategy": "macd", "action": "hold", "score": 0.0, "macd": None, "signal": None}

    prev_macd, curr_macd = macd_line.iloc[-2], macd_line.iloc[-1]
    prev_sig,  curr_sig  = signal_line.iloc[-2], signal_line.iloc[-1]
    diff  = curr_macd - curr_sig
    score = round(abs(diff), 5)

    # クロス判定
    if prev_macd < prev_sig and curr_macd > curr_sig:
        action = "buy"
    elif prev_macd > prev_sig and curr_macd < curr_sig:
        action = "sell"
    else:
        action = "hold"
        score  = 0.0

    return {
        "strategy": "macd",
        "action":   action,
        "score":    score,
        "macd":     round(curr_macd, 5),
        "signal":   round(curr_sig, 5),
    }

# ─────────────────────────────────────
# strategy_executor 用ラッパー
# ─────────────────────────────────────
def evaluate(df: pd.DataFrame, params: dict) -> tuple[str, float]:
    """(action, score) を返す簡易 I/F"""
    result = evaluate_macd("dummy", df)
    return result["action"], result["score"]

# バージョン履歴
# 2025-05-16 初版作成
# 2025-05-16 from __future__ import を最上部へ移動
