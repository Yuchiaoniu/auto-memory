#!/bin/bash
cd ~/forest-carbon-measurement
echo "--- last 5 commits ---"
git log --oneline -5
echo ""
echo "--- diff name-only HEAD~1..HEAD ---"
git diff --name-only HEAD~1 HEAD
echo ""
CHANGED=$(git diff --name-only HEAD~1 HEAD | grep -v -E '^(public/data/trees\.json)$' | head -1)
if [ -z "$CHANGED" ]; then
  echo "RESULT: DATA_ONLY (would skip restart)"
else
  echo "RESULT: CODE_CHANGE in $CHANGED (would restart)"
fi
echo ""
echo "--- diff name-only HEAD~3..HEAD (broader sample) ---"
git diff --name-only HEAD~3 HEAD
CHANGED3=$(git diff --name-only HEAD~3 HEAD | grep -v -E '^(public/data/trees\.json)$' | head -1)
if [ -z "$CHANGED3" ]; then
  echo "RESULT: DATA_ONLY"
else
  echo "RESULT: CODE_CHANGE in $CHANGED3"
fi
