#!/usr/bin/env python3
from __future__ import annotations
"""
fallback_breakout – ブレイクアウト系フォールバック戦術
"""

import numpy as np
from typing import Dict, Any

WIN = 5        # ブレイク判定窓（tick）

def run(pair: str, df, params: Dict[str, Any] | None = None) -> dict:
    closes = df_close.values if hasattr(df, "close") else np.asarray(df, dtype=float)
    if closes.size < WIN:
        return {"strategy": "fallback_breakout", "action": "none", "score": 0}

    highest = closes[-WIN:].max()
    lowest  = closes[-WIN:].min()
    last    = closes[-1]

    if last >= highest:                    # 高値タッチで buy
        return {"strategy": "fallback_breakout", "action": "buy",  "score": 1}
    if last <= lowest:                     # 安値タッチで sell
        return {"strategy": "fallback_breakout", "action": "sell", "score": 1}

    return {"strategy": "fallback_breakout", "action": "none", "score": 0}
