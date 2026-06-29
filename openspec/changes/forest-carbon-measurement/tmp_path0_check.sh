#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== Path 0 覆蓋率 + 跟手動皮尺值是否一致 ==="
sqlite3 -header -column data.db "
SELECT
  COUNT(*) AS total,
  SUM(CASE WHEN path0_dbh_cm IS NOT NULL THEN 1 ELSE 0 END) AS path0_has_value,
  SUM(CASE WHEN manual_tape_dbh_cm IS NOT NULL THEN 1 ELSE 0 END) AS manual_has_value,
  SUM(CASE WHEN path0_dbh_cm IS NOT NULL AND manual_tape_dbh_cm IS NOT NULL
            AND ABS(path0_dbh_cm - manual_tape_dbh_cm) < 0.5 THEN 1 ELSE 0 END) AS path0_matches_manual,
  SUM(CASE WHEN manual_tape_frame_ts_sec IS NOT NULL THEN 1 ELSE 0 END) AS manual_has_ts
FROM trees;
"
echo
echo "=== 抽 5 棵看 path0 vs manual_tape 差距 ==="
sqlite3 -header -column data.db "
SELECT substr(id,1,8) AS id,
       path0_dbh_cm AS p0_dbh,
       manual_tape_dbh_cm AS m_dbh,
       manual_tape_frame_ts_sec AS m_ts,
       ROUND(path0_dbh_cm - manual_tape_dbh_cm, 1) AS p0_minus_m
FROM trees
WHERE manual_tape_dbh_cm IS NOT NULL
LIMIT 5;
"
echo
echo "=== Path 0 關鍵幀目錄是否存在 ==="
ls uploads/ | head -20
echo "---"
if [ -d uploads/path0-evidence ]; then
  echo "uploads/path0-evidence/ 內檔案數: $(ls uploads/path0-evidence/ | wc -l)"
else
  echo "uploads/path0-evidence/ 目錄不存在"
fi
echo
echo "=== trees.json 裡 path0 是用哪個值（抽第一棵） ==="
sqlite3 data.db "SELECT id, path0_dbh_cm, manual_tape_dbh_cm FROM trees WHERE manual_tape_dbh_cm IS NOT NULL LIMIT 1;" | head -1
