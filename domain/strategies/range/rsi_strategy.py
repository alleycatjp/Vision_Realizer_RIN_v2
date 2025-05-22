#!/usr/bin/env python3
from __future__ import annotations
"""
📄 domain/strategies/range/rsi_strategy.py – 汎用入力対応（確定版）
"""

from typing import Any
import numpy as np
import pandas as pd

RSI_PERIOD      = 14
RSI_OVERSOLD    = 30.0
RSI_OVERBOUGHT  = 70.0


def _to_close_array(obj: Any) -> np.ndarray:
    if isinstance(obj, pd.DataFrame):
        return np.asarray(obj["close"], dtype=float)
    if isinstance(obj, pd.Series):
        return np.asarray(obj.values, dtype=float)
    return np.asarray(obj, dtype=float)              # ndarray / list


def _rsi(series: np.ndarray, period: int = RSI_PERIOD) -> float:
    delta = np.diff(series)
    gain  = np.where(delta > 0,  delta, 0.0)
    loss  = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.convolve(gain,  np.ones(period), 'valid') / period
    avg_loss = np.convolve(loss,  np.ones(period), 'valid') / period
    rs = np.where(avg_loss == 0, np.inf, avg_gain / avg_loss)
    return float(100.0 - 100.0 / (1.0 + rs[-1]))


def evaluate(
    data,                       # DataFrame / Series / ndarray / list
    period: int      = RSI_PERIOD,
    oversold: float  = RSI_OVERSOLD,
    overbought: float = RSI_OVERBOUGHT,
) -> dict:
    close = _to_close_array(data)
    if close.size < period + 1:
        return {"action": "none", "score": 0.0}

    rsi = _rsi(close[-(period + 1):], period)

    if rsi < oversold:
        action = "buy"
    elif rsi > overbought:
        action = "sell"
    else:
        action = "none"

    score = round(abs(rsi - 50.0) / 50.0, 3)
    return {"action": action, "score": score}


# 旧 API 互換
def evaluate_rsi(df, params: dict | None = None) -> dict:
    return evaluate(df, **(params or {}))
