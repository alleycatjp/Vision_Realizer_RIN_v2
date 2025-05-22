"""
Risk Controller V2
────────────────────────────────────────
flag off : 旧ロジック (nav * 1%)
flag on  : NAV×ATR 連動で
           ・サイズ   = nav * 1% / atr
           ・ストップ = entry - atr×1.5
"""

from infrastructure.config_loader import feature_enabled

# ─── パブリック API ────────────────────────── #

def calc_size(nav: float, atr: float, *, multiplier: float = 1.0) -> float:
    """
    nav   : Net Asset Value (口座残高)
    atr   : Average True Range
    return: position size
    """
    if feature_enabled("risk_controller_v2"):
        risk_per_trade = 0.01 * nav           # 1% リスク
        pos = (risk_per_trade / max(atr, 1e-9)) * multiplier
        return max(0.0, min(pos, nav))        # NAV を超えない
    # ─ flag off → 旧ロジック (固定 1%)
    return nav * 0.01 * multiplier


def calc_stop(entry_price: float, atr: float, *, atr_multiple: float = 1.5) -> float:
    """
    entry_price: エントリー価格
    atr        : Average True Range
    return     : stop price
    """
    if feature_enabled("risk_controller_v2"):
        return entry_price - atr * atr_multiple
    return entry_price - atr

# ─── 旧 API 名互換（もし呼び出しが残っていれば） ─────────── #

def calc_size_v1(nav: float, atr: float) -> float:   # legacy alias
    return nav * 0.01
