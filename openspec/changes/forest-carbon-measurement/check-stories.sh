#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- stories schema ---"
sqlite3 data.db '.schema stories'
echo ""
echo "--- stories by type ---"
sqlite3 data.db "SELECT story_type, COUNT(*) FROM stories GROUP BY story_type;"
echo ""
echo "--- 'orphan' stories: tree_id empty/null but event_id present? ---"
sqlite3 data.db "SELECT story_type, COUNT(*) FROM stories WHERE tree_id='' OR tree_id IS NULL GROUP BY story_type;"
echo ""
echo "--- sample 'orphan' story (first 200 chars of markdown) ---"
sqlite3 data.db "SELECT story_type, event_id, substr(markdown,1,200) FROM stories WHERE tree_id='' OR tree_id IS NULL LIMIT 3;"
echo ""
echo "--- events count ---"
sqlite3 data.db "SELECT COUNT(*) FROM events;"
