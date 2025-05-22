"""Adapter registry & auto-import (bitbank など自動登録)."""
import importlib, pkgutil, pathlib
registry = {}

_pkg = pathlib.Path(__file__).resolve().parent
for m in pkgutil.iter_modules([str(_pkg)]):
    if m.name == "__init__":           # self を除外
        continue
    mod = importlib.import_module(f"{__name__}.{m.name}")
    # クラス名が *Adapter で終わるものを 1 つ拾って登録
    for attr in dir(mod):
        if attr.endswith("Adapter"):
            registry[m.name] = getattr(mod, attr)
            break
