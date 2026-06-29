#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== weatherService exports ==="
sed -n '270,290p' src/services/weatherService.js
echo ""
echo "=== eventService exports + helpers ==="
grep -n 'module.exports\|^function assign\|^function setStoryC\|setStoryC\s*=' src/services/eventService.js
echo ""
echo "=== stories db helpers ==="
grep -n 'module.exports\|^function insert\|^function getLatest' src/db/stories.js
echo ""
echo "=== tree metadata for fill targets ==="
sqlite3 data.db "SELECT id, video_original_name, gps, create_date, altitude_m FROM trees WHERE id IN ('32b07239-e856-42bd-9ef1-09978d79013a','e06aa4b9-7d83-43a1-a98c-9c6e69221c6f','3eaea6f9-02a9-4dae-95a0-dba4fbcd3d50','39a452d7-18e1-49a5-8e60-1c4c3931d8b0');"
echo ""
echo "=== event id (only one) ==="
sqlite3 data.db "SELECT id, name FROM events;"
