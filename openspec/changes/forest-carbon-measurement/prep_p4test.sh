#!/bin/bash
cd ~/forest-carbon-measurement
cp -n data.db "data.db.bak-p4test-$(date +%s)" && echo "[backup] done"
sed -i 's/\r$//' rerun_p4.js
echo "[trees before] $(sqlite3 data.db "SELECT COUNT(*) FROM trees")"
echo -n "[5787 existing id] "
sqlite3 data.db "SELECT id FROM trees WHERE video_drive_url LIKE '%13fgOJO%'"
echo "[done prep]"
