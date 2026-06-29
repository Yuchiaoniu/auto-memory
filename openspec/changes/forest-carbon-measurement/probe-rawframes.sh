#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- raw_result.rawFrames length per tree ---"
sqlite3 data.db "SELECT id, video_original_name, json_array_length(json_extract(raw_result, '\$.rawFrames')) FROM trees ORDER BY created_at LIMIT 5;"
echo ""
echo "--- first rawFrames element shape ---"
sqlite3 data.db "SELECT json_extract(raw_result, '\$.rawFrames[0]') FROM trees LIMIT 1;" | head -c 1500
echo ""
echo ""
echo "--- count trees with rawFrames ---"
sqlite3 data.db "SELECT COUNT(*) FROM trees WHERE json_extract(raw_result, '\$.rawFrames') IS NOT NULL;"
echo ""
echo "--- tmp_frames file count per dir (should be ~13) ---"
for d in $(ls tmp_frames | head -3); do
  echo "$d: $(ls tmp_frames/$d | wc -l) frames"
done
echo ""
echo "--- check rawFrames count vs tmp_frames count for one tree (need mapping) ---"
sqlite3 data.db "SELECT id, json_array_length(json_extract(raw_result, '\$.rawFrames')) FROM trees ORDER BY created_at LIMIT 3;"
