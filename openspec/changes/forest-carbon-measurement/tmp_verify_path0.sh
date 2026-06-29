#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== 抽 3 棵驗證 /api/trees/:id/path-frames evidence ==="
sqlite3 data.db "SELECT id FROM trees ORDER BY id LIMIT 3" | while read TID; do
  echo "--- tree=$TID ---"
  curl -s "http://localhost:3000/api/trees/$TID/path-frames" | python3 -c '
import json, sys
d = json.load(sys.stdin)
out = {
  "winnerPath": d.get("winnerPath"),
  "tmpFramesDir": d.get("tmpFramesDir"),
  "path0": d.get("paths", {}).get("path0"),
}
print(json.dumps(out, indent=2, ensure_ascii=False))
'
done
echo
echo "=== 確認 frame_endpoint 可拿到實際 JPG ==="
TID=$(sqlite3 data.db "SELECT id FROM trees ORDER BY id LIMIT 1")
IDX=$(curl -s "http://localhost:3000/api/trees/$TID/path-frames" | python3 -c '
import json, sys
d = json.load(sys.stdin)
print(d["paths"]["path0"]["evidence"]["frameIdx"])
')
echo "treeId=$TID idx=$IDX"
curl -s -o /tmp/frame_check.jpg -w "http_code=%{http_code} size=%{size_download}\n" \
  "http://localhost:3000/api/trees/$TID/frames/$IDX"
file /tmp/frame_check.jpg
