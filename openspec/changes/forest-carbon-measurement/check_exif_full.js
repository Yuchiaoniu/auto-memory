// check_exif_full.js — 印出 exifRaw 全部欄位，找 v9 / 距離 / 對焦
const db = require('./src/db/init').getDb()

const row = db.prepare(
  'SELECT video_original_name, raw_result FROM trees WHERE raw_result IS NOT NULL ORDER BY created_at LIMIT 1'
).get()

let rr = {}
try { rr = JSON.parse(row.raw_result) } catch(_) {}
const exifRaw = rr.metadata?.exifRaw || {}

console.log(`=== ${row.video_original_name} exifRaw 全欄位 ===\n`)

// 全部 key-value
const entries = Object.entries(exifRaw)
console.log(`總欄位數：${entries.length}\n`)

// 找 v9 / distance / focus / depth / subject / lens / motor / dof
const keywords = /v9|distance|focus|depth|subject|lens|motor|dof|range|apertur|blur|defocus/i
const interesting = entries.filter(([k]) => keywords.test(k))
if (interesting.length) {
  console.log('=== 距離/對焦相關 ===')
  interesting.forEach(([k, v]) => console.log(`  ${k}: ${JSON.stringify(v)}`))
  console.log()
}

// 印所有 key（找 v9）
console.log('=== 所有欄位名稱 ===')
entries.forEach(([k]) => process.stdout.write(k + '  '))
console.log('\n')

// 特別找 v9
const v9 = entries.filter(([k]) => /v9/i.test(k))
if (v9.length) {
  console.log('=== v9 相關 ===')
  v9.forEach(([k,v]) => console.log(`  ${k}: ${JSON.stringify(v)}`))
}
