import pathlib
class BaseAdapter:
    """各取引所アダプターの共通基底クラス"""
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        # ファイル名 (.py) を取引所 ID に自動設定
        cls.name = cls.__module__.split(".")[-1]
    def fetch_tickers(self):
        raise NotImplementedError
