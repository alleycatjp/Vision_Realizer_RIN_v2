# Strategy Specification

## 概要

本ファイルは Vision_Realizer_RIN に搭載された各戦術モジュール（strategy）の仕様・アルゴリズム・切替条件について記述する。

## 現在の戦術カテゴリ

- range
- trend
- volatility
- bear
- fallback

## 各戦術の切替ロジック

- market_state により現在の相場を判定
- 相場の分類に応じて strategy_executor が戦術を選定
- スイッチングは自動／ノンストップで行われる
