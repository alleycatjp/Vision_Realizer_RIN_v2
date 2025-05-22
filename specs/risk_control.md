# Risk Control Specification

## リスク制御の基本方針

- 「負けないこと」を最優先とする
- NAV × ATR によるロットサイズ調整
- ATR 連動ストップ幅により、許容リスクを定量化

## 機能一覧

- 自動ロット調整機能
- ATR に基づいた損切り幅算出
- DD 閾値による killswitch トリガ
