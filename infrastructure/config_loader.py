from pathlib import Path
from typing import Dict, Any, List
import json

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "config" / "paths.json").open() as f:
    _P = json.load(f)

# ── 公開API ───────────────────────────
def get_paths() -> dict:
    """paths.json フル辞書を返す（新正式API）"""
    return _P.copy()

def get_pair_config(*args: List[str]) -> Dict[str, Any]:
    """
    get_pair_config(asset, exchange, pair)
    例: get_pair_config("cp", "bitbank", "BTC_JPY")
    """
    if len(args) != 3:
        raise TypeError("get_pair_config(asset, exchange, pair)")
    asset, exchange, pair = args
    cfg = ROOT / "config" / "pairs" / asset / exchange / f"{pair.upper()}.json"
    with cfg.open() as f:
        return json.load(f)

# ---------- legacy alias ----------
def load_paths() -> dict:
    """旧コード互換エイリアス（→ get_paths）"""
    return get_paths()

# ──────────────────────────────────────────────────────────────
# Feature-flag helper
#   config/feature_flags.json で "flag_name": true なら機能 ON
# ──────────────────────────────────────────────────────────────
from pathlib import Path
import json as _json

_FEATURE_FLAGS_PATH = Path(__file__).parent.parent / "config" / "feature_flags.json"

def feature_enabled(flag_name: str, default: bool = False) -> bool:
    try:
        with open(_FEATURE_FLAGS_PATH, "r", encoding="utf-8") as fp:
            flags = _json.load(fp)
        return bool(flags.get(flag_name, default))
    except FileNotFoundError:
        return default
