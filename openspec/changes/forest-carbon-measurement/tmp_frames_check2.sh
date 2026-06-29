#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== 31 棵的 tmp_frames/<dir>/ 是否齊全 + 幀數 ==="
sqlite3 data.db "SELECT id, tmp_frames_dir, manual_tape_frame_ts_sec, duration_sec FROM trees ORDER BY id" | while IFS='|' read tid dir ts dur; do
  full="tmp_frames/$dir"
  if [ -d "$full" ]; then
    n=$(ls "$full" 2>/dev/null | wc -l)
    echo "[OK]  ${tid:0:8} frames=$n  manual_ts=${ts}s  duration=${dur}s"
  else
    echo "[MISS] ${tid:0:8} dir=$full manual_ts=${ts}s"
  fi
done | sort | uniq -c | sort -rn | head -10
echo
echo "=== 詳細統計 ==="
sqlite3 -header -column data.db "
SELECT
  COUNT(*) AS total,
  SUM(CASE WHEN tmp_frames_dir IS NOT NULL THEN 1 ELSE 0 END) AS with_dir_in_db,
  SUM(CASE WHEN duration_sec IS NOT NULL THEN 1 ELSE 0 END) AS with_duration
FROM trees;
"
echo
echo "=== 抽 5 棵看 tmp_frames/<dir>/ 內檔名格式 ==="
for dir in $(ls tmp_frames/ | head -5); do
  echo "--- tmp_frames/$dir ---"
  ls tmp_frames/$dir | head -10
done
