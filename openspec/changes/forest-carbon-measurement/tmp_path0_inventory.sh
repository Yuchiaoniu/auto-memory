#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== 備份 data.db ==="
cp data.db data.db.bak.path0-overwrite
ls -lh data.db data.db.bak.path0-overwrite
echo
echo "=== uploads/ 目錄結構 ==="
ls -F uploads/ | head -40
echo
echo "=== uploads/ 內影片數 ==="
ls uploads/*.mov uploads/*.mp4 uploads/*.MOV uploads/*.MP4 2>/dev/null | wc -l
echo
echo "=== 31 棵樹的 id 跟 uploads/ 影片檔對應狀況 ==="
sqlite3 data.db "SELECT id FROM trees ORDER BY id;" | while read tid; do
  if   [ -f "uploads/${tid}.mov" ]; then echo "  [OK]  $tid → uploads/${tid}.mov"
  elif [ -f "uploads/${tid}.mp4" ]; then echo "  [OK]  $tid → uploads/${tid}.mp4"
  elif [ -f "uploads/${tid}.MOV" ]; then echo "  [OK]  $tid → uploads/${tid}.MOV"
  else echo "  [MISS] $tid"
  fi
done
echo
echo "=== 確認 ffmpeg 已安裝 ==="
which ffmpeg && ffmpeg -version | head -1
echo
echo "=== dashboard.html 內 path0 evidence 顯示邏輯 ==="
grep -n -A 2 "path0\|Path0\|path 0\|路徑0\|path_0" public/dashboard.html | head -40
