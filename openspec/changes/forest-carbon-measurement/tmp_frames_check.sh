#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== tmp_frames_dir 在 DB 裡的數量 ==="
sqlite3 -header -column data.db "SELECT
  COUNT(*) AS total,
  SUM(CASE WHEN tmp_frames_dir IS NOT NULL THEN 1 ELSE 0 END) AS with_dir
FROM trees;"
echo
echo "=== 抽 5 棵看 tmp_frames_dir 路徑與內容 ==="
sqlite3 data.db "SELECT id, tmp_frames_dir FROM trees WHERE tmp_frames_dir IS NOT NULL LIMIT 5" | while IFS='|' read tid dir; do
  echo "tree=$tid dir=$dir"
  if [ -d "$dir" ]; then
    ls "$dir" 2>/dev/null | head -10
    echo "(file count: $(ls "$dir" 2>/dev/null | wc -l))"
  else
    echo "  (目錄不存在)"
  fi
  echo "---"
done
echo
echo "=== tmp_frames/ 根目錄狀況 ==="
ls -d tmp_frames/* 2>/dev/null | head -5
echo "tmp_frames 子目錄總數: $(ls -d tmp_frames/* 2>/dev/null | wc -l)"
echo
echo "=== server 端 path0 evidence 如何組出來 (index.js 736+) ==="
sed -n '700,800p' src/index.js
