// recover_pathA_opencv.js  §35
// 兩階段 Path A 復原：
//   第一階段：OpenCV detect_card.py 篩出含正交卡片的幀（本機 CPU，免 API）
//   第二階段：Gemini 只負責量 trunk-to-card ratio（不再做卡片偵測）
// 目標：pathA MAPE > 15% 的樣本
// 內建回歸保護：newErr > oldErr 時自動跳過（不覆蓋）

require('dotenv').config()
const fs    = require('fs')
const path  = require('path')
const { spawnSync } = require('child_process')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { getDb } = require('./src/db/init')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const CREDITCARD_WIDTH_MM = 85.6
const TMP_FRAMES_ROOT = path.join(process.cwd(), 'tmp_frames')
const DETECT_PY = path.join(process.cwd(), 'scripts', 'detect_card.py')

// Simplified schema: OpenCV handles detection, Gemini only measures ratio
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

const RATIO_PROMPT = `你是林業測量 AI。這些圖片已由 OpenCV 確認含有正交信用卡（長邊 85.6mm）靠著樹幹。

請對每張圖片回傳：
1. trunkToCardRatio：胸高（約 1.3m）樹幹寬 ÷ 信用卡長邊的倍數（無法判斷填 0）
2. confidence：信心度 0.0–1.0

不需要重新驗證卡片是否存在或正交，OpenCV 已確認。專注在估算比例。`

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

function runOpencv(framePaths, rotateCW) {
  const args = rotateCW ? ['--rotate-cw', ...framePaths] : framePaths
  const r = spawnSync('python3', [DETECT_PY, ...args], { encoding: 'utf8', timeout: 90000 })
  if (r.status !== 0 || !r.stdout.trim()) {
    const msg = (r.stderr || '').slice(0, 300)
    if (msg.includes('opencv not installed') || msg.includes('cv2')) {
      throw new Error('OpenCV not installed — run: pip3 install opencv-python-headless')
    }
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

async function recoverTree(tree) {
  const framesDir = path.join(TMP_FRAMES_ROOT, tree.tmp_frames_dir)
  if (!fs.existsSync(framesDir)) {
    console.log(`  tmp_frames missing: ${tree.tmp_frames_dir}`)
    return null
  }

  const framePaths = []
  for (let i = 0; i <= 12; i++) {
    const fp = path.join(framesDir, `frame_${i}.jpg`)
    if (fs.existsSync(fp)) framePaths.push(fp)
  }
  if (!framePaths.length) { console.log(`  no frames`); return null }
  console.log(`  ${framePaths.length} frames`)

  const rotateCW = tree.id.startsWith('db0c5e0f')
  if (rotateCW) console.log(`  rotate 90 CW`)

  let cvResults
  try {
    cvResults = runOpencv(framePaths, rotateCW)
  } catch (e) {
    console.log(`  ${e.message}`)
    return null
  }

  const withCard = cvResults.filter(r => r.cardDetected)
  const orthogonal = withCard.filter(r => r.isOrthogonal).sort((a, b) => b.sharpness - a.sharpness)
  const relaxed    = withCard.filter(r => !r.isOrthogonal).sort((a, b) => b.sharpness - a.sharpness)

  console.log(`  OpenCV: ${withCard.length} card frames (${orthogonal.length} orthogonal, ${relaxed.length} relaxed)`)

  const selected = orthogonal.length > 0 ? orthogonal.slice(0, 3) : relaxed.slice(0, 3)
  if (!selected.length) { console.log(`  no card frames`); return null }

  const mode = orthogonal.length > 0 ? 'orthogonal' : 'relaxed'
  console.log(`  sending ${selected.length} frames to Gemini (${mode} mode)`)

  let geminiFrames
  try {
    geminiFrames = await measureRatio(selected.map(r => r.path))
  } catch (e) {
    console.log(`  Gemini error: ${e.message}`)
    return null
  }

  const dbhValues = geminiFrames
    .filter(f => f.trunkToCardRatio > 0 && f.confidence >= 0.4)
    .map(f => {
      const d = Math.round(f.trunkToCardRatio * CREDITCARD_WIDTH_MM / 10 * 10) / 10
      return d >= 1 && d <= 200 ? d : null
    })
    .filter(d => d !== null)

  if (!dbhValues.length) { console.log(`  Gemini: no valid ratios`); return null }

  const dbhCm = median(dbhValues)
  console.log(`  Gemini median DBH=${dbhCm}cm from ${dbhValues.length} frames [${dbhValues.join(', ')}]`)
  return { dbhCm, mode }
}

async function main() {
  const db = getDb()

  const trees = db.prepare(`
    SELECT id, species, video_original_name, path0_dbh_cm, pathA_dbh_cm, tmp_frames_dir,
           ABS(pathA_dbh_cm - path0_dbh_cm) / path0_dbh_cm * 100 AS err_pct
    FROM trees
    WHERE tmp_frames_dir IS NOT NULL
      AND path0_dbh_cm IS NOT NULL
      AND pathA_dbh_cm IS NOT NULL
      AND ABS(pathA_dbh_cm - path0_dbh_cm) / path0_dbh_cm > 0.15
    ORDER BY err_pct DESC
  `).all()

  console.log(`target trees (MAPE > 15%): ${trees.length}\n`)

  if (!trees.length) { console.log('nothing to do'); return }

  let improved = 0, regressed = 0, failed = 0

  for (const tree of trees) {
    console.log(`\n--- ${tree.id.slice(0, 8)} ${tree.video_original_name} (err=${tree.err_pct.toFixed(1)}%, p0=${tree.path0_dbh_cm}, pA=${tree.pathA_dbh_cm})`)

    let result
    try {
      result = await recoverTree(tree)
    } catch (e) {
      console.log(`  uncaught: ${e.message}`)
      failed++
      continue
    }

    if (!result) { failed++; continue }

    const pr = buildPathResult(result.dbhCm, tree.species)
    const newErr = Math.abs(pr.dbhCm - tree.path0_dbh_cm) / tree.path0_dbh_cm * 100

    if (newErr > tree.err_pct) {
      console.log(`  REGRESSION ${tree.pathA_dbh_cm}->${pr.dbhCm}cm  ${tree.err_pct.toFixed(1)}%->${newErr.toFixed(1)}%  SKIP`)
      regressed++
      continue
    }

    db.prepare(
      'UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?'
    ).run(pr.dbhCm, pr.volumeM3, pr.carbonKg, tree.id)

    console.log(`  UPDATED: ${tree.pathA_dbh_cm}->${pr.dbhCm}cm  err: ${tree.err_pct.toFixed(1)}%->${newErr.toFixed(1)}%  [${result.mode}]`)
    improved++
  }

  console.log(`\n== done ==  improved=${improved}  regressed=${regressed}  failed=${failed}  total=${trees.length}`)

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
