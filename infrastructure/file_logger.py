# infrastructure/file_logger.py
import json
from datetime import datetime           # ← 追加
from pathlib import Path
from typing import Any, Mapping

from infrastructure.config_loader import get_paths, get_pair_config
from infrastructure.notifier import send   # ← 追加

# --------------------------------------------------
_PATHS = get_paths()


def log_decision(row: Mapping[str, Any]) -> None:
    """戦略判定結果を 1 行 JSON で追記し、Slack にも中継。"""
    log = (
        Path(_PATHS["decision_log_dir"])
        / row["exchange"]
        / f'{row["pair"]}.json'
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(row, ensure_ascii=False) + "\n")
    send("decision", row)

    # Slack に転送（失敗しても例外を握りつぶす設計）
    send("decision", row)


def log_warning(msg: str) -> None:
    """例外やリスク通知をテキストで保存し、Slack にも通知。"""
    warn = Path(_PATHS["log_dir"]) / "error.log"
    warn.parent.mkdir(parents=True, exist_ok=True)
    warn.parent.mkdir(parents=True, exist_ok=True)
    with warn.open("a", encoding="utf-8") as fp:
        fp.write(f"{datetime.utcnow().isoformat()} {msg}\n")

    send("warn", {"msg": msg})

# ─────────────────────────────────────────────
# JSON util  ― Streamlit UI から呼び出し
from pathlib import Path, Path

def load_json(path: Path, default=None):
    try:
        with open(path) as f:
            import json; return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}

def save_json(path: Path, data) -> None:
    import json, pathlib
    pathlib.Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))
