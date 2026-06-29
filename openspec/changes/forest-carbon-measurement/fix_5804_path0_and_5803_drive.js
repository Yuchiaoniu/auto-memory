// fix_5804_path0_and_5803_drive.js  §32.7–32.8
// 1. 更新 5804 第二棵（b8b61455）path0 = 54cm 周長 → 17.2cm
// 2. 從 Google Drive 下載 IMG_5803.mov → Gemini Files API 分析影片 → UPDATE pathA

require('dotenv').config()
const { execSync } = require('child_process')
const fs   = require('fs')
const path = require('path')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { getDb }                = require('./src/db/init')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const CREDITCARD_WIDTH_MM = 85.6
const DRIVE_FILE_ID = '1U3Mi5Gtu_BqsYV2CjAyVQB4wy6J2ZbAu'
const TMP_VIDEO = '/tmp/IMG_5803_drive.mov'

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

// ── §32.8: 5804 第二棵補 path0 ──────────────────────────────────────────────────
async function fix5804Path0(db) {
  console.log('\n====== §32.8 5804 第二棵 path0 ======')
  const tree = db.prepare("SELECT * FROM trees WHERE id LIKE 'b8b61455%'").get()
  if (!tree) { console.log('  ❌ 找不到 b8b61455'); return }

  const circumCm = 54
  const dbhCm = Math.round(circumCm / Math.PI * 10) / 10   // 17.2
  const calc   = buildPathResult(dbhCm, tree.species)

  db.prepare(`
    UPDATE trees
    SET path0_dbh_cm=?, path0_volume_m3=?, path0_carbon_kg=?,
        manual_tape_circ_cm=?,
        winner_path='path0', dbh_cm=?, volume_m3=?, carbon_kg=?
    WHERE id=?
  `).run(
    calc.dbhCm, calc.volumeM3, calc.carbonKg,
    circumCm,
    calc.dbhCm, calc.volumeM3, calc.carbonKg,
    tree.id,
  )
  console.log(`  💾 b8b61455 path0=${calc.dbhCm}cm (周長 ${circumCm}cm) V=${calc.volumeM3}m³ C=${calc.carbonKg}kg`)
  console.log(`  pA=${tree.pathA_dbh_cm}cm（差距 ${((tree.pathA_dbh_cm - calc.dbhCm) / calc.dbhCm * 100).toFixed(0)}%，winner 改 path0）`)
}

// ── §32.7: 5803 Drive 影片分析 ──────────────────────────────────────────────────
async function fix5803Drive(db) {
  console.log('\n====== §32.7 5803 Drive 影片分析 ======')
  const tree = db.prepare("SELECT * FROM trees WHERE video_original_name LIKE '%5803%'").get()
  if (!tree) { console.log('  ❌ 找不到 5803'); return }
  console.log(`  id=${tree.id.slice(0,8)} p0=${tree.path0_dbh_cm} pA=${tree.pathA_dbh_cm}`)

  // Step 1: 下載影片
  if (fs.existsSync(TMP_VIDEO)) {
    const sizeMB = (fs.statSync(TMP_VIDEO).size / 1024 / 1024).toFixed(1)
    console.log(`  已有暫存影片 ${TMP_VIDEO} (${sizeMB} MB)，跳過下載`)
  } else {
    console.log(`  下載中…（可能需要數分鐘）`)
    try {
      execSync(
        `curl -L --max-redirs 10 --cookie-jar /tmp/gcookie.txt ` +
        `"https://drive.usercontent.google.com/download?id=${DRIVE_FILE_ID}&export=download&authuser=0&confirm=t" ` +
        `-o "${TMP_VIDEO}"`,
        { stdio: 'pipe', timeout: 300000 }
      )
    } catch (e) {
      console.log(`  ❌ 下載失敗：${e.message}`)
      return
    }
  }

  const sizeMB = (fs.statSync(TMP_VIDEO).size / 1024 / 1024).toFixed(1)
  console.log(`  影片大小 ${sizeMB} MB`)
  if (parseFloat(sizeMB) < 0.1) {
    console.log(`  ❌ 影片太小，下載可能失敗（Drive 可能需要登入）`)
    fs.unlinkSync(TMP_VIDEO)
    return
  }

  // Step 2: 上傳到 Gemini Files API
  console.log(`  上傳到 Gemini Files API…`)
  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)

  let uploadedFile
  try {
    const uploadResult = await genAI.fileManager.uploadFile(TMP_VIDEO, {
      mimeType: 'video/quicktime',
      displayName: 'IMG_5803.mov',
    })
    uploadedFile = uploadResult.file
    console.log(`  已上傳：${uploadedFile.name}，等待處理…`)
  } catch (e) {
    console.log(`  ❌ 上傳失敗：${e.message}`)
    return
  }

  // 等待 Gemini 處理完成
  let file = uploadedFile
  let attempts = 0
  while (file.state === 'PROCESSING' && attempts < 30) {
    await new Promise(r => setTimeout(r, 5000))
    file = await genAI.fileManager.getFile(file.name)
    process.stdout.write(`.`)
    attempts++
  }
  console.log()

  if (file.state !== 'ACTIVE') {
    console.log(`  ❌ Gemini 處理失敗，狀態：${file.state}`)
    return
  }
  console.log(`  ✅ Gemini 影片就緒`)

  // Step 3: 讓 Gemini 分析影片找第 10 秒的信用卡
  const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' })
  const videoPrompt = `這是一段樹木量測的影片。在影片約第 10 秒處，有人手持信用卡（標準尺寸 85.6mm × 54mm）靠著樹幹。

請分析此時刻，回傳 JSON（不含 markdown）：
{
  "creditCardVisible": true/false,
  "trunkToCardRatio": 胸高樹幹寬 / 信用卡長邊（85.6mm）的倍數，未偵測到填 0,
  "cardWidthFraction": 信用卡長邊佔畫面寬的比例 0.0-1.0,
  "trunkWidthFraction": 樹幹寬佔畫面寬的比例 0.0-1.0,
  "confidence": 偵測信心度 0.0-1.0,
  "timestampSec": 你偵測到信用卡的最佳時間點（秒）
}

注意：只找信用卡（塑膠卡片長寬比約 1.6:1），不要把卷尺或皮尺當參照物。`

  let parsed
  try {
    const result = await model.generateContent([
      { fileData: { mimeType: 'video/quicktime', fileUri: file.uri } },
      { text: videoPrompt },
    ])
    const text = result.response.text().trim()
    const jsonText = text.replace(/^```json\s*/i, '').replace(/\s*```$/, '')
    parsed = JSON.parse(jsonText)
    console.log(`  Gemini 回應：`, JSON.stringify(parsed))
  } catch (e) {
    console.log(`  ❌ Gemini 分析失敗：${e.message}`)
    // 清理
    await genAI.fileManager.deleteFile(file.name).catch(() => {})
    return
  }

  // 計算 DBH
  const iw = tree.image_width || 1920
  let ratio = parsed.trunkToCardRatio || 0
  if (!(ratio > 0) && (parsed.trunkWidthFraction || 0) > 0 && (parsed.cardWidthFraction || 0) > 0) {
    ratio = parsed.trunkWidthFraction / parsed.cardWidthFraction
  }
  const dbhRaw = ratio > 0 ? ratio * CREDITCARD_WIDTH_MM / 10 : null
  const dbhCm  = dbhRaw != null && dbhRaw >= 1 && dbhRaw <= 200
    ? Math.round(dbhRaw * 10) / 10
    : null

  if (!dbhCm || !parsed.creditCardVisible) {
    console.log(`  ❌ 無法取得有效 DBH（ratio=${ratio} dbhRaw=${dbhRaw?.toFixed(1)}）`)
    await genAI.fileManager.deleteFile(file.name).catch(() => {})
    return
  }

  const calc = buildPathResult(dbhCm, tree.species)
  db.prepare('UPDATE trees SET pathA_dbh_cm=?, pathA_volume_m3=?, pathA_carbon_kg=? WHERE id=?')
    .run(calc.dbhCm, calc.volumeM3, calc.carbonKg, tree.id)
  console.log(`  💾 UPDATE pathA=${calc.dbhCm}cm (p0=${tree.path0_dbh_cm}, 差${((calc.dbhCm-tree.path0_dbh_cm)/tree.path0_dbh_cm*100).toFixed(0)}%)`)
  console.log(`  V=${calc.volumeM3}m³ C=${calc.carbonKg}kg`)

  // 清理 Gemini Files
  await genAI.fileManager.deleteFile(file.name).catch(() => {})
  console.log(`  Gemini 檔案已清除`)
}

async function main() {
  const db = getDb()
  await fix5804Path0(db)
  await fix5803Drive(db)

  // 最終統計
  const total    = db.prepare('SELECT COUNT(*) as n FROM trees').get().n
  const hasPathA = db.prepare('SELECT COUNT(*) as n FROM trees WHERE pathA_dbh_cm IS NOT NULL').get().n
  const hasPath0 = db.prepare('SELECT COUNT(*) as n FROM trees WHERE path0_dbh_cm IS NOT NULL').get().n
  console.log(`\n== 完成 == path0 ${hasPath0}/${total}  pathA ${hasPathA}/${total}`)
}

main().catch(console.error)
