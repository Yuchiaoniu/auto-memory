// test_one_frame.js  —  send a single frame to Gemini and report ratio
// Usage: node test_one_frame.js <frame_path>
require('dotenv').config()
const fs = require('fs')
const { GoogleGenerativeAI, SchemaType } = require('@google/generative-ai')

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

const SCHEMA = {
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

async function main() {
  const fp = process.argv[2]
  if (!fp) { console.error('usage: node test_one_frame.js <path>'); process.exit(1) }

  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
  const model = genAI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: { responseMimeType: 'application/json', responseSchema: SCHEMA },
  })
  const parts = [
    { text: RATIO_PROMPT },
    { inlineData: { mimeType: 'image/jpeg', data: fs.readFileSync(fp).toString('base64') } },
  ]
  const res = await model.generateContent(parts)
  const frames = JSON.parse(res.response.text()).frames || []
  frames.forEach(f => {
    const dbh = f.trunkToCardRatio > 0
      ? (Math.round(f.trunkToCardRatio * CREDITCARD_WIDTH_MM / 10 * 10) / 10) + ' cm'
      : 'n/a'
    console.log(`ratio=${f.trunkToCardRatio}  conf=${f.confidence}  → DBH≈${dbh}`)
  })
}
main().catch(console.error)
