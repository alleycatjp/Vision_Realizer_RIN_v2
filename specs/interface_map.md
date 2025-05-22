# Interface Map

## 外部インターフェース

- Exchange Adapter（infrastructure/adapters/*.py）
- Config JSON（config/*.json）
- UI層（presentation/ui_streamlit/ui.py）

## 内部接続

- application 層 ⇔ domain 層 ⇔ infrastructure 層
- strategy_executor → order_executor
- risk_controller → order_executor
