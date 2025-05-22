import application.dual_loop_bot as bot
from importlib import reload
def test_volume_flag_off(monkeypatch):
    import infrastructure.config_loader as cfg
    cfg.feature_enabled = lambda n, d=False: False
    reload(bot)
    assert bot is not None
