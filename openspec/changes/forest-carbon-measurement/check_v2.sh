#!/bin/bash
DB=~/forest-carbon-measurement/data.db
echo "v2done=$(grep -c 'done]' ~/p4_v2.log)/30  fatal=$(grep -c FATAL ~/p4_v2.log)  batch=$(ps aux|grep run_v2.sh|grep -v grep|wc -l)"
echo "p4v2rows=$(sqlite3 "$DB" "SELECT COUNT(*) FROM trees WHERE winner_path='p4v2'")"
echo "--- sample p4v2 (id, species, source, dbh, carbon) ---"
sqlite3 -separator ' | ' "$DB" "SELECT substr(id,1,8), species, species_source, dbh_cm, round(carbon_kg,1) FROM trees WHERE winner_path='p4v2' LIMIT 4"
echo "--- v2 log errors (last 4) ---"
grep 'DBH=' ~/p4_v2.log | tail -4
