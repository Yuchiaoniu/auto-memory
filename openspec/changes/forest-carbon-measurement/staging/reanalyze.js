// §29.3 backfill: write frame_analyses rows from each tree's raw_result.rawFrames
// Historical 31 trees: rawFrames is 5 items (Gemini-analyzed); frame_idx stored as 0..4 (array position).
// New uploads (after §29 deploy) populate frame_analyses inside processVideo with real tmp_frames frame_N idx.

require('dotenv').config()
const Database = require('better-sqlite3')
const path = require('path')
const fs = require('fs')

const { insertMany } = require('./src/db/frameAnalyses')

const db = new Database('data.db')

function main() {
  console.log('=== reanalyze backfill start ===')
  const trees = db.prepare(`
    SELECT id, video_original_name, raw_result, created_at
    FROM trees
    WHERE raw_result IS NOT NULL
    ORDER BY created_at ASC
  `).all()

  let ok = 0, skip = 0, fail = 0, totalRows = 0
  for (const t of trees) {
    let raw
    try { raw = JSON.parse(t.raw_result) } catch (e) { fail++; console.warn('  bad JSON:', t.id); continue }
    const frames = Array.isArray(raw?.rawFrames) ? raw.rawFrames : null
    if (!frames || frames.length === 0) { skip++; continue }

    const enriched = frames.map((f, i) => ({
      ...f,
      frameIdx: i,
      frameQualityLabel: raw?.median?.frameQuality || null,
    }))

    try {
      const n = insertMany(t.id, enriched)
      ok++; totalRows += n
      console.log(`  ${t.id.slice(0,8)} ${t.video_original_name} → ${n} rows`)
    } catch (e) {
      fail++; console.warn(`  FAIL ${t.id.slice(0,8)}:`, e.message)
    }
  }

  console.log('--- map tree → tmp_frames_dir by mtime proximity ---')
  const dirsRoot = path.join(process.cwd(), 'tmp_frames')
  const dirs = fs.existsSync(dirsRoot)
    ? fs.readdirSync(dirsRoot).map(d => {
        const full = path.join(dirsRoot, d)
        try { return { dir: d, mtime: fs.statSync(full).mtimeMs } } catch { return null }
      }).filter(Boolean).sort((a, b) => a.mtime - b.mtime)
    : []

  const updateStmt = db.prepare('UPDATE trees SET tmp_frames_dir = ? WHERE id = ?')
  let mapped = 0
  for (const t of trees) {
    const treeMs = t.created_at * 1000
    let best = null, bestDelta = Infinity
    for (const d of dirs) {
      const delta = Math.abs(d.mtime - treeMs)
      if (delta < bestDelta) { bestDelta = delta; best = d }
    }
    // 接受 ±10 分鐘內的最近匹配
    if (best && bestDelta <= 10 * 60 * 1000) {
      updateStmt.run(best.dir, t.id)
      mapped++
    }
  }

  console.log(`\n=== summary ===`)
  console.log(`  ok=${ok} skip=${skip} fail=${fail} totalRows=${totalRows}`)
  console.log(`  tmp_frames_dir mapped: ${mapped}/${trees.length}`)
  db.close()
}

main()
