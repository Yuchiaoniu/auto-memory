// scripts/dryrun-video.js
// 直接把影片送 Gemini（跳過 ffmpeg / OpenCV / detect_card），N=5 取 median
// Usage: node scripts/dryrun-video.js --file-id <drive-fid> --img IMG_xxxx --tape <cm> [--repeat 5]

require('dotenv').config()
const fs = require('fs')
const path = require('path')
const { spawnSync } = require('child_process')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { GoogleAIFileManager, FileState } = require('@google/generative-ai/server')
const { getDb } = require('../src/db/init')

const GDOWN_BIN     = '/home/yuchi/.local/bin/gdown'
const DRYRUN_VIDS   = '/tmp/dryrun_videos'
const PIPELINE_VER  = 'video-direct-v2-N10'
const CREDITCARD_WIDTH_CM = 8.56
const DEFAULT_N = 10
const API_KEY = process.env.GEMINI_API_KEY

const MEASURE_PROMPT = `這是一支樹幹測量影片。畫面中有一張信用卡（國際標準長邊 85.6mm）靠在樹幹上 — **這就是胸高 1.3 公尺的測量位置**。

請看完整支影片，找出**卡片最清晰、最正對鏡頭**的時刻。然後在那個時刻：

1. 量信用卡長邊像素寬 → cardPixelWidth
2. 量「卡片所在的同一個高度」上樹幹的左右邊緣像素寬 → trunkPixelWidth
   ⚠ 不要看樹幹上方或下方、不要看分叉處、不要看細枝
   ⚠ 只看跟卡片同高度（左右水平延伸）的樹幹寬度
   ⚠ 樹幹「主體」邊緣，不含樹皮花紋、附生植物、背景樹、陰影
3. 計算 trunkToCardRatio = trunkPixelWidth / cardPixelWidth
4. videoTimestampSec：你做判斷的影片時間點（第幾秒）— 這欄位用來稽核你看的位置對不對
5. confidence 0.0–1.0

只回傳一組數字。無法判斷時所有數字填 0。`

const SCHEMA = {
  type: SchemaType.OBJECT,
  properties: {
    cardPixelWidth:    { type: SchemaType.NUMBER },
    trunkPixelWidth:   { type: SchemaType.NUMBER },
    trunkToCardRatio:  { type: SchemaType.NUMBER },
    videoTimestampSec: { type: SchemaType.NUMBER },
    confidence:        { type: SchemaType.NUMBER },
  },
  required: ['cardPixelWidth', 'trunkPixelWidth', 'trunkToCardRatio', 'videoTimestampSec', 'confidence'],
}

function median(arr) {
  const v = arr.filter(x => x != null && x > 0).sort((a, b) => a - b)
  if (!v.length) return null
  return v[Math.floor(v.length / 2)]
}
function coeffVar(arr) {
  const v = arr.filter(x => x != null && x > 0)
  if (v.length < 2) return null
  const mean = v.reduce((a, b) => a + b, 0) / v.length
  const std  = Math.sqrt(v.reduce((s, x) => s + (x - mean) ** 2, 0) / v.length)
  return mean > 0 ? (std / mean) * 100 : null
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

function parseDriveFileId(url) {
  if (!url) return null
  const m = url.match(/\/d\/([a-zA-Z0-9_-]+)/) || url.match(/[?&]id=([a-zA-Z0-9_-]+)/)
  return m ? m[1] : null
}

function downloadFromDrive(fileId, destPath) {
  const r = spawnSync(GDOWN_BIN, [fileId, '-O', destPath, '-q'], { encoding: 'utf8', timeout: 600000 })
  if (r.status !== 0 || !fs.existsSync(destPath) || fs.statSync(destPath).size < 1024) {
    throw new Error(`gdown failed: stderr=${(r.stderr || '').slice(0, 300)}`)
  }
}

async function uploadAndWait(fileManager, localPath, imgName) {
  console.log(`[upload] ${path.basename(localPath)} (${Math.round(fs.statSync(localPath).size/1024/1024)} MB)`)
  const t0 = Date.now()
  const result = await fileManager.uploadFile(localPath, {
    mimeType: 'video/quicktime',
    displayName: imgName,
  })
  let file = result.file
  console.log(`[upload] uri=${file.uri} state=${file.state} (${Math.round((Date.now()-t0)/1000)}s)`)
  while (file.state === FileState.PROCESSING) {
    await sleep(3000)
    file = await fileManager.getFile(file.name)
    console.log(`[upload] state=${file.state} (${Math.round((Date.now()-t0)/1000)}s)`)
  }
  if (file.state !== FileState.ACTIVE) {
    throw new Error(`File upload failed, state=${file.state}`)
  }
  console.log(`[upload] ACTIVE after ${Math.round((Date.now()-t0)/1000)}s total`)
  return file
}

async function callGemini(genAI, file, idx) {
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: { responseMimeType: 'application/json', responseSchema: SCHEMA },
  })
  const result = await model.generateContent([
    { fileData: { mimeType: file.mimeType, fileUri: file.uri } },
    { text: MEASURE_PROMPT },
  ])
  return JSON.parse(result.response.text())
}

async function main() {
  const argv = process.argv.slice(2)
  const getFlag = (n) => { const i = argv.indexOf(`--${n}`); return i >= 0 ? argv[i + 1] : null }
  const fileId = getFlag('file-id')
  const img    = getFlag('img')
  const tape   = parseFloat(getFlag('tape'))
  const repeatN = Math.max(1, parseInt(getFlag('repeat') || String(DEFAULT_N), 10))

  if (!fileId || !img || !tape) {
    console.error('Usage: node scripts/dryrun-video.js --file-id <fid> --img <IMG_xxxx> --tape <cm> [--repeat 5]')
    process.exit(1)
  }

  if (!API_KEY) { console.error('GEMINI_API_KEY not set'); process.exit(1) }

  fs.mkdirSync(DRYRUN_VIDS, { recursive: true })
  const localPath = path.join(DRYRUN_VIDS, `${img}.mov`)
  if (fs.existsSync(localPath) && fs.statSync(localPath).size > 1024 * 1024) {
    console.log(`[video] cache hit: ${localPath}`)
  } else {
    console.log(`[video] downloading from Drive ${fileId}...`)
    downloadFromDrive(fileId, localPath)
  }

  const fileManager = new GoogleAIFileManager(API_KEY)
  const genAI = new GoogleGenerativeAI(API_KEY)
  const file = await uploadAndWait(fileManager, localPath, img)

  console.log(`\n[gemini] N=${repeatN} parallel calls...`)
  const t0 = Date.now()
  const settled = await Promise.allSettled(
    Array.from({ length: repeatN }, (_, i) => callGemini(genAI, file, i))
  )
  console.log(`[gemini] done in ${Math.round((Date.now()-t0)/1000)}s`)

  const results = settled.map((s, i) => {
    if (s.status === 'fulfilled') return s.value
    console.log(`  run ${i+1}: ERROR ${s.reason?.message?.slice(0, 100)}`)
    return null
  })
  results.forEach((r, i) => {
    if (r) console.log(`  run ${i+1}: ratio=${r.trunkToCardRatio}  card=${r.cardPixelWidth}px  trunk=${r.trunkPixelWidth}px  t=${r.videoTimestampSec}s  conf=${r.confidence}`)
  })

  const ratios = results.map(r => r?.trunkToCardRatio ?? null)
  const medRatio = median(ratios)
  const cv = coeffVar(ratios)
  const dbh = medRatio != null ? Math.round(medRatio * CREDITCARD_WIDTH_CM * 10) / 10 : null
  const err = dbh ? Math.abs(dbh - tape) / tape * 100 : null

  console.log(`\n=== ${img} (${PIPELINE_VER}) ===`)
  console.log(`tape:           ${tape} cm`)
  console.log(`ratios:         [${ratios.join(', ')}]`)
  console.log(`median ratio:   ${medRatio?.toFixed(3)}  cv=${cv?.toFixed(1)}%`)
  console.log(`DBH (median):   ${dbh} cm  err=${err?.toFixed(1)}%`)

  // 寫進 dryrun_runs (用既有欄位 + pipeline_version 區分)
  const db = getDb()
  const info = db.prepare(`
    INSERT INTO dryrun_runs (
      tree_id, tree_label, pipeline_version, tmp_frames_dir,
      dbh_cm, winner_path,
      baseline_manual_tape_cm, error_vs_baseline_pct, notes,
      path0_dbh_cm,
      pathA_legacy_dbh_cm, pathA_legacy_ratio,
      pathA_legacy_runs_json, pathA_legacy_median_ratio, pathA_legacy_cv_pct,
      error_pathA_legacy_pct, pathA_winner_strategy, pathA_winner_dbh_cm, repeat_n
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    `${img}_video_${Date.now()}`, `${img}.mov`, PIPELINE_VER, null,
    dbh, dbh ? 'video' : null,
    tape, err, `video-direct uploaded ${path.basename(localPath)}; N=${repeatN}`,
    tape,
    dbh, medRatio,
    JSON.stringify(ratios), medRatio, cv,
    err, dbh ? 'video' : null, dbh, repeatN
  )
  console.log(`\nwritten dryrun #${info.lastInsertRowid}`)

  // 清理 Files API（避免 storage 持續累積）
  try {
    await fileManager.deleteFile(file.name)
    console.log(`[cleanup] deleted ${file.name}`)
  } catch (e) {
    console.log(`[cleanup] delete failed: ${e.message}`)
  }
}

main().catch(e => { console.error('FATAL:', e); process.exit(1) })
