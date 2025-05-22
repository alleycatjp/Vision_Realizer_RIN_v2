"""
Kill-Switch V2 ― Bot を確実に停止させる安全装置
"""

import logging, subprocess, sys
from pathlib import Path
from typing import Union

UNIT_NAME = "rin-bot.service"  # systemd unit
TMP_KILL = Path("tmp/kill")    # 起動ブロック用フラグ
DD_THRESHOLD = -0.15           # −15 % ドローダウン

_log = logging.getLogger(__name__)

class KillSwitch:
    def __init__(self, reason: str) -> None:
        self.reason = reason

    def _log(self)        : _log.critical("KILL-SWITCH: %s", self.reason)
    def _flag(self)       : (TMP_KILL.parent.mkdir(exist_ok=True), TMP_KILL.touch(exist_ok=True))
    def _stop_systemd(self): subprocess.run(["systemctl", "stop", UNIT_NAME], check=False, capture_output=True)

    def activate(self) -> None:
        self._log(); self._flag(); self._stop_systemd(); sys.exit(1)

# ── 旧 API 互換 ──
def check(dd: float, color: str) -> None:
    if dd <= DD_THRESHOLD or color.lower() == "red":
        print("[KillSwitch] drawdown/RED detected – stopping bot")
        KillSwitch(f"dd={dd:.2%} / color={color}").activate()

def trigger(reason: Union[str, Exception]) -> None:
    KillSwitch(str(reason)).activate()
