#!/bin/bash
cd ~/forest-carbon-measurement
run() {
  echo ""
  echo "########## $2 (tape $3) ##########"
  node rerun_p4.js --file-id "$1" --img "$2" --tape "$3" --repeat 10
}
run 1vwIqBt4Zob3wno3999dgfQkF5SSggRi6 IMG_5801 16.9
run 1v6BthyaAo0uY4HvIs-yK5_YETJnWSV-5 IMG_5810 29.9
run 1hAJOWC6SO9urNIn0aLESVQ7u1JUfZeHT IMG_5815 32.5
echo ""
echo "=== ALL 3 DONE ==="
