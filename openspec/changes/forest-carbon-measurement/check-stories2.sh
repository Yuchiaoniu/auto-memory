#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- trees missing Story A ---"
sqlite3 data.db "SELECT t.id, t.video_original_name FROM trees t LEFT JOIN stories s ON s.tree_id=t.id AND s.story_type='A' WHERE s.id IS NULL;"
echo ""
echo "--- which trees got Story A successfully ---"
sqlite3 data.db "SELECT COUNT(DISTINCT tree_id) FROM stories WHERE story_type='A' AND tree_id != '';"
echo ""
echo "--- Story C tree counts mentioned in markdown ---"
sqlite3 data.db "SELECT id, created_at, substr(markdown, instr(markdown,'共 '), 12) FROM stories WHERE story_type='C' ORDER BY created_at;"
