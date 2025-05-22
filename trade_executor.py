# ========================================
# 📄 trade_executor.py - TP/SL 約定シミュレータ
# ----------------------------------------
# ■ 目的（ファイルの存在意義）:
#   バックテスト／ライブ運用の双方で共通利用できる、
#   "出口戦略" 判定ロジックをシングルソース化する。
#   ・TP (Take‑Profit)
#   ・SL (Stop‑Loss)
#   ・取引手数料（BitbankAdapter ─ maker −0.02 %）
#
# ■ 使用方法（サンプル）:
#   from trade_executor import simulate
#   exit_price, reason, pnl_pct = simulate(
#       entry_price=5000000,
#       direction="buy",
#       price_path=[...],
#       tp_pct=0.4,
#       sl_pct=0.2,
#   )
# ----------------------------------------
from typing import List, Tuple

# BitbankAdapter maker 手数料 −0.02 %
FEE_PCT: float = -0.0002  # 負の値で手数料控除／報酬


def simulate(
    entry_price: float,
    direction: str,
    price_path: List[float],
    tp_pct: float,
    sl_pct: float,
) -> Tuple[float, str, float]:
    """TP / SL を評価し、ポジションをクローズするまでシミュレート。

    Args:
        entry_price: 約定価格（JPY など）
        direction: "buy" (ロング) または "sell" (ショート)
        price_path: ティックごとの価格列
        tp_pct: 利確幅 [%] 例 0.4 (= +0.4 %)
        sl_pct: 損切幅 [%] 例 0.2 (= −0.2 %)

    Returns:
        exit_price: 決済価格
        reason: "tp" | "sl" | "timeout" など
        pnl_pct: 手数料込み損益率 (正で利益 / 負で損失)
    """
    if direction not in {"buy", "sell"}:
        raise ValueError("direction must be 'buy' or 'sell'")

    # TP/SL 水準を事前計算
    if direction == "buy":
        tp_price = entry_price * (1 + tp_pct / 100)
        sl_price = entry_price * (1 - sl_pct / 100)
    else:  # sell (short)
        tp_price = entry_price * (1 - tp_pct / 100)
        sl_price = entry_price * (1 + sl_pct / 100)

    exit_price: float = price_path[-1]  # デフォルト: 最終ティックで決済
    reason: str = "timeout"

    for price in price_path:
        if direction == "buy":
            if price >= tp_price:
                exit_price, reason = price, "tp"
                break
            if price <= sl_price:
                exit_price, reason = price, "sl"
                break
        else:  # short
            if price <= tp_price:
                exit_price, reason = price, "tp"
                break
            if price >= sl_price:
                exit_price, reason = price, "sl"
                break

    # PnL 計算（long:+, short:-）
    pnl_pct = ((exit_price - entry_price) / entry_price) * (1 if direction == "buy" else -1)
    pnl_pct += FEE_PCT  # 手数料適用

    return exit_price, reason, pnl_pct
