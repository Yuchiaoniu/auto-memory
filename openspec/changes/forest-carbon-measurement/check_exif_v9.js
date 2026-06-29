// check_exif_v9.js — 查 raw_result 裡的 metadata 欄位，找 v9 / 距離 / 對焦相關資訊
const db = require('./src/db/init').getDb()

// 取一棵有完整 raw_result 的樹
const rows = db.prepare(
  'SELECT id, video_original_name, raw_result FROM trees WHERE raw_result IS NOT NULL ORDER BY created_at LIMIT 3'
).all()

rows.forEach(r => {
  let rr = {}
  try { rr = JSON.parse(r.raw_result) } catch(_) {}

  console.log(`\n=== ${r.video_original_name} (${r.id.slice(0,8)}) ===`)

  const meta = rr.metadata || {}
  console.log('metadata keys:', Object.keys(meta).join(', '))

  // 找所有包含 v9 / distance / focus / depth / motor / lens / subject 的 key
  const interesting = Object.entries(meta).filter(([k,v]) =>
    /v9|distance|focus|depth|motor|lens|subject|focal|sensor|aperture|zoom|dof/i.test(k)
  )
  if (interesting.length) {
    console.log('距離/對焦相關欄位:')
    interesting.forEach(([k,v]) => console.log(`  ${k}: ${v}`))
  } else {
    console.log('無距離/對焦欄位')
  }

  // 全部 metadata 列出（找 v9）
  const v9Keys = Object.entries(meta).filter(([k]) => /v9/i.test(k))
  if (v9Keys.length) {
    console.log('v9 相關:', v9Keys)
  }

  // 印出所有 metadata（避免遺漏）
  console.log('全部 metadata:')
  Object.entries(meta).forEach(([k,v]) => {
    if (v !== null && v !== undefined) console.log(`  ${k}: ${JSON.stringify(v).slice(0,80)}`)
  })
})
