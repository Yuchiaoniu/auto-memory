// §27.8 一次性重置腳本（VM 上執行）
// - 清空 7 表（保留 schema 與 projects/plots/blockchain_jobs/evaluation_runs）
// - 清空 uploads/tmp_frames/evidence
// - 推送清空版 trees.json 到 GitHub
require('dotenv').config()
const fs = require('fs')
const path = require('path')
const Database = require('better-sqlite3')

const db = new Database('data.db')

console.log('=== §27.8 reset start ===')

const before = {
  trees: db.prepare('SELECT COUNT(*) AS n FROM trees').get().n,
  env:   db.prepare('SELECT COUNT(*) AS n FROM environmental_context').get().n,
  stories: db.prepare('SELECT COUNT(*) AS n FROM stories').get().n,
  events:  db.prepare('SELECT COUNT(*) AS n FROM events').get().n,
  gt:      db.prepare('SELECT COUNT(*) AS n FROM ground_truth').get().n,
  cmt:     db.prepare('SELECT COUNT(*) AS n FROM event_comments').get().n,
  cf:      db.prepare('SELECT COUNT(*) AS n FROM correction_factor_log').get().n,
}
console.log('Before:', before)

db.pragma('foreign_keys = OFF')
const tx = db.transaction(() => {
  db.exec('DELETE FROM environmental_context')
  db.exec('DELETE FROM stories')
  db.exec('DELETE FROM ground_truth')
  db.exec('DELETE FROM event_comments')
  db.exec('DELETE FROM events')
  db.exec('DELETE FROM correction_factor_log')
  db.exec('DELETE FROM blockchain_jobs')
  db.exec('DELETE FROM evaluation_runs')
  db.exec('DELETE FROM trees')
})
tx()
db.pragma('foreign_keys = ON')

const after = {
  trees: db.prepare('SELECT COUNT(*) AS n FROM trees').get().n,
  env:   db.prepare('SELECT COUNT(*) AS n FROM environmental_context').get().n,
  stories: db.prepare('SELECT COUNT(*) AS n FROM stories').get().n,
  events:  db.prepare('SELECT COUNT(*) AS n FROM events').get().n,
  gt:      db.prepare('SELECT COUNT(*) AS n FROM ground_truth').get().n,
  cmt:     db.prepare('SELECT COUNT(*) AS n FROM event_comments').get().n,
  cf:      db.prepare('SELECT COUNT(*) AS n FROM correction_factor_log').get().n,
  bc:      db.prepare('SELECT COUNT(*) AS n FROM blockchain_jobs').get().n,
  eval:    db.prepare('SELECT COUNT(*) AS n FROM evaluation_runs').get().n,
}
console.log('After: ', after)
db.close()

// 檔案系統清理
console.log('\n=== filesystem cleanup ===')
const dirs = ['uploads', 'tmp_frames', 'evidence', 'public/videos']
dirs.forEach(d => {
  if (!fs.existsSync(d)) { console.log(d + ': (none)'); return }
  const items = fs.readdirSync(d)
  let count = 0
  items.forEach(name => {
    const p = path.join(d, name)
    try {
      const st = fs.statSync(p)
      if (st.isDirectory()) fs.rmSync(p, { recursive: true, force: true })
      else fs.unlinkSync(p)
      count++
    } catch (e) { console.warn('  skip ' + p + ': ' + e.message) }
  })
  console.log(d + ': removed ' + count + ' items')
})

// trees.json 同步（推空陣列到 GitHub）
console.log('\n=== github sync (empty trees.json) ===')
;(async () => {
  try {
    const { pushTreesJson } = require('./src/services/githubSyncService')
    await pushTreesJson()
    console.log('github-sync OK')
  } catch (e) {
    console.warn('github-sync failed: ' + e.message)
  }
  console.log('\n=== §27.8 reset done ===')
})()
