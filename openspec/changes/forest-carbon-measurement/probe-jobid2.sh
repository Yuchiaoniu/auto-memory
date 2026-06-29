#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- video_filename sample (might contain jobId?) ---"
sqlite3 data.db "SELECT id, video_original_name, video_filename, video_drive_url FROM trees LIMIT 5;"
echo ""
echo "--- tmp_frames dir mtimes vs tree created_at ---"
sqlite3 data.db "SELECT id, video_original_name, datetime(created_at, 'unixepoch') FROM trees ORDER BY created_at LIMIT 5;"
echo ""
ls -lat tmp_frames | head -10
echo ""
echo "--- check raw_result top-level keys ---"
sqlite3 data.db "SELECT json_each.key FROM trees, json_each(trees.raw_result) WHERE trees.id = (SELECT id FROM trees LIMIT 1);"
echo ""
echo "--- search raw_result for jobId anywhere ---"
sqlite3 data.db "SELECT id FROM trees WHERE raw_result LIKE '%jobId%' LIMIT 3;"
echo ""
echo "--- check uploads dir for original video ---"
ls uploads/ 2>/dev/null | head -10
