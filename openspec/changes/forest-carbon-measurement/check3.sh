#!/bin/bash
echo "=node rerun_p4 procs= $(ps aux | grep rerun_p4 | grep -v grep | wc -l)"
echo "=run3.sh proc= $(ps aux | grep run3.sh | grep -v grep | wc -l)"
echo "=winner_path=p4 count= $(sqlite3 ~/forest-carbon-measurement/data.db "SELECT COUNT(*) FROM trees WHERE winner_path='p4'")"
echo "=p4 trees (id, species, dbh, original_dbh)="
sqlite3 -separator ' | ' ~/forest-carbon-measurement/data.db "SELECT substr(id,1,8), species, dbh_cm, original_dbh_cm FROM trees WHERE winner_path='p4'"
echo "=latest tmp video dir size="
ls -la /tmp/p4_videos/ 2>/dev/null | tail -5
