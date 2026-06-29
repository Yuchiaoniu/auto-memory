// check_target_trees.js — 查詢 5798/5803/5804/5812/5818 的 DB 資訊
const db = require('./src/db/init').getDb()
const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const targets = ['5798', '5803', '5804', '5812', '5818']
const rows = db.prepare(`
  SELECT id, video_original_name, duration_sec, tmp_frames_dir,
         path0_dbh_cm, pathA_dbh_cm, pathB_dbh_cm, species, image_width
  FROM trees
  WHERE ${targets.map(t => `video_original_name LIKE '%${t}%'`).join(' OR ')}
  ORDER BY video_original_name
`).all()

console.log(`找到 ${rows.length} 棵：\n`)
rows.forEach(r => {
  console.log(`--- ${r.id.slice(0,8)} ${r.video_original_name}`)
  console.log(`    species=${r.species}  dur=${r.duration_sec}s  iw=${r.image_width}`)
  console.log(`    p0=${r.path0_dbh_cm}  pA=${r.pathA_dbh_cm}  pB=${r.pathB_dbh_cm}`)
  console.log(`    tmpDir=${r.tmp_frames_dir}`)

  // 計算 frameIdx 對應各時間戳
  const timestamps = { '5798': 7, '5803': 10, '5804': [15, 37], '5812': 12, '5818': 35 }
  const nameNum = Object.keys(timestamps).find(k => r.video_original_name.includes(k))
  if (nameNum && r.duration_sec) {
    const tsList = [].concat(timestamps[nameNum])
    tsList.forEach(ts => {
      const idx = Math.round(ts / r.duration_sec * 12)
      const clamped = Math.max(0, Math.min(12, idx))
      console.log(`    ts=${ts}s → frameIdx=${clamped}`)
    })
  }

  // 檢查 tmp_frames 是否存在
  if (r.tmp_frames_dir) {
    const dir = path.join(process.cwd(), 'tmp_frames', r.tmp_frames_dir)
    if (fs.existsSync(dir)) {
      const files = fs.readdirSync(dir).filter(f => f.endsWith('.jpg'))
      console.log(`    tmp_frames: ${files.length} 幀存在`)
    } else {
      console.log(`    tmp_frames: ⚠️ 目錄不存在`)
    }
  }
  console.log()
})

console.log('=== 檢查原始影片 ===')
const uploadsDir = path.join(process.cwd(), 'uploads')
if (fs.existsSync(uploadsDir)) {
  const uploadsFiles = fs.readdirSync(uploadsDir)
  targets.forEach(t => {
    const found = uploadsFiles.filter(f => f.toLowerCase().includes(t.toLowerCase().replace('img_', '')))
    console.log(`${t}: ${found.length > 0 ? found.join(', ') : '❌ 不存在'}`)
  })
} else {
  console.log('uploads/ 目錄不存在')
}
