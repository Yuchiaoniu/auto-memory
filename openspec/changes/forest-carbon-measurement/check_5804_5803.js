// 確認 5804 兩筆 + 查 5803 的 video_drive_url
const db = require('./src/db/init').getDb()

console.log('=== 5804 兩筆 ===')
const rows5804 = db.prepare(
  "SELECT id, path0_dbh_cm, pathA_dbh_cm, winner_path FROM trees WHERE video_original_name LIKE '%5804%' ORDER BY created_at"
).all()
rows5804.forEach(r => {
  console.log(`id=${r.id.slice(0,8)} p0=${r.path0_dbh_cm} pA=${r.pathA_dbh_cm} winner=${r.winner_path}`)
})

// 圓周 / π → DBH
const circ54 = Math.round(54 / Math.PI * 10) / 10
const circ80 = Math.round(80 / Math.PI * 10) / 10
console.log(`\n54cm 周長 → DBH=${circ54}cm`)
console.log(`80cm 周長 → DBH=${circ80}cm`)
console.log(`→ 原始記錄 p0=${rows5804[0]?.path0_dbh_cm} 對應 80cm (誤差 ${Math.abs(circ80 - (rows5804[0]?.path0_dbh_cm||0)).toFixed(2)}cm)`)

console.log('\n=== 5803 Drive URL ===')
const row5803 = db.prepare(
  "SELECT id, video_drive_url, video_filename, path0_dbh_cm, pathA_dbh_cm FROM trees WHERE video_original_name LIKE '%5803%'"
).get()
if (row5803) {
  console.log(`id=${row5803.id.slice(0,8)}`)
  console.log(`video_drive_url=${row5803.video_drive_url}`)
  console.log(`video_filename=${row5803.video_filename}`)
  console.log(`p0=${row5803.path0_dbh_cm} pA=${row5803.pathA_dbh_cm}`)
} else {
  console.log('找不到 5803')
}
