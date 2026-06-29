#!/bin/bash
pkill -f stop10.sh 2>/dev/null
echo "=== df -h / ==="
df -h / | tail -2
echo "=== 大目錄 ==="
du -sh /tmp/p4_videos 2>/dev/null
du -sh /tmp/dryrun_videos 2>/dev/null
du -sh ~/forest-carbon-measurement/tmp_frames 2>/dev/null
du -sh ~/forest-carbon-measurement/uploads 2>/dev/null
du -sh ~/forest-carbon-measurement/data.db.bak-* 2>/dev/null | tail -5
echo "=== /tmp top ==="
du -sh /tmp/* 2>/dev/null | sort -rh | head -8
