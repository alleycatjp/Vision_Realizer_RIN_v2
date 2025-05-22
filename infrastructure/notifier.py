# ────────────────────────────────────────────────────────────
# infrastructure/notifier.py
# Rin から Slack などに通知を飛ばす最小モジュール
# ────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import requests
from datetime import datetime
from typing import Any, Mapping

# ──────────────────────────────
# 環境変数から Webhook URL を取得
# （systemd service の Environment= で渡す）
# ──────────────────────────────
_WEBHOOK = os.getenv("RIN_WEBHOOK_URL")


def _render_text(event: str, payload: Mapping[str, Any]) -> str:
    """Slack に表示させる 1 行テキストを生成"""
    if event == "decision":
        # {"pair": "btc_jpy", "action": "buy", "score": 0.87, ...}
        return (
            f":chart_with_upwards_trend: *{payload.get('pair','?')}* → "
            f"*{payload.get('action','?')}*  score `{payload.get('score','?')}`"
        )
    if event in {"warn", "error"}:
        return f":warning: {payload.get('msg', '')}"
    # それ以外（debug など）
    return f":speech_balloon: [{event}] {payload}"


def send(event: str, payload: Mapping[str, Any] | None = None) -> None:
    """
    任意イベントを Webhook へ POST。
    - URL が未設定なら即 return（本番・開発で安全に共用）
    - POST 失敗でも例外を外に投げず、Bot を止めない
    """
    if not _WEBHOOK:
        return

    payload = payload or {}

    body = {
        # これを入れないと Slack は黙殺する
        "text": _render_text(event, payload),
        # 追加メタ（後で取り出したいとき用）
        "event": event,
        "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        "payload": payload,
    }

    try:
        requests.post(_WEBHOOK, json=body, timeout=5)
    except Exception as e:  # noqa: BLE001
        # 失敗しても致命エラーにはしない
        print(f"[notifier] WARN: {e}")
