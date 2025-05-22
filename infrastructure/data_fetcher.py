# !/usr/bin/env python3
"""Module documentation follows."""
"""
infrastructure/data_fetcher.py
― 登録されたすべての取引所アダプタからティッカーを取得し
  user_data/price_data/cp/<exchange>/<pair>.csv へ保存するワンショットスクリプト
"""

from infrastructure.adapters import registry     # dict { DEFAULT_EXCHANGE: <module>, ... }
from infrastructure import loader                # loader.save(list[dict]) → CSV 保存


def main() -> None:
    all_ticks = []

    for name, module in registry.items():
        print(f"fetch ⇢ {name}")
        all_ticks.extend(module.fetch_tickers())     # 各 adapter は fetch_tickers() 実装必須

    loader.save(all_ticks)                           # exchange 別に自動で振り分け保存
    print(f"saved {len(all_ticks)} tickers.")


if __name__ == "__main__":
    main()
