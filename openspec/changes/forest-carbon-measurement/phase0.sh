#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== TREES COUNT ==="
sqlite3 data.db "SELECT COUNT(*) FROM trees;"
echo "=== SPECIES/VIDEO/FRAME COLUMNS ==="
sqlite3 data.db "PRAGMA table_info(trees);" | awk -F'|' '{print $2}' | grep -iE 'spec|scientif|common|name|video|tmp_frames|raw_result'
echo "=== SPECIES DATA (id, species, source) ==="
sqlite3 -header data.db "SELECT id, species, species_source FROM trees ORDER BY id;" 2>&1 | head -40
echo "=== SPECIES_SOURCE COUNTS ==="
sqlite3 data.db "SELECT species_source, COUNT(*) FROM trees GROUP BY species_source;" 2>&1
echo "=== BLOCKCHAIN_JOBS COLUMNS ==="
sqlite3 data.db "PRAGMA table_info(blockchain_jobs);" | awk -F'|' '{print $2}'
echo "=== BC SAMPLE ==="
sqlite3 -header data.db "SELECT tree_id, tx_status, tx_hash FROM blockchain_jobs LIMIT 5;" 2>&1
echo "=== SERVICES FILES ==="
ls ~/forest-carbon-measurement/src/services/ | grep -iE 'plantnet|inatural|gemini|blockchain'
echo "=== EXPLORER: DOCKER ==="
(docker ps --format '{{.Names}} | {{.Image}} | {{.Ports}}' 2>/dev/null || echo 'docker not available')
echo "=== EXPLORER: LISTENING PORTS ==="
(ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null) | grep -E ':(8545|8546|4000|8080|3000|26000|443|80)' || echo 'no matching ports'
echo "=== EXPLORER: PROCESSES ==="
ps aux | grep -iE 'blockscout|expedition|epirus|sirato|ethereum-lite|explorer' | grep -v grep || echo 'no explorer process'
echo "=== BESU eth_blockNumber ==="
curl -s -X POST http://localhost:8545 -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
echo ""
echo "=== DONE ==="
