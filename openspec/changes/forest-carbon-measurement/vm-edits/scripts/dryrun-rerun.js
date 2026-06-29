// scripts/dryrun-rerun.js  §38.3 重抽模式
// 沙箱重測：從 Drive 下載原始影片 → 2fps 密集重抽 → 並跑 legacy/opencv 雙路徑
//   - Legacy（§32）：orthogonal cards 中 sharpness top 3 + analyzeTrunkPathAOnly
//   - OpenCV（§35.7）：first/middle/last of orthogonal + 2 filler + 完整 prompt
// Path 0 直接讀 manual_tape_dbh_cm（不再算 OCR）
// 不複製 frames、不動 trees / blockchain_jobs / frame_analyses
// Usage: node scripts/dryrun-rerun.js <tree_id_prefix>

require('dotenv').config()
const fs   = require('fs')
const path = require('path')
const { spawnSync } = require('child_process')
const { getDb } = require('../src/db/init')
const {
  analyzeTrunkWithRetry, getMedianResult,
  analyzeTrunkPathAOnly, getPathAMedianRatio,
} = require('../src/services/geminiService')
const { selectRegularFrames, frameToBase64 } = require('../src/services/frameService')
const { calculate } = require('../src/services/calculationService')

const DETECT_PY     = path.join(__dirname, 'detect_card.py')
const GDOWN_BIN     = '/home/yuchi/.local/bin/gdown'
const DRYRUN_VIDS   = '/tmp/dryrun_videos'
const DRYRUN_FRAMES = '/tmp/dryrun_frames'
const PIPELINE_VER  = '35.7+legacy32+resample'

function parseDriveFileId(url) {
  if (!url) return null
  const m = url.match(/\/d\/([a-zA-Z0-9_-]+)/) || url.match(/[?&]id=([a-zA-Z0-9_-]+)/)
  return m ? m[1] : null
}

function downloadFromDrive(fileId, destPath) {
  // gdown 6.x: 直接傳 fileId（或 URL）為 positional arg，不再用 --id
  const r = spawnSync(GDOWN_BIN, [fileId, '-O', destPath, '-q'], {
    encoding: 'utf8', timeout: 600000,
  })
  if (r.status !== 0 || !fs.existsSync(destPath) || fs.statSync(destPath).size < 1024) {
    throw new Error(`gdown failed: stderr=${(r.stderr || '').slice(0, 300)}`)
  }
}

async function main() {
  const treePrefix = process.argv[2]
  if (!treePrefix) {
    console.error('Usage: node scripts/dryrun-rerun.js <tree_id_prefix>')
    process.exit(1)
  }

  const db   = getDb()
  const tree = db.prepare('SELECT * FROM trees WHERE id LIKE ?').get(treePrefix + '%')
  if (!tree) { console.error(`tree not found: ${treePrefix}`); process.exit(1) }

  const manualTape = tree.manual_tape_dbh_cm
  if (!manualTape) {
    console.error('manual_tape_dbh_cm 為空，無 baseline 比誤差')
    process.exit(1)
  }

  const fileId = parseDriveFileId(tree.video_drive_url)
  if (!fileId) {
    console.error(`video_drive_url 為空或無法解析: ${tree.video_drive_url}`)
    process.exit(1)
  }

  console.log(`tree: ${tree.id.slice(0, 8)}  ${tree.video_original_name || ''}`)
  console.log(`drive file_id: ${fileId}`)
  console.log(`manual_tape: ${manualTape} cm  old pathA: ${tree.pathA_dbh_cm} cm\n`)

  fs.mkdirSync(DRYRUN_VIDS,   { recursive: true })
  fs.mkdirSync(DRYRUN_FRAMES, { recursive: true })

  // 1. 取得影片（cache 在 /tmp/dryrun_videos/<id8>.mov；24h 後 cleanup 會清）
  const videoPath = path.join(DRYRUN_VIDS, `${tree.id.slice(0, 8)}.mov`)
  if (fs.existsSync(videoPath) && fs.statSync(videoPath).size > 1024 * 1024) {
    console.log(`[video] cache 命中：${videoPath} (${Math.round(fs.statSync(videoPath).size/1024/1024)} MB)`)
  } else {
    console.log(`[video] 從 Drive 下載 file_id=${fileId} ...`)
    downloadFromDrive(fileId, videoPath)
    console.log(`[video] OK: ${Math.round(fs.statSync(videoPath).size/1024/1024)} MB`)
  }

  // 2. 2fps 重抽 + OpenCV 偵測
  const runId = Date.now()
  const framesDir = path.join(DRYRUN_FRAMES, String(runId))
  fs.mkdirSync(framesDir, { recursive: true })
  console.log(`\n[detect] detect_card.py --video --fps 2 → ${framesDir}`)
  const r = spawnSync('python3',
    [DETECT_PY, '--video', videoPath, '--fps', '2', '--save-dir', framesDir],
    { encoding: 'utf8', timeout: 600000 })
  if (r.status !== 0 || !r.stdout.trim()) {
    console.error('detect_card.py failed:', (r.stderr || '').slice(0, 400))
    process.exit(1)
  }
  const detectResults = JSON.parse(r.stdout)
  const allFrames    = detectResults
  const cardDetected = detectResults.filter(f => f.cardDetected)
  const orthogonal   = detectResults.filter(f => f.cardDetected && f.isOrthogonal)

  console.log(`[detect] total=${allFrames.length}  cardDetected=${cardDetected.length}  orthogonal=${orthogonal.length}`)

  // 3. LEGACY 路：orthogonal cards 中 sharpness top 3
  console.log('\n[legacy] §32: orthogonal cards 中 sharpness top 3 + credit-card-only prompt')
  let legacyCandidates = [...orthogonal].sort((a, b) => b.sharpness - a.sharpness).slice(0, 3)
  if (legacyCandidates.length === 0 && cardDetected.length > 0) {
    console.log('[legacy] 無正交卡，fallback 到 cardDetected sharpness top 3')
    legacyCandidates = [...cardDetected].sort((a, b) => b.sharpness - a.sharpness).slice(0, 3)
  }
  console.log(`[legacy] picked ${legacyCandidates.length} frames: ${legacyCandidates.map(f => path.basename(f.path)).join(',')}`)

  let legacyDbh = null, legacyRatio = null, legacyConf = null, legacyRaw = null
  if (legacyCandidates.length > 0) {
    const legacyBase64s = legacyCandidates.map(f => frameToBase64(f.path))
    legacyRaw = await analyzeTrunkPathAOnly(legacyBase64s)
    const legacyMedian = getPathAMedianRatio(legacyRaw.frames || [])
    legacyDbh = legacyMedian?.dbhCm ?? null
    legacyRatio = legacyMedian?.ratio ?? null
    legacyConf = legacyMedian?.confidence ?? null
  }
  const legacyErr = legacyDbh ? Math.abs(legacyDbh - manualTape) / manualTape * 100 : null
  console.log(`[legacy] DBH = ${legacyDbh} cm  err vs manual = ${legacyErr?.toFixed(1)}%`)

  // 4. OPENCV 路（§35.7）：first/middle/last of orthogonal + 2 filler + 完整 prompt
  console.log('\n[opencv] §35.7: first/middle/last of orthogonal + 2 filler + 完整 prompt')
  const sortedCardsByTime = [...orthogonal].sort((a, b) => a.frameIdx - b.frameIdx)
  let pickedCards = []
  if (sortedCardsByTime.length >= 3) {
    pickedCards = [
      sortedCardsByTime[0],
      sortedCardsByTime[Math.floor(sortedCardsByTime.length / 2)],
      sortedCardsByTime[sortedCardsByTime.length - 1],
    ]
  } else {
    pickedCards = sortedCardsByTime
  }
  const cardIdxSet    = new Set(pickedCards.map(f => f.frameIdx))
  const nonCardFrames = allFrames.filter(f => !cardIdxSet.has(f.frameIdx))
  const fillerCount   = Math.max(0, 5 - pickedCards.length)
  const fillerFrames  = selectRegularFrames(nonCardFrames, fillerCount)
  const opencvFrames  = [...pickedCards, ...fillerFrames].sort((a, b) => a.frameIdx - b.frameIdx)

  console.log(`[opencv] picked ${pickedCards.length} cards + ${fillerFrames.length} filler; idxs = [${opencvFrames.map(f => f.frameIdx).join(',')}]`)

  const opencvBase64s = opencvFrames.map(f => frameToBase64(f.path))
  const metadata = {
    imageWidth:    tree.image_width  || 1920,
    imageHeight:   tree.image_height || 1080,
    focalLengthMm: tree.focal_length_mm,
    sensorWidthMm: tree.sensor_width_mm,
  }
  let opencvDbh = null, opencvMed = null, opencvRaw = null
  if (opencvBase64s.length > 0) {
    opencvRaw = await analyzeTrunkWithRetry(opencvBase64s, metadata)
    opencvMed = getMedianResult(opencvRaw.frames || [], metadata.imageWidth, metadata.imageHeight)
    if (opencvMed) {
      const calc = calculate({
        species:                   tree.species,
        pixelWidth:                opencvMed.pixelWidth,
        estimatedDistanceM:        opencvMed.estimatedDistanceM,
        distanceStdPct:            opencvMed.distanceStdPct,
        validFrames:               opencvMed.validFrames,
        metadata,
        frameQuality:              'good',
        referenceDetected:         opencvMed.referenceDetected,
        referenceType:             opencvMed.referenceType,
        trunkToReferenceRatio:     opencvMed.trunkToReferenceRatio,
        referencePixelWidth:       opencvMed.referencePixelWidth,
        referencePixelHeight:      opencvMed.referencePixelHeight,
        referenceEstimatedWidthMm: opencvMed.referenceEstimatedWidthMm,
        referenceConfidence:       opencvMed.referenceConfidence,
        directMeasurementCm:       0,    // §38.2: Path 0 不再算 OCR
        measurementType:           '',
        referenceOffTrunkDetected: false,
      })
      opencvDbh = calc.paths?.pathA?.dbhCm ?? null
    }
  }
  const opencvErr = opencvDbh ? Math.abs(opencvDbh - manualTape) / manualTape * 100 : null
  console.log(`[opencv] DBH = ${opencvDbh} cm  err vs manual = ${opencvErr?.toFixed(1)}%`)

  // 5. winner
  let winnerStrategy = null, winnerDbh = null
  if (legacyErr != null && opencvErr != null) {
    if (legacyErr <= opencvErr) { winnerStrategy = 'legacy'; winnerDbh = legacyDbh }
    else                        { winnerStrategy = 'opencv'; winnerDbh = opencvDbh }
  } else if (legacyErr != null) { winnerStrategy = 'legacy'; winnerDbh = legacyDbh }
  else if (opencvErr != null)   { winnerStrategy = 'opencv'; winnerDbh = opencvDbh }

  // 6. 寫 dryrun_runs
  const info = db.prepare(`
    INSERT INTO dryrun_runs (
      tree_id, tree_label, pipeline_version, tmp_frames_dir,
      all_card_frames_json, selected_frame_idxs_json, gemini_frames_json, median_json,
      dbh_cm, winner_path,
      baseline_manual_tape_cm, baseline_path0_cm, baseline_pathA_cm,
      error_vs_baseline_pct, error_vs_old_pathA_pct, notes,
      path0_dbh_cm,
      pathA_legacy_dbh_cm, pathA_legacy_ratio, pathA_legacy_confidence,
      pathA_legacy_frame_idxs_json, pathA_legacy_raw_json,
      pathA_opencv_dbh_cm, pathA_opencv_frame_idxs_json,
      error_pathA_legacy_pct, error_pathA_opencv_pct,
      pathA_winner_strategy, pathA_winner_dbh_cm
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    tree.id,
    tree.video_original_name || null,
    PIPELINE_VER,
    `dryrun_frames/${runId}`,
    JSON.stringify(orthogonal.map(f => ({ idx: f.frameIdx, sharp: f.sharpness, angDev: f.angleDev }))),
    JSON.stringify(opencvFrames.map(f => f.frameIdx)),
    JSON.stringify(opencvRaw?.frames || []),
    JSON.stringify(opencvMed || null),
    winnerDbh,
    winnerStrategy ? `pathA_${winnerStrategy}` : null,
    manualTape,
    tree.path0_dbh_cm || null,
    tree.pathA_dbh_cm || null,
    winnerDbh && manualTape ? Math.abs(winnerDbh - manualTape) / manualTape * 100 : null,
    winnerDbh && tree.pathA_dbh_cm ? Math.abs(winnerDbh - tree.pathA_dbh_cm) / tree.pathA_dbh_cm * 100 : null,
    `resample 2fps; allFrames=${allFrames.length}; orthogonal=${orthogonal.length}`,
    manualTape,
    legacyDbh,
    legacyRatio,
    legacyConf,
    JSON.stringify(legacyCandidates.map(f => f.frameIdx)),
    JSON.stringify(legacyRaw?.frames || []),
    opencvDbh,
    JSON.stringify(opencvFrames.map(f => f.frameIdx)),
    legacyErr,
    opencvErr,
    winnerStrategy,
    winnerDbh
  )

  console.log(`\n=== dryrun #${info.lastInsertRowid} (resample) ===`)
  console.log(`manual_tape (Path 0):     ${manualTape} cm`)
  console.log(`old pathA (DB):           ${tree.pathA_dbh_cm} cm`)
  console.log(`new pathA (legacy §32):   ${legacyDbh} cm  err=${legacyErr?.toFixed(1)}%`)
  console.log(`new pathA (opencv §35.7): ${opencvDbh} cm  err=${opencvErr?.toFixed(1)}%`)
  console.log(`winner:                   ${winnerStrategy ? `pathA_${winnerStrategy}` : 'none'} → ${winnerDbh} cm`)
  console.log(`frames at: ${framesDir}/  (${allFrames.length} frames)`)
}

main().catch(err => { console.error('ERROR:', err); process.exit(1) })
