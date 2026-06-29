#!/bin/bash
# 每 30 秒記錄批次健康狀態到 ~/p4_watch.log；偵測卡住/磁碟滿/批次死掉
WLOG=~/p4_watch.log
: > "$WLOG"
prev_done=-1
stall=0
while true; do
  ts=$(date '+%H:%M:%S')
  done=$(grep -c '\[done\]' ~/p4_batch2.log 2>/dev/null || echo 0)
  fatal=$(grep -c 'FATAL' ~/p4_batch2.log 2>/dev/null || echo 0)
  alive=$(ps aux | grep -E 'run_remaining.sh|rerun_p4' | grep -v grep | wc -l)
  freeM=$(df -m / | tail -1 | awk '{print $4}')
  finished=$(grep -c 'ALL REMAINING DONE' ~/p4_batch2.log 2>/dev/null || echo 0)
  cur=$(grep '##########' ~/p4_batch2.log 2>/dev/null | tail -1 | tr -d '#' | xargs)
  # 進度停滯偵測
  if [ "$done" -eq "$prev_done" ]; then stall=$((stall+1)); else stall=0; fi
  prev_done=$done
  flag=""
  [ "$alive" -eq 0 ] && [ "$finished" -eq 0 ] && flag="$flag [批次已死]"
  [ "$freeM" -lt 250 ] && flag="$flag [磁碟<250MB危險]"
  [ "$stall" -ge 20 ] && [ "$alive" -gt 0 ] && flag="$flag [疑似卡住>10分]"
  [ "$finished" -ge 1 ] && flag="$flag [全部完成]"
  echo "$ts done=$done/23 fatal=$fatal alive=$alive free=${freeM}MB cur=[$cur]$flag" >> "$WLOG"
  [ "$finished" -ge 1 ] && break
  [ "$alive" -eq 0 ] && [ "$finished" -eq 0 ] && { echo "$ts 批次非正常結束，看門狗退出" >> "$WLOG"; break; }
  sleep 30
done
