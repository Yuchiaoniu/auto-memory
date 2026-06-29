// status_check_all.js — 三路徑完整狀態確認
const db = require('./src/db/init').getDb()

const all = db.prepare(`
  SELECT id, video_original_name,
         path0_dbh_cm, pathA_dbh_cm, pathB_dbh_cm,
         winner_path, dbh_cm
  FROM trees ORDER BY video_original_name, created_at
`).all()

const total    = all.length
const hasP0    = all.filter(r => r.path0_dbh_cm != null).length
const hasPA    = all.filter(r => r.pathA_dbh_cm != null).length
const hasPB    = all.filter(r => r.pathB_dbh_cm != null).length
const hasAll3  = all.filter(r => r.path0_dbh_cm != null && r.pathA_dbh_cm != null && r.pathB_dbh_cm != null).length

console.log(`總棵數：${total}`)
console.log(`path0 覆蓋：${hasP0}/${total}`)
console.log(`pathA 覆蓋：${hasPA}/${total}`)
console.log(`pathB 覆蓋：${hasPB}/${total}`)
console.log(`三路皆有：${hasAll3}/${total}`)
console.log()

// 明細表
console.log('影片                  p0     pA     pB    winner   pA-p0%  pB-p0%')
all.forEach(r => {
  const diffA = r.path0_dbh_cm && r.pathA_dbh_cm
    ? ((r.pathA_dbh_cm - r.path0_dbh_cm) / r.path0_dbh_cm * 100).toFixed(0) + '%'
    : '  -'
  const diffB = r.path0_dbh_cm && r.pathB_dbh_cm
    ? ((r.pathB_dbh_cm - r.path0_dbh_cm) / r.path0_dbh_cm * 100).toFixed(0) + '%'
    : '  -'
  console.log(
    (r.video_original_name || '').padEnd(22),
    String(r.path0_dbh_cm ?? '-').padStart(5),
    String(r.pathA_dbh_cm ?? '-').padStart(6),
    String(r.pathB_dbh_cm ?? '-').padStart(6),
    String(r.winner_path  ?? '-').padStart(8),
    diffA.padStart(7),
    diffB.padStart(7)
  )
})

// NULL 明細
const nullP0 = all.filter(r => r.path0_dbh_cm == null)
const nullPA = all.filter(r => r.pathA_dbh_cm == null)
const nullPB = all.filter(r => r.pathB_dbh_cm == null)
if (nullP0.length) console.log('\npath0 NULL:', nullP0.map(r => r.video_original_name).join(', '))
if (nullPA.length) console.log('pathA NULL:', nullPA.map(r => r.video_original_name).join(', '))
if (nullPB.length) console.log('pathB NULL:', nullPB.map(r => r.video_original_name).join(', '))
