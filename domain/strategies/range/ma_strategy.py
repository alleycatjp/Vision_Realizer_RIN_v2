"""Module documentation follows."""

"""Moving Average crossover strategy
   SMA 20 / SMA 50
"""
import pandas as pd

def evaluate_ma(df, fast=20, slow=50):
    if len(df) < slow: 
        return {"signal": "hold", "score": 0}
    sma_fast = df_close.rolling(fast).mean().iloc[-1]
    sma_slow = df_close.rolling(slow).mean().iloc[-1]
    if sma_fast > sma_slow:
        return {"signal": "buy", "score": 1}
    elif sma_fast < sma_slow:
        return {"signal": "sell", "score": -1}
    return {"signal": "hold", "score": 0}

