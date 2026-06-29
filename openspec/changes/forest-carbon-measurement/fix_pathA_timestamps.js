// fix_pathA_timestamps.js  §32.4–32.6
// 使用使用者指定的精確時間戳對應的 frameIdx 重新測量 5 棵問題樹
// 原始影片已刪，改用 tmp_frames 內預切的 frame_{idx}.jpg

require('dotenv').config()
const fs   = require('fs')
const path = require('path')
const crypto = require('crypto')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { getDb }                = require('./src/db/init')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const CREDITCARD_WIDTH_MM = 85.6
const TMP_FRAMES_ROOT = path.join(process.cwd(), 'tmp_frames')

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
4. creditCardAtTrunk：信用卡是否靠著樹幹
5. trunkToCardRatio：胸高樹幹寬是信用卡長邊（85.6mm）的幾倍。請用像素量測計算。未偵測到填 0
6. cardWidthFraction：信用卡長邊佔畫面寬比例（0.0–1.0）。未偵測到填 0
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

  const iw = imageWidth || 1920
  let ratio = f.trunkToCardRatio || 0
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
}

// 分析指定 frameIdx，嘗試前後各一幀作為備援
async function analyzeWithNeighbors(tmpDir, primaryIdx, imageWidth) {
  const indices = [primaryIdx]
  if (primaryIdx > 0)  indices.push(primaryIdx - 1)
  if (primaryIdx < 12) indices.push(primaryIdx + 1)

  let bestRelaxed = null

  for (const idx of indices) {
    const fp = path.join(TMP_FRAMES_ROOT, tmpDir, `frame_${idx}.jpg`)
    if (!fs.existsSync(fp)) {
      console.log(`    frame_${idx}: 檔案不存在，跳過`)
      continue
    }
    process.stdout.write(`    frame_${idx}: `)
    const r = await analyzeFrame(fp, imageWidth)
    if (!r || !r.cardDetected || r.dbhCm == null) {
      console.log(`無卡片偵測 (card=${r?.cardDetected} dbh=${r?.dbhCm})`)
      continue
    }
    if (r.atTrunk) {
      console.log(`✅ DBH=${r.dbhCm}cm ratio=${r.ratio.toFixed(2)} conf=${r.confidence}`)
      return r.dbhCm
    }
    console.log(`⚠️  DBH=${r.dbhCm}cm (atTrunk=false conf=${r.confidence})`)
    if (!bestRelaxed || r.confidence > bestRelaxed.confidence) bestRelaxed = r
  }

  if (bestRelaxed) {
    console.log(`    → 採用放寬條件 DBH=${bestRelaxed.dbhCm}cm`)
    return bestRelaxed.dbhCm
  }
  return null
}

async function main() {
  const db = getDb()

  // 依影片名稱查樹的完整資料
  function getTree(videoPattern) {
    return db.prepare(
      'SELECT * FROM trees WHERE video_original_name LIKE ? ORDER BY created_at LIMIT 1'
    ).get(`%${videoPattern}%`)
  }

  // ── §32.4: 補 NULL ──────────────────────────────────────────────────────────
  console.log('\n====== §32.4 補 NULL pathA ======')
  for (const { pattern, frameIdx, label } of [
    { pattern: '5803', frameIdx: 2, label: '5803 (ts≈10s)' },
    { pattern: '5818', frameIdx: 9, label: '5818 (ts≈35s)' },
  ]) {
    console.log(`\n--- ${label}`)
    const tree = getTree(pattern)
    if (!tree) { console.log('  ❌ 找不到'); continue }
    console.log(`  id=${tree.id.slice(0,8)} p0=${tree.path0_dbh_cm} pA=${tree.pathA_dbh_cm}`)

    const dbhCm = await analyzeWithNeighbors(tree.tmp_frames_dir, frameIdx, tree.image_width)
    if (!dbhCm) { console.log('  ❌ 仍無法偵測'); continue }

    const calc = buildPathResult(dbhCm, tree.species)
    db.prepare('UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?')
      .run(calc.dbhCm, calc.volumeM3, calc.carbonKg, tree.id)
    console.log(`  💾 UPDATE pathA=${calc.dbhCm}cm V=${calc.volumeM3}m³ C=${calc.carbonKg}kg`)
  }

  // ── §32.5: 修正離群值 ────────────────────────────────────────────────────────
  console.log('\n====== §32.5 修正離群值 ======')
  for (const { pattern, frameIdx, label } of [
    { pattern: '5798', frameIdx: 1, label: '5798 (ts≈7s, 舊pA=75.3)' },
    { pattern: '5812', frameIdx: 2, label: '5812 (ts≈12s, 舊pA=47.1)' },
  ]) {
    console.log(`\n--- ${label}`)
    const tree = getTree(pattern)
    if (!tree) { console.log('  ❌ 找不到'); continue }
    console.log(`  id=${tree.id.slice(0,8)} p0=${tree.path0_dbh_cm} pA(舊)=${tree.pathA_dbh_cm}`)

    const dbhCm = await analyzeWithNeighbors(tree.tmp_frames_dir, frameIdx, tree.image_width)
    if (!dbhCm) { console.log('  ❌ 無偵測，保留舊值'); continue }

    const calc = buildPathResult(dbhCm, tree.species)
    db.prepare('UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?')
      .run(calc.dbhCm, calc.volumeM3, calc.carbonKg, tree.id)
    console.log(`  💾 UPDATE pathA=${calc.dbhCm}cm (舊=${tree.pathA_dbh_cm})  差異=${((calc.dbhCm - tree.pathA_dbh_cm) / tree.pathA_dbh_cm * 100).toFixed(1)}%`)
  }

  // ── §32.6: 5804 分裂 ─────────────────────────────────────────────────────────
  console.log('\n====== §32.6 5804 分裂 ======')
  const tree5804 = getTree('5804')
  if (!tree5804) {
    console.log('  ❌ 找不到 5804')
  } else {
    // 第一棵：更新原 id，用 frame_1 (15s)
    console.log(`\n--- 5804 第一棵 (frame_1, ts≈15s)`)
    console.log(`  id=${tree5804.id.slice(0,8)} p0=${tree5804.path0_dbh_cm} pA(舊)=${tree5804.pathA_dbh_cm}`)
    const dbh1 = await analyzeWithNeighbors(tree5804.tmp_frames_dir, 1, tree5804.image_width)
    if (dbh1) {
      const calc1 = buildPathResult(dbh1, tree5804.species)
      db.prepare('UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?')
        .run(calc1.dbhCm, calc1.volumeM3, calc1.carbonKg, tree5804.id)
      console.log(`  💾 UPDATE 第一棵 pathA=${calc1.dbhCm}cm`)
    } else {
      console.log('  ❌ 第一棵無偵測，保留舊值')
    }

    // 第二棵：INSERT 新記錄，用 frame_2 (37s)
    console.log(`\n--- 5804 第二棵 (frame_2, ts≈37s)`)
    const dbh2 = await analyzeWithNeighbors(tree5804.tmp_frames_dir, 2, tree5804.image_width)
    if (dbh2) {
      const calc2 = buildPathResult(dbh2, tree5804.species)
      const newId = crypto.randomUUID()
      db.prepare(`
        INSERT INTO trees (
          id, species, video_original_name, tmp_frames_dir,
          image_width, image_height, duration_sec, gps, device_model,
          frame_rate, video_codec, orientation,
          pathA_dbh_cm, pathA_volume_m3, pathA_carbon_kg,
          winner_path, dbh_cm, volume_m3, carbon_kg
        ) VALUES (
          ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pathA',?,?,?
        )
      `).run(
        newId,
        tree5804.species,
        tree5804.video_original_name,
        tree5804.tmp_frames_dir,
        tree5804.image_width,
        tree5804.image_height,
        tree5804.duration_sec,
        tree5804.gps,
        tree5804.device_model,
        tree5804.frame_rate,
        tree5804.video_codec,
        tree5804.orientation,
        calc2.dbhCm, calc2.volumeM3, calc2.carbonKg,
        calc2.dbhCm, calc2.volumeM3, calc2.carbonKg,
      )
      console.log(`  💾 INSERT 第二棵 id=${newId.slice(0,8)} pathA=${calc2.dbhCm}cm (path0 待補)`)
    } else {
      console.log('  ❌ 第二棵無偵測，未新增')
    }
  }

  // ── 最終統計 ─────────────────────────────────────────────────────────────────
  console.log('\n====== 最終統計 ======')
  const total    = db.prepare('SELECT COUNT(*) as n FROM trees').get().n
  const hasPathA = db.prepare('SELECT COUNT(*) as n FROM trees WHERE pathA_dbh_cm IS NOT NULL').get().n
  console.log(`pathA 覆蓋率：${hasPathA}/${total}`)

  // 三路徑比較表
  const all = db.prepare(`
    SELECT video_original_name, path0_dbh_cm, pathA_dbh_cm, pathB_dbh_cm, winner_path
    FROM trees ORDER BY video_original_name
  `).all()
  console.log('\n影片               p0     pA     pB    winner')
  all.forEach(r => {
    const diff = r.path0_dbh_cm && r.pathA_dbh_cm
      ? ((r.pathA_dbh_cm - r.path0_dbh_cm) / r.path0_dbh_cm * 100).toFixed(0) + '%'
      : '   -'
    console.log(
      (r.video_original_name || '').padEnd(20),
      String(r.path0_dbh_cm ?? '-').padStart(5),
      String(r.pathA_dbh_cm ?? '-').padStart(6),
      String(r.pathB_dbh_cm ?? '-').padStart(6),
      String(r.winner_path  ?? '-').padStart(7),
      diff
    )
  })
}

main().catch(console.error)
