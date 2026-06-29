const { getDb } = require('./init')
const { randomUUID } = require('crypto')

function insert({ treeId, actualDbhCm, estimatedDbhCm, source }) {
  const correctionFactor = estimatedDbhCm > 0
    ? Math.round((actualDbhCm / estimatedDbhCm) * 10000) / 10000
    : null
  const id = randomUUID()
  getDb().prepare(`
    INSERT INTO ground_truth (id, tree_id, actual_dbh_cm, estimated_dbh_cm, correction_factor, source)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(id, treeId, actualDbhCm, estimatedDbhCm, correctionFactor, source)
  return { id, correctionFactor }
}

// §30 人工皮尺實量寫入（獨立於 path 0/A 自填的 actual_dbh_cm）
// 一棵樹一個 manual 值：source='manual' 已存在則更新；否則插入新列
function upsertManual({ treeId, manualDbhCm, measuredBy = null, notes = null }) {
  const db = getDb()
  const existing = db.prepare(
    `SELECT id FROM ground_truth WHERE tree_id = ? AND source = 'manual' LIMIT 1`
  ).get(treeId)

  const now = Math.floor(Date.now() / 1000)
  if (existing) {
    db.prepare(`
      UPDATE ground_truth
      SET manual_dbh_cm = ?, actual_dbh_cm = ?, measured_by = ?, measured_at = ?, notes = ?
      WHERE id = ?
    `).run(manualDbhCm, manualDbhCm, measuredBy, now, notes, existing.id)
    return { id: existing.id, updated: true }
  }

  const id = randomUUID()
  db.prepare(`
    INSERT INTO ground_truth
      (id, tree_id, actual_dbh_cm, manual_dbh_cm, source, measured_by, measured_at, notes)
    VALUES (?, ?, ?, ?, 'manual', ?, ?, ?)
  `).run(id, treeId, manualDbhCm, manualDbhCm, measuredBy, now, notes)
  return { id, updated: false }
}

function getManualByTreeId(treeId) {
  return getDb().prepare(
    `SELECT * FROM ground_truth WHERE tree_id = ? AND source = 'manual' LIMIT 1`
  ).get(treeId) || null
}

function getByTreeId(treeId) {
  return getDb().prepare('SELECT * FROM ground_truth WHERE tree_id = ? ORDER BY created_at DESC').all(treeId)
}

function getStats() {
  return getDb().prepare(`
    SELECT source, COUNT(*) as count,
           AVG(correction_factor) as avg_correction,
           MIN(correction_factor) as min_correction,
           MAX(correction_factor) as max_correction
    FROM ground_truth
    WHERE correction_factor IS NOT NULL
    GROUP BY source
  `).all()
}

module.exports = { insert, upsertManual, getManualByTreeId, getByTreeId, getStats }
