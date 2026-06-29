#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- which trees not in event 6138... ---"
sqlite3 data.db "SELECT id, video_original_name, event_id FROM trees WHERE event_id IS NULL OR event_id != '6138fc64-6670-42a7-bd38-4dfe8c02cf12';"
echo ""
echo "--- tmp_frames dir ---"
ls -la tmp_frames 2>/dev/null | head -10
echo ""
echo "--- dashboard endpoints ---"
grep -nE 'app\.(get|post)' src/index.js | head -30
echo ""
echo "--- dashboard.html refs to frames/paths ---"
grep -nE 'frame|path0|pathA|pathB|關鍵幀' public/dashboard.html | head -20
echo ""
echo "--- public/videos ---"
ls public/videos 2>/dev/null | head -5
echo ""
echo "--- evidence dir ---"
ls -la evidence 2>/dev/null | head -10
