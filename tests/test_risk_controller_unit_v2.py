from importlib import reload

def _toggle(flag: bool):
    """
    feature_flags を切り替えて risk_controller を再読み込み
    """
    import infrastructure.config_loader as cfg
    cfg.feature_enabled = lambda name, default=False: flag
    import application.risk_controller as mod
    reload(mod)
    return mod

def test_v1_logic():
    mod = _toggle(False)                    # 旧ロジック
    assert mod.calc_size(1000, 10) == 10    # NAV * 1 %
    assert mod.calc_stop(100, 10) == 90     # entry - atr

def test_v2_logic():
    mod = _toggle(True)                     # 新ロジック
    size = mod.calc_size(1000, 10)
    stop = mod.calc_stop(100, 10)
    assert 0 < size < 1000                  # NAV を超えない
    assert stop == 100 - 10 * 1.5           # entry - atr * 1.5
