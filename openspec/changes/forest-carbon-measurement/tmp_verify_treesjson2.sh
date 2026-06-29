#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== 從 GitHub API 抓 trees.json (即時) ==="
TS=$(date +%s)
curl -s "https://api.github.com/repos/Yuchiaoniu/forest-carbon-measurement/contents/public/data/trees.json?ref=master&_t=$TS" -o /tmp/contents.json
python3 <<'PY'
import json, base64
with open('/tmp/contents.json') as f:
    res = json.load(f)
content = base64.b64decode(res['content']).decode('utf-8')
data = json.loads(content)
sha = res['sha'][:8]
size = res['size']
print('GitHub commit sha:', sha)
print('檔案大小:', size, 'bytes')
print('總樹數:', len(data))
win = {}
for t in data:
    w = t.get('winnerPath') or '?'
    win[w] = win.get(w, 0) + 1
print('winner 分布:', win)
filled_path0 = sum(1 for t in data if (t.get('paths', {}).get('path0') or {}).get('dbhCm'))
print('paths.path0.dbhCm 有值:', filled_path0)
total_c = sum(t.get('carbonKg', 0) or 0 for t in data)
print('總碳量 (carbonKg):', round(total_c, 1), 'kg')
print('--- 抽 3 棵 ---')
for t in data[:3]:
    p0 = t.get('paths', {}).get('path0') or {}
    tid = t['id'][:8]
    dbh = t.get('dbhCm', '?')
    p0dbh = p0.get('dbhCm', '?')
    w = t.get('winnerPath', '?')
    mdbh = t.get('manualTapeDbhCm', '-')
    print(f'  id={tid} dbh={dbh} path0.dbh={p0dbh} winner={w} manualDbh={mdbh}')
PY
echo
echo "=== DB ground truth ==="
sqlite3 -header -column data.db "
SELECT COUNT(*) AS total,
  SUM(CASE WHEN winner_path='path0' THEN 1 ELSE 0 END) AS winner_path0,
  ROUND(SUM(carbon_kg), 1) AS total_carbon_kg
FROM trees;
"
