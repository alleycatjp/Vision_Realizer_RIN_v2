"""Module documentation follows."""

"""ATR breakout strategy"""
import pandas as pd

def atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def evaluate_atr(df, period=14, k=1.5):
    if len(df) < period + 2: 
        return {"signal": "hold", "score": 0}
    a = atr(df, period).iloc[-2]
    prev_close = df['close'].iloc[-2]
    cur_close = df['close'].iloc[-1]
    if cur_close > prev_close + k * a:
        return {"signal": "buy", "score": 1}
    if cur_close < prev_close - k * a:
        return {"signal": "sell", "score": -1}
    return {"signal": "hold", "score": 0}

