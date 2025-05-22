#!/usr/bin/env python3
"""
📄 domain/strategies/range_rsi.py – 汎用入力対応（final）
--------------------------------------------------------
• data 引数を DataFrame / Series / ndarray / list すべて受け付け
• 入力を numpy.ndarray[float] の close 配列に統一して RSI 判定
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

# --- パラメータ（必要なら paths.json / params.json へ外出し可） ----
RSI_PERIOD = 7
RSI_UPPER  = 60
RSI_LOWER  = 40
# --------------------------------------------------------------------


def _rsi(series: np.ndarray, period: int) -> float:
    """シンプル RSI 計算（末尾の値だけ返す）"""
    delta = np.diff(series)
    gain  = np.where(delta > 0,  delta, 0.0)
    loss  = np.where(delta < 0, -delta, 0.0)
    avg_gain = np.convolve(gain,  np.ones(period), 'valid') / period
    avg_loss = np.convolve(loss,  np.ones(period), 'valid') / period
    rs = np.where(avg_loss == 0, np.inf, avg_gain / avg_loss)
    return float(100.0 - 100.0 / (1.0 + rs[-1]))   # 最新 RSI


def _to_close_array(obj: Any) -> np.ndarray:
    """入力を numpy.ndarray[float] の close 配列へ統一"""
    if isinstance(obj, pd.DataFrame):
        return np.asarray(obj["close"], dtype=float)
    if isinstance(obj, pd.Series):
        return np.asarray(obj.values, dtype=float)
    return np.asarray(obj, dtype=float)  # ndarray / list


def run(data, params=None) -> dict:
    """
    Parameters
    ----------
    data : DataFrame / Series / ndarray / list
        時系列データ（終値）。長さが RSI_PERIOD+1 未満なら判定しない。
    params : dict | None
        予備（未使用）
    """
    close = _to_close_array(data)
    if close.size < RSI_PERIOD + 1:
        return {"action": "none", "score": 0.0}

    rsi = _rsi(close[-(RSI_PERIOD + 1):], RSI_PERIOD)

    if rsi > RSI_UPPER:
        return {"action": "sell", "score": (rsi - RSI_UPPER) / (100 - RSI_UPPER)}
    if rsi < RSI_LOWER:
        return {"action": "buy",  "score": (RSI_LOWER - rsi) / RSI_LOWER}
    return {"action": "none", "score": 0.0}
