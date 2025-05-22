import pandas as pd
from domain.strategies.range.rsi_strategy import evaluate

def test_rsi_buy_when_oversold():
    # RSI を下げたダミーデータで "buy" を期待
    prices = list(range(100, 50, -1))
    df = pd.DataFrame({"ts": range(len(prices)), "close": prices})
    res = evaluate(df, period=14, oversold=30)
    assert res["action"] == "buy"
