# System Overview

## RINの本質

Vision_Realizer_RIN は、複数市場に対応しながら「負けないこと」を最優先に設計された、自律運用Botである。

## アーキテクチャ構成

- application/...   ← 操作制御層
- domain/...        ← 戦術判断ロジック層
- infrastructure/... ← 実世界データI/O、取引所連携
- config/...        ← 抽象化された設定ファイル群
- tools/...         ← 開発支援スクリプト
- presentation/...  ← UI層（streamlit）

## 自動切替・最適化の構造

- 状況判断モジュール（market_state）
- 戦術切替モジュール（strategy_executor）
- リスク制御モジュール（risk_controller）
