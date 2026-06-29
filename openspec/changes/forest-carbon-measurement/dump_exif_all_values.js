// dump_exif_all_values.js — 印出 exifRaw 所有欄位完整值，尋找鏡頭馬達位置
const db = require('./src/db/init').getDb()

const rows = db.prepare(
  'SELECT id, video_original_name, raw_result FROM trees WHERE raw_result IS NOT NULL ORDER BY created_at LIMIT 3'
).all()

rows.forEach(r => {
  let rr = {}
  try { rr = JSON.parse(r.raw_result) } catch(_) {}
  const exifRaw = rr.metadata?.exifRaw || {}
  const entries = Object.entries(exifRaw)

  console.log(`\n${'='.repeat(60)}`)
  console.log(`${r.video_original_name} (${r.id.slice(0,8)})`)
  console.log(`欄位數：${entries.length}`)
  console.log(`${'='.repeat(60)}`)

  // 印所有欄位完整值（不截斷）
  entries.forEach(([k, v]) => {
    if (v === null || v === undefined) return
    const val = typeof v === 'object' ? JSON.stringify(v) : String(v)
    console.log(`${k}: ${val}`)
  })
})
