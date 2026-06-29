// recover_pathA_drive.js  §35.6
// 從 Google Drive URL 下載影片 → 2fps OpenCV 掃描卡片 → Gemini ratio-only
// 目標：pathA MAPE > 15% 且有 video_drive_url 的樣本
// 回歸保護：newErr > oldErr 時自動跳過（不覆蓋）

require('dotenv').config()
const fs    = require('fs')
const path  = require('path')
const os    = require('os')
const { spawnSync } = require('child_process')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { getDb } = require('./src/db/init')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const CREDITCARD_WIDTH_MM = 85.6
const TMP_ROOT = path.join(os.tmpdir(), 'drive_recovery')
const DETECT_PY = path.join(process.cwd(), 'scripts', 'detect_card.py')

const RATIO_SCHEMA = {
  type: SchemaType.OBJECT,
  properties: {
    frames: {
      type: SchemaType.ARRAY,
      items: {
        type: SchemaType.OBJECT,
        properties: {
          trunkToCardRatio: { type: SchemaType.NUMBER },
          confidence:       { type: SchemaType.NUMBER },
        },
        required: ['trunkToCardRatio', 'confidence'],
      },
    },
  },
  required: ['frames'],
}

const RATIO_PROMPT = `你是林業測量 AI。這些圖片已由 OpenCV 確認含有正交信用卡（長邊 85.6mm）靠著樹幹，且已校正為水平視角。

請對每張圖片回傳：
1. trunkToCardRatio：胸高（約 1.3m）樹幹寬 ÷ 信用卡長邊的倍數（無法判斷填 0）
2. confidence：信心度 0.0–1.0

重要限制：
- 完全忽略畫面中捲尺、標尺或任何文字上的數字，不得將這些數字當成長度或直徑的依據
- 只能用信用卡的視覺大小作為比例尺，純粹從畫面中兩者的像素寬度比例估算
- 若捲尺或其他物體遮住了部分卡片，卡片長邊仍是 85.6mm，請根據可見的卡片邊緣位置推算完整長邊並使用 85.6mm 作為參考，不要只量可見部分

不需要重新驗證卡片是否存在或正交，OpenCV 已確認。專注在估算比例。`

function extractDriveId(url) {
  const m = url.match(/\/file\/d\/([^/?]+)/)
  return m ? m[1] : null
}

function downloadDriveVideo(fileId, destPath) {
  const script = `import gdown; gdown.download(id="${fileId}", output="${destPath}", quiet=False)`
  const r = spawnSync('python3', ['-c', script], { encoding: 'utf8', timeout: 600000 })
  if (r.status !== 0) {
    throw new Error(`gdown failed: ${(r.stderr || r.stdout || '').slice(0, 400)}`)
  }
  if (!fs.existsSync(destPath) || fs.statSync(destPath).size < 1000) {
    throw new Error(`download seems empty or missing: ${destPath}`)
  }
}

function runOpencvVideo(videoPath, framesDir, rotateCW) {
  const args = ['--video', videoPath, '--fps', '2', '--save-dir', framesDir]
  if (rotateCW) args.push('--rotate-cw')
  const r = spawnSync('python3', [DETECT_PY, ...args], { encoding: 'utf8', timeout: 1800000 })
  if (r.status !== 0 || !r.stdout.trim()) {
    const msg = (r.stderr || '').slice(0, 300)
    throw new Error(`detect_card.py failed: ${msg}`)
  }
  return JSON.parse(r.stdout)
}

async function measureRatio(selectedPaths) {
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: { responseMimeType: 'application/json', responseSchema: RATIO_SCHEMA },
  })
  const parts = [{ text: RATIO_PROMPT }]
  for (const fp of selectedPaths) {
    parts.push({ inlineData: { mimeType: 'image/jpeg', data: fs.readFileSync(fp).toString('base64') } })
  }
  const res = await model.generateContent(parts)
  return JSON.parse(res.response.text()).frames || []
}

function median(arr) {
  if (!arr.length) return null
  const s = [...arr].sort((a, b) => a - b)
  return s[Math.floor(s.length / 2)]
}

function buildPathResult(dbhCm, species) {
  const f = getFormulaByScientificName(species)
  const h  = f.hdA  * Math.pow(dbhCm, f.hdB)
  const v  = f.volA * Math.pow(dbhCm, f.volB) * Math.pow(h, f.volC)
  const c  = v * f.woodDensity * f.bef * 0.5
  return {
    dbhCm:    Math.round(dbhCm * 10) / 10,
    volumeM3: Math.round(v * 10000) / 10000,
    carbonKg: Math.round(c * 10) / 10,
  }
}

async function recoverTree(tree, treeDir) {
  const fileId = extractDriveId(tree.video_drive_url)
  if (!fileId) throw new Error(`cannot extract Drive ID from: ${tree.video_drive_url}`)

  const videoPath = path.join(treeDir, tree.video_original_name)
  const framesDir = path.join(treeDir, 'frames')
  fs.mkdirSync(framesDir, { recursive: true })

  console.log(`  downloading from Drive (id=${fileId})...`)
  downloadDriveVideo(fileId, videoPath)
  const sizeMB = (fs.statSync(videoPath).size / 1e6).toFixed(1)
  console.log(`  downloaded ${sizeMB} MB`)

  const rotateCW = tree.id.startsWith('db0c5e0f')
  console.log(`  scanning at 2fps${rotateCW ? ' +rotateCW' : ''}...`)
  const cvResults = runOpencvVideo(videoPath, framesDir, rotateCW)

  const withCard   = cvResults.filter(r => r.cardDetected)
  const orthogonal = withCard.filter(r => r.isOrthogonal).sort((a, b) => b.sharpness - a.sharpness)
  const relaxed    = withCard.filter(r => !r.isOrthogonal).sort((a, b) => b.sharpness - a.sharpness)
  console.log(`  OpenCV: ${cvResults.length} frames scanned, ${withCard.length} card frames (${orthogonal.length} orthogonal, ${relaxed.length} relaxed)`)

  const selected = orthogonal.length > 0 ? orthogonal.slice(0, 3) : relaxed.slice(0, 3)
  if (!selected.length) { console.log(`  no card frames found`); return null }

  const mode = orthogonal.length > 0 ? 'orthogonal' : 'relaxed'
  console.log(`  sending ${selected.length} frames to Gemini (${mode} mode)`)

  const geminiFrames = await measureRatio(selected.map(r => r.path))

  const dbhValues = geminiFrames
    .filter(f => f.trunkToCardRatio > 0 && f.confidence >= 0.4)
    .map(f => {
      const d = Math.round(f.trunkToCardRatio * CREDITCARD_WIDTH_MM / 10 * 10) / 10
      return d >= 1 && d <= 200 ? d : null
    })
    .filter(d => d !== null)

  if (!dbhValues.length) { console.log(`  Gemini: no valid ratios`); return null }

  const dbhCm = median(dbhValues)
  console.log(`  Gemini median DBH=${dbhCm}cm from [${dbhValues.join(', ')}]`)
  return { dbhCm, mode }
}

async function main() {
  const db = getDb()
  fs.mkdirSync(TMP_ROOT, { recursive: true })

  const trees = db.prepare(`
    SELECT id, species, video_original_name, video_drive_url,
           path0_dbh_cm, pathA_dbh_cm,
           ABS(pathA_dbh_cm - path0_dbh_cm) / path0_dbh_cm * 100 AS err_pct
    FROM trees
    WHERE video_drive_url IS NOT NULL
      AND path0_dbh_cm IS NOT NULL
      AND pathA_dbh_cm IS NOT NULL
      AND ABS(pathA_dbh_cm - path0_dbh_cm) / path0_dbh_cm > 0.15
      AND id NOT LIKE '32b07239%'
    ORDER BY err_pct DESC
  `).all()

  console.log(`target trees (MAPE > 15% + Drive URL): ${trees.length}\n`)
  if (!trees.length) { console.log('nothing to do'); return }

  let improved = 0, regressed = 0, failed = 0

  for (const tree of trees) {
    console.log(`\n--- ${tree.id.slice(0, 8)} ${tree.video_original_name} (err=${tree.err_pct.toFixed(1)}%, p0=${tree.path0_dbh_cm}, pA=${tree.pathA_dbh_cm})`)

    const treeDir = path.join(TMP_ROOT, tree.id.slice(0, 8))
    fs.mkdirSync(treeDir, { recursive: true })

    let result
    try {
      result = await recoverTree(tree, treeDir)
    } catch (e) {
      console.log(`  ERROR: ${e.message}`)
      failed++
      fs.rmSync(treeDir, { recursive: true, force: true })
      continue
    }

    if (!result) {
      failed++
      fs.rmSync(treeDir, { recursive: true, force: true })
      continue
    }

    const pr = buildPathResult(result.dbhCm, tree.species)
    const newErr = Math.abs(pr.dbhCm - tree.path0_dbh_cm) / tree.path0_dbh_cm * 100

    if (newErr > tree.err_pct) {
      console.log(`  REGRESSION ${tree.pathA_dbh_cm}->${pr.dbhCm}cm  ${tree.err_pct.toFixed(1)}%->${newErr.toFixed(1)}%  SKIP`)
      regressed++
      fs.rmSync(treeDir, { recursive: true, force: true })
      continue
    }

    db.prepare(
      'UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?'
    ).run(pr.dbhCm, pr.volumeM3, pr.carbonKg, tree.id)

    console.log(`  UPDATED: ${tree.pathA_dbh_cm}->${pr.dbhCm}cm  err: ${tree.err_pct.toFixed(1)}%->${newErr.toFixed(1)}%  [${result.mode}]`)
    improved++
    fs.rmSync(treeDir, { recursive: true, force: true })
  }

  console.log(`\n== done ==  improved=${improved}  regressed=${regressed}  failed=${failed}  total=${trees.length}`)

  // Final distribution
  const paired = db.prepare(`
    SELECT path0_dbh_cm, pathA_dbh_cm, video_original_name,
           ABS(pathA_dbh_cm - path0_dbh_cm) / path0_dbh_cm * 100 AS err_pct
    FROM trees WHERE path0_dbh_cm IS NOT NULL AND pathA_dbh_cm IS NOT NULL
    ORDER BY err_pct
  `).all()
  const w10 = paired.filter(r => r.err_pct <= 10).length
  const w15 = paired.filter(r => r.err_pct <= 15).length
  const w25 = paired.filter(r => r.err_pct <= 25).length
  console.log(`\n== final pathA error (${paired.length} paired) ==`)
  console.log(`  <=10%: ${w10}  <=15%: ${w15}  <=25%: ${w25}  >25%: ${paired.length - w25}`)
  paired.forEach(r => {
    const flag = r.err_pct <= 10 ? 'OK ' : r.err_pct <= 15 ? 'OK2' : r.err_pct <= 25 ? 'MED' : 'BAD'
    console.log(`  [${flag}] p0=${r.path0_dbh_cm}  pA=${r.pathA_dbh_cm}  err=${r.err_pct.toFixed(1)}%  ${r.video_original_name}`)
  })
}

main().catch(console.error)
