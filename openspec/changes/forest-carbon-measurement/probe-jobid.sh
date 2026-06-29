#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- trees columns relevant to jobid/frames ---"
sqlite3 data.db "PRAGMA table_info(trees);" | grep -iE 'job|frame|tmp|raw|video'
echo ""
echo "--- raw_result keys (one sample) ---"
sqlite3 data.db "SELECT raw_result FROM trees LIMIT 1;" | head -c 1200
echo ""
echo ""
echo "--- tmp_frames dirs vs trees count ---"
ls tmp_frames 2>/dev/null | wc -l
sqlite3 data.db "SELECT COUNT(*) FROM trees;"
echo ""
echo "--- match jobId to tree via raw_result.jobId? ---"
sqlite3 data.db "SELECT id, json_extract(raw_result, '\$.jobId') FROM trees LIMIT 3;"
echo ""
echo "--- evidence-frame file sample size ---"
ls -la uploads/evidence 2>/dev/null | head -5
