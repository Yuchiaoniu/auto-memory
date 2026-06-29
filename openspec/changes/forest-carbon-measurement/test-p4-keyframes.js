// 測試：P4（整支影片給 Gemini）能否回傳 5 個 MM:SS 關鍵幀 + 特徵
// Usage: node test-p4-keyframes.js --file-id <fid> --img <IMG_xxxx> [--repeat 3]
require('dotenv').config()
const fs = require('fs')
const path = require('path')
const { spawnSync } = require('child_process')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')
const { GoogleAIFileManager, FileState } = require('@google/generative-ai/server')

const GDOWN_BIN = '/home/yuchi/.local/bin/gdown'
const DRYRUN_VIDS = '/tmp/dryrun_videos'
const API_KEY = process.env.GEMINI_API_KEY

const PROMPT = `這是一支樹幹測量影片。畫面中有一張信用卡（國際標準長邊 85.6mm）靠在樹幹上 — 這就是胸高 1.3 公尺的測量位置。

請分析這段影片中的樹木樹徑。請看完整支影片，找出卡片最清晰、最正對鏡頭的時刻，量信用卡長邊像素寬（cardPixelWidth）與「卡片同高度」樹幹左右邊緣像素寬（trunkPixelWidth），計算 trunkToCardRatio = trunkPixelWidth / cardPixelWidth，並給 confidence 0.0–1.0。

除了給出最終的測量數字之外，請精確列出你用來計算樹徑的 5 個關鍵幀時間點（格式為 MM:SS），並說明你在該時間點看到了什麼特徵（例如：樹幹無遮蔽處、特定海拔高度氣壓計畫面）。放在 keyframes 陣列，每項含 timestamp（MM:SS 字串）與 feature（中文描述）。`

const SCHEMA = {
  type: SchemaType.OBJECT,
  properties: {
    cardPixelWidth: { type: SchemaType.NUMBER },
    trunkPixelWidth: { type: SchemaType.NUMBER },
    trunkToCardRatio: { type: SchemaType.NUMBER },
    confidence: { type: SchemaType.NUMBER },
    keyframes: {
      type: SchemaType.ARRAY,
      items: {
        type: SchemaType.OBJECT,
        properties: {
          timestamp: { type: SchemaType.STRING },
          feature: { type: SchemaType.STRING },
        },
        required: ['timestamp', 'feature'],
      },
    },
  },
  required: ['cardPixelWidth', 'trunkPixelWidth', 'trunkToCardRatio', 'confidence', 'keyframes'],
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }
function downloadFromDrive(fileId, destPath) {
  const r = spawnSync(GDOWN_BIN, [fileId, '-O', destPath, '-q'], { encoding: 'utf8', timeout: 600000 })
  if (r.status !== 0 || !fs.existsSync(destPath) || fs.statSync(destPath).size < 1024)
    throw new Error(`gdown failed: ${(r.stderr || '').slice(0, 300)}`)
}
async function uploadAndWait(fm, localPath, name) {
  const t0 = Date.now()
  let { file } = await fm.uploadFile(localPath, { mimeType: 'video/quicktime', displayName: name })
  while (file.state === FileState.PROCESSING) { await sleep(3000); file = await fm.getFile(file.name) }
  if (file.state !== FileState.ACTIVE) throw new Error(`upload state=${file.state}`)
  console.log(`[upload] ACTIVE ${Math.round((Date.now()-t0)/1000)}s`)
  return file
}
const MMSS = /^\d{1,2}:\d{2}$/
function validKf(kf) {
  return Array.isArray(kf) && kf.length > 0 && kf.every(k => k && MMSS.test(String(k.timestamp || '')) && String(k.feature || '').length > 0)
}

async function main() {
  const argv = process.argv.slice(2)
  const get = n => { const i = argv.indexOf(`--${n}`); return i >= 0 ? argv[i+1] : null }
  const fileId = get('file-id'), img = get('img'), repeat = parseInt(get('repeat') || '3', 10)
  if (!fileId || !img) { console.error('need --file-id --img'); process.exit(1) }
  if (!API_KEY) { console.error('GEMINI_API_KEY missing'); process.exit(1) }

  fs.mkdirSync(DRYRUN_VIDS, { recursive: true })
  const localPath = path.join(DRYRUN_VIDS, `${img}.mov`)
  if (fs.existsSync(localPath) && fs.statSync(localPath).size > 1024*1024) console.log(`[video] cache hit`)
  else { console.log(`[video] downloading ${fileId}...`); downloadFromDrive(fileId, localPath) }

  const fm = new GoogleAIFileManager(API_KEY)
  const genAI = new GoogleGenerativeAI(API_KEY)
  const file = await uploadAndWait(fm, localPath, img)
  const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash', generationConfig: { responseMimeType: 'application/json', responseSchema: SCHEMA } })

  console.log(`\n[gemini] ${img} N=${repeat}...\n`)
  let okCount = 0
  for (let i = 0; i < repeat; i++) {
    try {
      const res = await model.generateContent([{ fileData: { mimeType: file.mimeType, fileUri: file.uri } }, { text: PROMPT }])
      const j = JSON.parse(res.response.text())
      const ok = validKf(j.keyframes)
      if (ok) okCount++
      console.log(`--- run ${i+1} --- ratio=${j.trunkToCardRatio} conf=${j.confidence} keyframes_valid=${ok} (${j.keyframes?.length || 0} 個)`)
      ;(j.keyframes || []).forEach((k, n) => console.log(`    ${n+1}. ${k.timestamp}  ${k.feature}`))
    } catch (e) {
      console.log(`--- run ${i+1} --- ERROR ${e.message?.slice(0,150)}`)
    }
  }
  console.log(`\n=== ${img}: ${okCount}/${repeat} 次回傳合格 MM:SS 關鍵幀 ===`)
  try { await fm.deleteFile(file.name) } catch {}
}
main().catch(e => { console.error('FATAL:', e); process.exit(1) })
