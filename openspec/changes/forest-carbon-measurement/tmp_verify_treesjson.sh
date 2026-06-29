#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== 從 GitHub raw 抓 trees.json 驗證 path0 ==="
curl -s "https://raw.githubusercontent.com/Yuchiaoniu/forest-carbon-measurement/master/public/data/trees.json" -o /tmp/trees.gh.json
echo "trees.json 大小: $(wc -c < /tmp/trees.gh.json) bytes"
python3 <<'PY'
import json
with open('/tmp/trees.gh.json') as f:
    data = json.load(f)
print(f"總樹數: {len(data)}")
win = {}
for t in data:
    w = t.get('winnerPath') or t.get('winner_path') or t.get('winner') or '?'
    win[w] = win.get(w, 0) + 1
print("winner 分布:", win)
filled_path0 = sum(1 for t in data if (t.get('paths', {}).get('path0') or {}).get('dbhCm'))
print(f"paths.path0.dbhCm 有值: {filled_path0}")
total_c = sum(t.get('carbonKg', 0) or 0 for t in data)
print(f"總碳量 (carbonKg): {total_c:.1f} kg")
print("--- 抽 3 棵 ---")
for t in data[:3]:
    p0 = t.get('paths', {}).get('path0') or {}
    print(f"  id={t['id'][:8]} species={(t.get('species') or '?')[:20]:<20} "
          f"dbh={t.get('dbhCm','?')} path0.dbh={p0.get('dbhCm','?')} winner={t.get('winnerPath','?')} "
          f"manual_dbh={t.get('manualTapeDbhCm','-')}")
PY
echo
echo "=== 比對 DB ==="
sqlite3 -header -column data.db "
SELECT
  COUNT(*) AS total,
  SUM(CASE WHEN winner_path='path0' THEN 1 ELSE 0 END) AS winner_path0,
  ROUND(SUM(carbon_kg), 1) AS total_carbon_kg,
  ROUND(AVG(path0_dbh_cm), 2) AS avg_path0_dbh
FROM trees;
"
