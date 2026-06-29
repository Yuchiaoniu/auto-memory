#!/bin/bash
# 守門員：等 p4_batch.log 累積到 15 個 [done] 就停掉批次
while true; do
  n=$(grep -c '\[done\]' ~/p4_batch.log 2>/dev/null)
  if [ "${n:-0}" -ge 15 ]; then
    pkill -f run_all.sh
    pkill -f rerun_p4.js
    echo "" >> ~/p4_batch.log
    echo "=== AUTO-STOPPED at ${n} done ===" >> ~/p4_batch.log
    break
  fi
  sleep 20
done
