import subprocess, importlib, sys, pathlib, inspect

# 環境セット：プロジェクト root を import パスに追加
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import application.bot  # noqa: E402

def test_bot_import():
    # bot モジュールが読み込める
    assert inspect.ismodule(application.bot)

def test_bot_dry_run():
    # --dry-run 実装があれば 0 終了、無ければスキップ
    if "--dry-run" in open(application.bot.__file__).read():
        assert subprocess.call(
            [sys.executable, "-m", "application.bot", "--dry-run"]
        ) == 0

def test_fetch_registry():
    mod = importlib.import_module("infrastructure.data_fetcher")
    # adapters.registry が組み立てられているか
    assert hasattr(mod, "registry") and isinstance(mod.registry, dict)
