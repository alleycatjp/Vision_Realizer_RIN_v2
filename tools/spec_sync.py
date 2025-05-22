#!/usr/bin/env python3
import os
import shutil
import datetime

SPEC_NAME = "strategy_spec.md"
SPEC_DIR = os.path.expanduser("~/Vision_Realizer_RIN_v2/specs")
ARCHIVE_DIR = os.path.join(SPEC_DIR, ".archive")
SPEC_PATH = os.path.join(SPEC_DIR, SPEC_NAME)

def backup_existing_file():
    if os.path.exists(SPEC_PATH):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = os.path.join(ARCHIVE_DIR, f"{timestamp}_{SPEC_NAME}")
        shutil.copy2(SPEC_PATH, archive_path)
        print(f"Backed up: {archive_path}")
    else:
        print("No existing spec file found. Skipping backup.")

def update_spec_file():
    content = """# Strategy Specification

## 概要

このファイルは Vision_Realizer_RIN に搭載された各戦術モジュールの仕様・アルゴリズム・切替条件を記録します。

## 現在の戦術カテゴリ

- range
- trend
- volatility
- bear
- fallback

## 更新履歴

- 自動更新: {timestamp}

## 各戦術の切替ロジック

- market_state により現在の相場を判定
- 相場の分類に応じて strategy_executor が戦術を選定
- スイッチングは自動／ノンストップで行われる
""".format(timestamp=datetime.datetime.now().isoformat())

    with open(SPEC_PATH, "w") as f:
        f.write(content)
    print(f"Updated spec: {SPEC_PATH}")

if __name__ == "__main__":
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    backup_existing_file()
    update_spec_file()
