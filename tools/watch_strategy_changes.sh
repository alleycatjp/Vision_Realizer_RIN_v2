#!/bin/bash
# strategy_executor.py に変更があれば自動更新を実行
WATCH_FILE=~/Vision_Realizer_RIN_v2/application/strategy_executor.py
LAST_HASH=""

while true; do
  NEW_HASH=$(md5sum "$WATCH_FILE" | awk '{print $1}')
  if [ "$NEW_HASH" != "$LAST_HASH" ]; then
    echo "strategy_executor.py changed. Running spec_sync..."
    python3 ~/Vision_Realizer_RIN_v2/tools/spec_sync.py
    LAST_HASH=$NEW_HASH
  fi
  sleep 10
done
