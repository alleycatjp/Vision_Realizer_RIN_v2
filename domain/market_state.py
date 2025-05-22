#!/usr/bin/env python3
from __future__ import annotations
import pandas as pd
# Market state detector  (窓 20 tick / 閾値緩和版)

from typing import List

WINDOW_TICKS = 25       # 20 tick ≒ 20 秒 or 200 秒など
SLOPE_TH     = 0.0003   # 0.03 %
VOLA_TH      = 0.04     # 4 %
BEAR_TH      = -0.05    # −5 %

def detect_market_state(prices):
    """Return range / trend / volatility / bear based on close prices only."""
    series = (prices["close"] if isinstance(prices, pd.DataFrame) else prices).astype(float)
    delta  = series.iloc[-1] - series.iloc[-WINDOW_TICKS]
    slope  = float(delta) / series.iloc[-WINDOW_TICKS]
    if abs(slope) <= 0.001:
        return "range"

    if slope <= BEAR_TH:
        return "bear"
    if abs(slope) >= SLOPE_TH:
        return "trend"

    vola = (max(series[-WINDOW_TICKS:]) - min(series[-WINDOW_TICKS:])) / series.iloc[-WINDOW_TICKS]
    if vola >= VOLA_TH:
        return "volatility"

    return "undecided"
