"""Module documentation follows."""

from __future__ import annotations
import pandas as pd
from dataclasses import dataclass
from typing import Literal

@dataclass(slots=True, frozen=True)
class Decision:
    action: Literal["sell", "none"]
    confidence: float

def evaluate(df: pd.DataFrame, cfg: dict) -> Decision:
    """MACD デッドクロス + ATR 拡大で sell 決定"""
    ema_fast = df_close.ewm(span=12, adjust=False).mean()
    ema_slow = df_close.ewm(span=26, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=9, adjust=False).mean()

    dead_cross = macd.iloc[-2] > signal.iloc[-2] and macd.iloc[-1] < signal.iloc[-1]
    atr = (df["high"] - df["low"]).rolling(cfg["atr_window"]).mean()
    atr_spike = atr.iloc[-1] > atr.mean() * cfg["atr_multiplier"]

    if dead_cross and atr_spike:
        return Decision("sell", 0.9)
    return Decision("none", 0.2)

