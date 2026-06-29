#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- trees schema ---"
sqlite3 data.db '.schema trees' | head -30
echo ""
echo "--- blockchain_jobs schema ---"
sqlite3 data.db '.schema blockchain_jobs'
echo ""
echo "--- env context count ---"
sqlite3 data.db 'SELECT COUNT(*) FROM environmental_context;'
echo ""
echo "--- stories count ---"
sqlite3 data.db 'SELECT COUNT(*) FROM stories;'
