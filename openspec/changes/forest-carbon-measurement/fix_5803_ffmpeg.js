// fix_5803_ffmpeg.js  §32.7 補救
// 影片已在 /tmp/IMG_5803_drive.mov，用 FFmpeg 提取 8/10/12 秒幀再送 Gemini 圖片分析

require('dotenv').config()
const { execSync } = require('child_process')
const fs   = require('fs')
const path = require('path')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { getDb }                = require('./src/db/init')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const CREDITCARD_WIDTH_MM = 85.6
const TMP_VIDEO = '/tmp/IMG_5803_drive.mov'

const CARD_SCHEMA = {
  type: SchemaType.OBJECT,
  properties: {
    frames: {
      type: SchemaType.ARRAY,
      items: {
        type: SchemaType.OBJECT,
        properties: {
          trunkDetected:       { type: SchemaType.BOOLEAN },
          trunkWidthFraction:  { type: SchemaType.NUMBER },
          creditCardDetected:  { type: SchemaType.BOOLEAN },
          creditCardAtTrunk:   { type: SchemaType.BOOLEAN },
          trunkToCardRatio:    { type: SchemaType.NUMBER },
          cardWidthFraction:   { type: SchemaType.NUMBER },
          detectionConfidence: { type: SchemaType.NUMBER },
        },
        required: [
          'trunkDetected','trunkWidthFraction','creditCardDetected','creditCardAtTrunk',
          'trunkToCardRatio','cardWidthFraction','detectionConfidence',
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
2. trunkWidthFraction：胸高樹幹寬佔畫面寬比例（0.0–1.0）
3. creditCardDetected：畫面中是否有信用卡（塑膠卡片長寬比約 1.6:1）
   - **不要把卷尺、皮尺、直尺當成參照物**
4. creditCardAtTrunk：信用卡是否靠著樹幹
5. trunkToCardRatio：胸高樹幹寬是信用卡長邊的幾倍。未偵測到填 0
6. cardWidthFraction：信用卡長邊佔畫面寬比例。未偵測到填 0
7. detectionConfidence：偵測信心度 0.0–1.0

重要提醒：僅辨識信用卡，不辨識其他參照物。`

function buildPathResult(dbhCm, species) {
  const formula  = getFormulaByScientificName(species)
  const heightM  = formula.hdA * Math.pow(dbhCm, formula.hdB)
  const volumeM3 = formula.volA * Math.pow(dbhCm, formula.volB) * Math.pow(heightM, formula.volC)
  const carbonKg = volumeM3 * formula.woodDensity * formula.bef * 0.5
  return {
    dbhCm:    Math.round(dbhCm * 10) / 10,
    volumeM3: Math.round(volumeM3 * 10000) / 10000,
    carbonKg: Math.round(carbonKg * 10) / 10,
  }
}

async function analyzeFrame(framePath, imageWidth) {
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: { responseMimeType: 'application/json', responseSchema: CARD_SCHEMA },
  })
  const b64 = fs.readFileSync(framePath).toString('base64')
  const result = await model.generateContent([
    { text: CARD_PROMPT },
    { inlineData: { mimeType: 'image/jpeg', data: b64 } },
  ])
  const parsed = JSON.parse(result.response.text())
  const f = (parsed.frames || [])[0]
  if (!f) return null

  let ratio = f.trunkToCardRatio || 0
  if (!(ratio > 0) && (f.trunkWidthFraction || 0) > 0 && (f.cardWidthFraction || 0) > 0) {
    ratio = f.trunkWidthFraction / f.cardWidthFraction
  }
  const dbhRaw = ratio > 0 ? ratio * CREDITCARD_WIDTH_MM / 10 : null
  const dbhCm  = dbhRaw != null && dbhRaw >= 1 && dbhRaw <= 200
    ? Math.round(dbhRaw * 10) / 10 : null

  return { cardDetected: f.creditCardDetected, atTrunk: f.creditCardAtTrunk,
           confidence: f.detectionConfidence || 0, ratio, dbhCm }
}

async function main() {
  if (!fs.existsSync(TMP_VIDEO)) {
    console.log(`❌ 找不到 ${TMP_VIDEO}，請先下載影片`)
    return
  }
  console.log(`影片：${TMP_VIDEO}`)

  const db = getDb()
  const tree = db.prepare("SELECT * FROM trees WHERE video_original_name LIKE '%5803%'").get()
  if (!tree) { console.log('❌ 找不到 5803'); return }
  console.log(`id=${tree.id.slice(0,8)} p0=${tree.path0_dbh_cm} pA=${tree.pathA_dbh_cm}`)

  // 嘗試 8s、10s、12s、15s 四個時間點
  const timestamps = [8, 10, 12, 15]
  let bestStrict = null
  let bestRelaxed = null

  for (const ts of timestamps) {
    const framePath = `/tmp/IMG_5803_${ts}s.jpg`
    process.stdout.write(`  ${ts}s → `)

    try {
      execSync(`ffmpeg -y -ss ${ts} -i "${TMP_VIDEO}" -vframes 1 "${framePath}" 2>/dev/null`)
    } catch (e) {
      console.log(`FFmpeg 失敗`)
      continue
    }
    if (!fs.existsSync(framePath)) { console.log(`幀不存在`); continue }

    const r = await analyzeFrame(framePath, tree.image_width || 1920)
    if (!r || !r.cardDetected || r.dbhCm == null) {
      console.log(`無卡片 (card=${r?.cardDetected} dbh=${r?.dbhCm})`)
      continue
    }
    if (r.atTrunk) {
      console.log(`✅ DBH=${r.dbhCm}cm ratio=${r.ratio.toFixed(2)} conf=${r.confidence}`)
      if (!bestStrict || r.confidence > bestStrict.confidence) bestStrict = r
    } else {
      console.log(`⚠️  DBH=${r.dbhCm}cm (atTrunk=false conf=${r.confidence})`)
      if (!bestRelaxed || r.confidence > bestRelaxed.confidence) bestRelaxed = r
    }
  }

  const best = bestStrict || bestRelaxed
  if (!best) {
    console.log('\n❌ 所有時間點均無偵測結果')
    return
  }

  const calc = buildPathResult(best.dbhCm, tree.species)
  db.prepare('UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?')
    .run(calc.dbhCm, calc.volumeM3, calc.carbonKg, tree.id)
  console.log(`\n💾 UPDATE pathA=${calc.dbhCm}cm (p0=${tree.path0_dbh_cm}, diff=${((calc.dbhCm-tree.path0_dbh_cm)/tree.path0_dbh_cm*100).toFixed(0)}%)`)
  console.log(`   V=${calc.volumeM3}m³  C=${calc.carbonKg}kg`)

  const total    = db.prepare('SELECT COUNT(*) as n FROM trees').get().n
  const hasPathA = db.prepare('SELECT COUNT(*) as n FROM trees WHERE pathA_dbh_cm IS NOT NULL').get().n
  console.log(`\npathA 覆蓋率：${hasPathA}/${total}`)
}

main().catch(console.error)
