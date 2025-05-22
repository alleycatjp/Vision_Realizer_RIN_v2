import pytest
from application.killswitch import KillSwitch

def test_kill_switch_exit(monkeypatch):
    # sys.exit をフックして終了コードを捕捉
    captured = {}
    monkeypatch.setattr("sys.exit", lambda code: captured.setdefault("code", code))
    KillSwitch("unit-test").activate()
    assert captured["code"] == 1
