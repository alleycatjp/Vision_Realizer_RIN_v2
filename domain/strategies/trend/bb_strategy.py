"""Module documentation follows."""

import pandas as pd

def evaluate_bb(pair, price_data):
    """
    ボリンジャーバンドによるトレンド判定。
    closeの終値をもとに、±1σ帯域を計算し、現在価格が帯域を抜けたかを判断。
    """

    if price_data is None or "close" not in price_data or len(price_data) < 21:
        return {
            "strategy": "bb",
            "action": "hold",
            "score": 0.0,
            "band_width": None,
            "price_position": None
        }

    close = price_data_close
    ma = close.rolling(window=20).mean()
    std = close.rolling(window=20).std()

    upper_band = ma + std
    lower_band = ma - std

    current_price = close.iloc[-1]
    upper = upper_band.iloc[-1]
    lower = lower_band.iloc[-1]

    # バンド幅
    band_width = upper - lower

    # 正規化された位置（-1 = 下限, +1 = 上限）
    price_position = ((current_price - lower) / (upper - lower)) * 2 - 1
    price_position = round(price_position, 3)

    # 判定ロジック
    if current_price > upper:
        action = "buy"
    elif current_price < lower:
        action = "sell"
    else:
        action = "hold"

    score = round(abs(price_position), 3)

    return {
        "strategy": "bb",
        "action": action,
        "score": score,
        "band_width": round(band_width, 5),
        "price_position": price_position
    }

