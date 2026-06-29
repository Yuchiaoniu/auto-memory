#!/bin/bash
cd ~/forest-carbon-measurement
echo "=== DRYRUN_RUNS COUNT ==="
sqlite3 data.db "SELECT COUNT(*) FROM dryrun_runs;" 2>&1
echo "=== DRYRUN_RUNS COLUMNS ==="
sqlite3 data.db "PRAGMA table_info(dryrun_runs);" 2>&1 | awk -F'|' '{print $2}'
echo "=== DRYRUN PIPELINE VERSIONS ==="
sqlite3 data.db "SELECT pipeline_version, COUNT(*) FROM dryrun_runs GROUP BY pipeline_version;" 2>&1 | head -30
echo "=== trees with video_drive_url ==="
sqlite3 data.db "SELECT COUNT(*) FROM trees WHERE video_drive_url IS NOT NULL AND video_drive_url != '';" 2>&1
echo "=== trees tmp_frames_dir sample ==="
sqlite3 -header data.db "SELECT id, tmp_frames_dir FROM trees WHERE tmp_frames_dir IS NOT NULL AND tmp_frames_dir != '' LIMIT 6;" 2>&1
echo "=== STANDARD PIPELINE: index.js species voting + frame keys ==="
grep -niE 'plantnet|inatural|identifySpecies|species|leafFrame|frameIndices|evidenceFrame|keyframe' src/index.js 2>&1 | head -40
echo "=== P4 SCRIPT frame handling (dryrun-video-v2.js) ==="
grep -niE 'frame|keyframe|frameIdx|chosenFrame|responseSchema|leaf' scripts/dryrun-video-v2.js 2>&1 | head -40
echo "=== geminiService: does any function return a frame index? ==="
grep -niE 'frameIndex|frameIdx|keyframe|leafFrameIndices|bestFrame|selectedFrame|frame_index' src/services/geminiService.js 2>&1 | head -40
echo "=== DONE ==="
