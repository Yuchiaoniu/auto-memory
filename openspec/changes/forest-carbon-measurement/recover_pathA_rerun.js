// recover_pathA_rerun.js  §32
// 對 pathA_dbh_cm IS NULL 的樹重跑 Gemini（全 13 幀，credit-card-only prompt）
// IMG_5786（id: db0c5e0f）幀先 FFmpeg 旋轉 90° CW

require('dotenv').config()
const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { getDb } = require('./src/db/init')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const CREDITCARD_WIDTH_MM = 85.6
const TMP_FRAMES_ROOT = path.join(process.cwd(), 'tmp_frames')

// Gemini 只找信用卡的簡化 schema
const CARD_SCHEMA = {
  type: SchemaType.OBJECT,
  properties: {
    frames: {
      type: SchemaType.ARRAY,
      items: {
        type: SchemaType.OBJECT,
        properties: {
          trunkDetected:          { type: SchemaType.BOOLEAN },
          trunkWidthFraction:     { type: SchemaType.NUMBER },
          creditCardDetected:     { type: SchemaType.BOOLEAN },
          creditCardAtTrunk:      { type: SchemaType.BOOLEAN },
          trunkToCardRatio:       { type: SchemaType.NUMBER },
          cardWidthFraction:      { type: SchemaType.NUMBER },
          detectionConfidence:    { type: SchemaType.NUMBER },
        },
        required: [
          'trunkDetected', 'trunkWidthFraction',
          'creditCardDetected', 'creditCardAtTrunk',
          'trunkToCardRatio', 'cardWidthFraction', 'detectionConfidence',
        ],
      },
    },
  },
  required: ['frames'],
}

const CARD_PROMPT = `你是林業測量 AI。圖片為手機拍攝的樹木關鍵幀。

目標：找出畫面中的**信用卡／金融卡**（標準尺寸 85.6mm × 54mm），以其作為比例尺計算樹幹胸高直徑。

對每張圖片回傳：

1. trunkDetected：是否能看到樹幹
2. trunkWidthFraction：胸高（約 1.3m 高）樹幹寬佔畫面寬比例（0.0–1.0）
3. creditCardDetected：畫面中是否有信用卡或金融卡（塑膠卡片，長寬比約 1.6:1）
   - 注意：**不要把卷尺、皮尺、直尺當成參照物**，這些不是信用卡
   - 就算卡片傾斜 45° 以內仍算偵測到
4. creditCardAtTrunk：信用卡是否靠著樹幹（接觸樹幹、貼在樹幹上、或放在樹幹根部正下方）
5. trunkToCardRatio：胸高樹幹寬度是信用卡長邊（85.6mm）的幾倍。請用像素量測計算。未偵測到填 0
6. cardWidthFraction：信用卡長邊佔畫面寬比例（0.0–1.0）。未偵測到填 0
7. detectionConfidence：偵測信心度 0.0–1.0（信用卡清晰可見 0.7+；部分遮蔽 0.4–0.7；極模糊或不確定 < 0.4）

重要提醒：僅辨識信用卡，不辨識其他參照物。`

function buildPathResult(dbhCm, species) {
  const formula = getFormulaByScientificName(species)
  const heightM  = formula.hdA * Math.pow(dbhCm, formula.hdB)
  const volumeM3 = formula.volA * Math.pow(dbhCm, formula.volB) * Math.pow(heightM, formula.volC)
  const carbonKg = volumeM3 * formula.woodDensity * formula.bef * 0.5
  return {
    dbhCm:    Math.round(dbhCm * 10) / 10,
    volumeM3: Math.round(volumeM3 * 10000) / 10000,
    carbonKg: Math.round(carbonKg * 10) / 10,
  }
}

async function analyzeFramesForCard(frameBase64s, imageWidth) {
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: { responseMimeType: 'application/json', responseSchema: CARD_SCHEMA },
  })
  const parts = [{ text: CARD_PROMPT }]
  frameBase64s.forEach(b64 => parts.push({ inlineData: { mimeType: 'image/jpeg', data: b64 } }))
  const result = await model.generateContent(parts)
  const parsed = JSON.parse(result.response.text())

  // 整理每幀結果，嘗試從 pixel 計算 ratio 當備援
  const iw = imageWidth || 1920
  return (parsed.frames || []).map(f => {
    let ratio = f.trunkToCardRatio || 0
    // pixel fallback：trunkWidthFraction 和 cardWidthFraction 都有值
    if (!(ratio > 0) && (f.trunkWidthFraction || 0) > 0 && (f.cardWidthFraction || 0) > 0) {
      ratio = f.trunkWidthFraction / f.cardWidthFraction
    }
    const dbhCm = ratio > 0 ? Math.round(ratio * CREDITCARD_WIDTH_MM / 10 * 10) / 10 : null
    const valid = dbhCm != null && dbhCm >= 1 && dbhCm <= 200
    return {
      cardDetected: f.creditCardDetected,
      atTrunk:      f.creditCardAtTrunk,
      confidence:   f.detectionConfidence || 0,
      ratio,
      dbhCm: valid ? dbhCm : null,
    }
  })
}

function rotateFramesCW(framesDir, frameFiles) {
  const rotatedDir = framesDir + '_rot'
  fs.mkdirSync(rotatedDir, { recursive: true })
  const rotated = []
  for (const f of frameFiles) {
    const src = path.join(framesDir, f)
    const dst = path.join(rotatedDir, f)
    if (!fs.existsSync(dst)) {
      execSync(`ffmpeg -y -i "${src}" -vf transpose=1 "${dst}" 2>/dev/null`)
    }
    rotated.push(dst)
  }
  return { rotatedDir, paths: rotated }
}

async function recoverTree(tree) {
  const framesDir = path.join(TMP_FRAMES_ROOT, tree.tmp_frames_dir)
  if (!fs.existsSync(framesDir)) {
    console.log(`  ⚠️  tmp_frames 不存在：${tree.tmp_frames_dir}`)
    return null
  }

  // 收集所有存在的幀（frame_0.jpg ~ frame_12.jpg）
  let frameFiles = []
  for (let i = 0; i <= 12; i++) {
    const name = `frame_${i}.jpg`
    if (fs.existsSync(path.join(framesDir, name))) frameFiles.push(name)
  }
  if (frameFiles.length === 0) {
    console.log(`  ⚠️  無可用幀`)
    return null
  }
  console.log(`  ${frameFiles.length} 幀可用`)

  const needsRotation = tree.id.startsWith('db0c5e0f')
  let workingDir = framesDir
  let workingFiles = frameFiles.map(f => path.join(framesDir, f))

  if (needsRotation) {
    console.log(`  🔄 旋轉幀 90° CW`)
    const { rotatedDir, paths } = rotateFramesCW(framesDir, frameFiles)
    workingDir = rotatedDir
    workingFiles = paths
  }

  // 分批送 Gemini（每次最多 5 幀，避免 token 過大）
  const BATCH = 5
  let allFrameResults = []
  const iw = tree.image_width || 1920

  for (let i = 0; i < workingFiles.length; i += BATCH) {
    const batch = workingFiles.slice(i, i + BATCH)
    const base64s = batch.map(fp => {
      const buf = fs.readFileSync(fp)
      return buf.toString('base64')
    })
    console.log(`  Gemini batch ${Math.floor(i/BATCH)+1}（${batch.length} 幀）`)
    const results = await analyzeFramesForCard(base64s, iw)
    allFrameResults = allFrameResults.concat(results)
  }

  // 找信心最高且 DBH 合法的幀
  const valid = allFrameResults.filter(f => f.cardDetected && f.atTrunk && f.dbhCm != null)
  if (valid.length === 0) {
    // 放寬：允許 atTrunk 不確定的幀
    const relaxed = allFrameResults.filter(f => f.cardDetected && f.dbhCm != null)
    if (relaxed.length === 0) {
      console.log(`  ❌ 未偵測到有效信用卡`)
      return null
    }
    console.log(`  ⚠️  使用放寬條件（atTrunk 不確定）`)
    relaxed.sort((a, b) => b.confidence - a.confidence)
    return relaxed[0].dbhCm
  }

  valid.sort((a, b) => b.confidence - a.confidence)
  const best = valid[0]
  console.log(`  ✅ DBH=${best.dbhCm}cm (ratio=${best.ratio.toFixed(2)}, conf=${best.confidence})`)
  return best.dbhCm
}

async function main() {
  const db = getDb()
  const trees = db.prepare(
    'SELECT id, species, video_original_name, path0_dbh_cm, tmp_frames_dir, image_width, image_height FROM trees WHERE pathA_dbh_cm IS NULL ORDER BY created_at'
  ).all()

  console.log(`pathA NULL: ${trees.length} 棵\n`)
  let recovered = 0

  for (const tree of trees) {
    console.log(`\n--- ${tree.id.slice(0,8)} ${tree.video_original_name} (p0=${tree.path0_dbh_cm}cm)`)

    if (!tree.tmp_frames_dir) {
      console.log('  ⚠️  無 tmp_frames_dir')
      continue
    }

    let dbhCm = null
    try {
      dbhCm = await recoverTree(tree)
    } catch (err) {
      console.log(`  ❌ 錯誤：${err.message}`)
      continue
    }

    if (!dbhCm) continue

    const result = buildPathResult(dbhCm, tree.species)
    db.prepare(
      'UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?'
    ).run(result.dbhCm, result.volumeM3, result.carbonKg, tree.id)
    console.log(`  💾 UPDATE: pathA DBH=${result.dbhCm}cm V=${result.volumeM3}m³ C=${result.carbonKg}kg`)
    recovered++
  }

  console.log(`\n== 完成：${recovered}/${trees.length} 棵恢復 pathA ==`)

  // 最終覆蓋率統計
  const total    = db.prepare('SELECT COUNT(*) as n FROM trees').get().n
  const hasPathA = db.prepare('SELECT COUNT(*) as n FROM trees WHERE pathA_dbh_cm IS NOT NULL').get().n
  console.log(`pathA 最終覆蓋率：${hasPathA}/${total} 棵`)
}

main().catch(console.error)
