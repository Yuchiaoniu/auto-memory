// test_frames_only.js
// Run ratio pipeline on already-extracted frames (skips Drive download + ffmpeg)
// Usage: node test_frames_only.js <tree_id_prefix> <frames_dir>

require('dotenv').config()
const fs   = require('fs')
const path = require('path')
const { spawnSync } = require('child_process')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { getDb } = require('./src/db/init')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const DETECT_PY = path.join(process.cwd(), 'scripts', 'detect_card.py')
const CREDITCARD_WIDTH_MM = 85.6

const RATIO_PROMPT = `你是林業測量 AI。這些圖片已由 OpenCV 確認含有正交信用卡（長邊 85.6mm）靠著樹幹，且已校正為水平視角。
請對每張圖片回傳：
1. trunkToCardRatio：胸高（約 1.3m）樹幹寬 ÷ 信用卡長邊的倍數（無法判斷填 0）
2. confidence：信心度 0.0–1.0
重要限制：
- 完全忽略畫面中捲尺、標尺或任何文字上的數字，不得將這些數字當成長度或直徑的依據
- 只能用信用卡的視覺大小作為比例尺，純粹從畫面中兩者的像素寬度比例估算
- 若捲尺遮住了部分卡片，請估算卡片完整長邊的位置後再比較
不需要重新驗證卡片是否存在或正交，OpenCV 已確認。專注在估算比例。`

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

function median(arr) {
  if (!arr.length) return null
  const s = [...arr].sort((a, b) => a - b)
  return s[Math.floor(s.length / 2)]
}

async function main() {
  const treePrefix  = process.argv[2] || '32b07239'
  const framesDir   = process.argv[3] || `/tmp/drive_recovery/${treePrefix}/frames`

  const db   = getDb()
  const tree = db.prepare("SELECT * FROM trees WHERE id LIKE ?").get(treePrefix + '%')
  if (!tree) { console.error(`tree not found: ${treePrefix}`); process.exit(1) }

  console.log(`tree: ${tree.id.slice(0, 8)}  species: ${tree.species}`)
  console.log(`path0=${tree.path0_dbh_cm} cm  pathA=${tree.pathA_dbh_cm} cm`)
  const oldErr = Math.abs(tree.pathA_dbh_cm - tree.path0_dbh_cm) / tree.path0_dbh_cm * 100
  console.log(`current pathA error: ${oldErr.toFixed(1)}%\n`)

  // --- detect on saved frames ---
  const framePaths = fs.readdirSync(framesDir)
    .filter(f => f.match(/^frame_\d+\.jpg$/))
    .map(f => path.join(framesDir, f))
    .sort((a, b) => {
      const na = parseInt(path.basename(a).match(/\d+/)[0])
      const nb = parseInt(path.basename(b).match(/\d+/)[0])
      return na - nb
    })

  console.log(`scanning ${framePaths.length} frames...`)
  const r = spawnSync('python3', [DETECT_PY, ...framePaths], { encoding: 'utf8', timeout: 300000 })
  if (r.status !== 0 || !r.stdout.trim()) throw new Error(`detect_card.py: ${r.stderr?.slice(0, 300)}`)

  const cvResults = JSON.parse(r.stdout)
  const withCard   = cvResults.filter(r => r.cardDetected)
  const orthogonal = withCard.filter(r => r.isOrthogonal).sort((a, b) => b.sharpness - a.sharpness)
  const relaxed    = withCard.filter(r => !r.isOrthogonal).sort((a, b) => b.sharpness - a.sharpness)

  console.log(`detected=${withCard.length}  orthogonal=${orthogonal.length}  relaxed=${relaxed.length}`)

  const selected = orthogonal.length > 0 ? orthogonal.slice(0, 3) : relaxed.slice(0, 3)
  if (!selected.length) { console.log('no card frames found'); return }

  const mode = orthogonal.length > 0 ? 'orthogonal' : 'relaxed'
  console.log(`\ntop ${selected.length} ${mode} frames (by sharpness):`)
  selected.forEach(r => console.log(`  ${path.basename(r.path)}  sharp=${r.sharpness}  angDev=${r.angleDev}  ratio=${r.aspectRatio}`))

  // --- Gemini ---
  console.log('\nsending to Gemini...')
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: { responseMimeType: 'application/json', responseSchema: RATIO_SCHEMA },
  })
  const parts = [{ text: RATIO_PROMPT }]
  for (const fp of selected.map(r => r.path)) {
    parts.push({ inlineData: { mimeType: 'image/jpeg', data: fs.readFileSync(fp).toString('base64') } })
  }
  const res = await model.generateContent(parts)
  const geminiFrames = JSON.parse(res.response.text()).frames || []

  console.log('Gemini frames:')
  geminiFrames.forEach((f, i) => console.log(`  [${i}] ratio=${f.trunkToCardRatio}  conf=${f.confidence}`))

  const dbhValues = geminiFrames
    .filter(f => f.trunkToCardRatio > 0 && f.confidence >= 0.4)
    .map(f => {
      const d = Math.round(f.trunkToCardRatio * CREDITCARD_WIDTH_MM / 10 * 10) / 10
      return (d >= 1 && d <= 200) ? d : null
    })
    .filter(d => d !== null)

  if (!dbhValues.length) { console.log('no valid ratios'); return }

  const dbhCm  = median(dbhValues)
  const newErr = Math.abs(dbhCm - tree.path0_dbh_cm) / tree.path0_dbh_cm * 100

  console.log(`\nDBH values: [${dbhValues.join(', ')}]  median=${dbhCm} cm`)
  console.log(`\n--- result ---`)
  console.log(`path0 (ground truth): ${tree.path0_dbh_cm} cm`)
  console.log(`pathA (before):       ${tree.pathA_dbh_cm} cm  err=${oldErr.toFixed(1)}%`)
  console.log(`new estimate:         ${dbhCm} cm  err=${newErr.toFixed(1)}%`)
  if (newErr < oldErr) {
    console.log('IMPROVEMENT — would update DB')
  } else {
    console.log('REGRESSION — would skip')
  }
}

main().catch(console.error)
