import pandas as pd
from domain.market_state import detect_market_state

def test_market_state_range():
    # ダミー価格が横ばい → "range" を期待
    df = pd.DataFrame({"ts": range(30), "close": [100]*30})
    assert detect_market_state(df) == "range"
