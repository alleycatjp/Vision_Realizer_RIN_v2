"""Module documentation follows."""

"""Common utility functions."""
import pathlib
import datetime
import zoneinfo

def ensure_dir_exists(path: str) -> None:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def timestamp_jst() -> str:
    return datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds")

