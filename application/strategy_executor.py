#!/usr/bin/env python3
"""
📄 application/strategy_executor.py – unified new/old API（final）
-----------------------------------------------------------------
• market_state に対応する戦術を順に呼び出し、最初に “action≠none” を返したものを採用
• 戦術シグネチャ差異（新 API: df, params ／ 旧 API: pair, df, params）を吸収
• 入力が DataFrame／Series／ndarray／list いずれでも “close” 列を保証して渡す
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# ───────────────────────────────────────────────
# 戦術インポート（必要に応じて追加）
from domain.strategies.range_rsi import run as rsi
from domain.strategies.trend.macd_strategy import evaluate as macd
from domain.strategies.fallback_breakout import run as fallback_breakout

STRATEGY_TABLE: dict[str, dict[str, Any]] = {
    "range":      {"rsi": rsi},
    "trend":      {"macd": macd},
    "volatility": {"macd": macd},
    "bear":       {"macd": macd},
    "undecided":  {"breakout": fallback_breakout},
}

_DEF_RESULT = {"action": "none", "score": 0.0}


# ───────────────────────────────────────────────
def _normalize(res: Any) -> dict:
    """tuple → dict 換装 & 欠損補完"""
    if isinstance(res, tuple):
        act = res[0] if len(res) > 0 else "none"
        score = float(res[1]) if len(res) > 1 else 0.0
        return {"action": act, "score": score}
    return res if isinstance(res, dict) else _DEF_RESULT.copy()


def _to_dataframe(obj) -> pd.DataFrame:
    """Series / ndarray / list → DataFrame(close=…) へ統一"""
    if isinstance(obj, pd.DataFrame):
        df = obj.copy()
    elif isinstance(obj, pd.Series):
        df = pd.DataFrame({"close": obj.values}, index=obj.index)
    else:  # ndarray / list-like
        df = pd.DataFrame({"close": np.asarray(obj, dtype=float)})

    # 列名調整
    if "close" not in df.columns:
        if "last" in df.columns:
            df["close"] = df["last"]
        elif len(df.columns) == 1:
            df.columns = ["close"]

    return df


# ───────────────────────────────────────────────
def evaluate_strategy(
    pair: str,
    raw,                              # DataFrame / Series / ndarray / list
    market: str,
    params: dict[str, Any] | None = None,
) -> dict:
    params = params or {}

    # ----------- normalize input → df with “close” ----------------
    df = _to_dataframe(raw)
    # ---------------------------------------------------------------

    for name, fn in STRATEGY_TABLE.get(market, {}).items():
        try:
            res = fn(df, params.get(name, {}))          # 新 API
        except TypeError:
            res = fn(pair, df, params.get(name, {}))    # 旧 API

        res = _normalize(res)
        if res["action"] != "none":
            return {"strategy": name, **res}

    return {"strategy": "none", **_DEF_RESULT.copy()}
