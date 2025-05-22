import json, socket, pathlib, time
from datetime import datetime, timedelta
from infrastructure.config_loader import feature_enabled

SOCK = "/tmp/rin_volume.sock"
PAIR_STATUS = pathlib.Path("config/pair_status.json")
MIN_VOL = 5_000_000   # JPY 相当 24h 出来高

def _load_volume_data() -> dict[str, float]:
    # NOTE: 実装簡略化 ─ user_data/price_data の CSV 数行目から出来高を読むならここ
    return {}  # { "BTC_JPY": 12345678, ... }

def _update_status(low_liq: set[str]) -> None:
    status = json.loads(PAIR_STATUS.read_text())
    for k in status:
        status[k]["enabled"] = k not in low_liq
    PAIR_STATUS.write_text(json.dumps(status, indent=2))

def run_daemon() -> None:
    """systemd-unit で回す想定"""
    if not feature_enabled("volume_checker_ipc"):  # flag off → 寝るだけ
        while True: time.sleep(3600)

    # ソケット初期化
    try: pathlib.Path(SOCK).unlink()
    except FileNotFoundError: pass
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    srv.bind(SOCK)

    while True:
        vol = _load_volume_data()
        low = {p for p, v in vol.items() if v < MIN_VOL}
        _update_status(low)
        # Bot へシグナル送信
        srv.sendto(b"REFRESH", SOCK)
        time.sleep(60*30)  # 30min
