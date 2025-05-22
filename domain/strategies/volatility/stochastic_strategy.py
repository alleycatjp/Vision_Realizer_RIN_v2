"""Module documentation follows."""

"""Stochastic %K 14-3, %D 3 strategy"""
import pandas as pd

def stochastic(df, k_period=14, d_period=3):
    low_min = df['low'].rolling(k_period).min()
    high_max = df['high'].rolling(k_period).max()
    k = 100 * (df['close'] - low_min) / (high_max - low_min)
    d = k.rolling(d_period).mean()
    return k, d

def evaluate_stoch(df, k_period=14, d_period=3):
    if len(df) < k_period + d_period:
        return {"signal": "hold", "score": 0}
    k, d = stochastic(df, k_period, d_period)
    if k.iloc[-2] < d.iloc[-2] and k.iloc[-1] > d.iloc[-1]:
        return {"signal": "buy", "score": 1}
    if k.iloc[-2] > d.iloc[-2] and k.iloc[-1] < d.iloc[-1]:
        return {"signal": "sell", "score": -1}
    return {"signal": "hold", "score": 0}

