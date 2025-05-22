#!/usr/bin/env python
# ===============================================
# 📄 dual_loop_bot.py – Bitbank Multi-Pair Bot (v2)
# ------------------------------------------------
# • WebSocket ⟶  sub-second price feed   (feed_loop)
# • 10-sec tact ⟶ strategy evaluation    (strategy_loop)
# • pair_status.json の enabled=true をすべて並列運用
# • 実売買ロジックは trade_executor / order_executor に委譲
# ===============================================

import asyncio, json, time, os
from collections import deque
from typing import Deque, Dict

import aiohttp                # pip install aiohttp
from trade_executor import simulate
from application.strategy_executor import evaluate_strategy
from domain.market_state import detect_market_state

# ───────────────────────────────────────────────
# 設定
WIN            = 20          # 戦術評価ウィンドウ (≈40 s)
COOLDOWN_TICK  = 3           # 同一方向エントリー間隔 (≈30 s)
TP_PCT         = 0.6
SL_PCT         = 0.15
PRICE_BUF_MAX  = 100

# 有効ペア一覧をロード
with open("config/pair_status.json") as f:
    _PAIRS_MAP: Dict[str, Dict[str, Dict]] = json.load(f)   # {exchange:{pair:{enabled}}}

# ───────────────────────────────────────────────
async def run_pair(exchange: str, pair: str) -> None:
    """1ペア専用の Feed ＋ Strategy イベントループ"""
    price_buf: Deque[float] = deque(maxlen=PRICE_BUF_MAX)
    last_trade_idx: int = -COOLDOWN_TICK - 1
    tick_idx: int = 0

    # ----- Feed Loop ---------------------------------------------------------
    async def feed_loop() -> None:
        url = "wss://stream.bitbank.cc/socket.io/?EIO=4&transport=websocket"
        retry = 0
        while True:
            try:
                async with aiohttp.ClientSession() as sess:
                    async with sess.ws_connect(url, heartbeat=25) as ws:
                        await ws.send_str("40/ticker")          # join room
                        print(f"[{pair}] WS connected")
                        retry = 0
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT and msg.data.startswith("42"):
                                payload = json.loads(msg.data[2:])[1]
                                price_buf.append(float(payload["last"]))
            except Exception as e:
                retry += 1
                sleep = min(30, 2 ** retry)
                print(f"[{pair}] WS error {e} – retry in {sleep}s")
                await asyncio.sleep(sleep)

    # ----- Strategy Loop -----------------------------------------------------
    async def strategy_loop() -> None:
        nonlocal last_trade_idx, tick_idx
        while True:
            await asyncio.sleep(10)               # 10-sec tact
            tick_idx += 1
            if len(price_buf) < WIN:
                continue
            if tick_idx - last_trade_idx <= COOLDOWN_TICK:
                continue

            snapshot = list(price_buf)[-WIN:]
            market   = detect_market_state(snapshot)
            signal   = evaluate_strategy(pair, snapshot, market, params={}).get("action")

            if signal in ("buy", "sell"):
                entry_price = snapshot[-1]
                _, _, pnl = simulate(
                    entry_price=entry_price,
                    direction=signal,
                    price_path=snapshot,
                    tp_pct=TP_PCT,
                    sl_pct=SL_PCT,
                )
                print(f"[{pair}] {signal} pnl={pnl:+.3%} at {entry_price}")
                last_trade_idx = tick_idx
                # TODO: order_executor.post_only(signal, entry_price)
        filled = order_executor.place_order(order, post_only=True)

    await asyncio.gather(feed_loop(), strategy_loop())

# ───────────────────────────────────────────────
async def main() -> None:
    tasks = [
        run_pair(ex, p)
        for ex, pairs in _PAIRS_MAP.items()
        for p, cfg in pairs.items()
        if cfg.get("enabled", True)
    ]
    if not tasks:
        raise RuntimeError("No enabled pairs found in pair_status.json")
    await asyncio.gather(*tasks)          # 永久タスクのため戻らない

# ───────────────────────────────────────────────
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[bot] terminated by user")
