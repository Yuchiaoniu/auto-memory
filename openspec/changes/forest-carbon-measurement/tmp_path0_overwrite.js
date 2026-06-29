// Path 0 覆寫腳本：把 manual_tape_dbh_cm 寫入 path0_*, 並改 winner=path0
// 用 species formula 重算 volume / carbon
const path = require('path')
process.chdir('/home/yuchi/forest-carbon-measurement')
const Database = require('better-sqlite3')
const { getFormulaByScientificName } = require('./src/data/formulaDb')

const db = new Database('data.db')

const rows = db.prepare(`
  SELECT id, species, manual_tape_dbh_cm, manual_tape_frame_ts_sec,
         path0_dbh_cm, dbh_cm, volume_m3, carbon_kg, winner_path
  FROM trees
  ORDER BY id
`).all()

console.log(`找到 ${rows.length} 棵樹`)
console.log()

const update = db.prepare(`
  UPDATE trees SET
    path0_dbh_cm = @path0_dbh_cm,
    path0_volume_m3 = @path0_volume_m3,
    path0_carbon_kg = @path0_carbon_kg,
    winner_path = 'path0',
    dbh_cm = @dbh_cm,
    volume_m3 = @volume_m3,
    carbon_kg = @carbon_kg,
    original_dbh_cm = NULL,
    applied_correction_factor = NULL
  WHERE id = @id
`)

let okCount = 0
let skipCount = 0

const tx = db.transaction(() => {
  for (const r of rows) {
    const dbh = r.manual_tape_dbh_cm
    if (!(dbh > 0)) {
      console.log(`[SKIP] ${r.id.slice(0, 8)} species=${r.species} 沒有 manual_tape_dbh_cm`)
      skipCount++
      continue
    }
    const formula = getFormulaByScientificName(r.species)
    const heightM = formula.hdA * Math.pow(dbh, formula.hdB)
    const volumeM3 = formula.volA * Math.pow(dbh, formula.volB) * Math.pow(heightM, formula.volC)
    const carbonKg = volumeM3 * formula.woodDensity * formula.bef * 0.5

    const newDbh = Math.round(dbh * 10) / 10
    const newH = Math.round(heightM * 10) / 10
    const newV = Math.round(volumeM3 * 10000) / 10000
    const newC = Math.round(carbonKg * 10) / 10

    update.run({
      id: r.id,
      path0_dbh_cm: newDbh,
      path0_volume_m3: newV,
      path0_carbon_kg: newC,
      dbh_cm: newDbh,
      volume_m3: newV,
      carbon_kg: newC,
    })

    console.log(`[OK]   ${r.id.slice(0, 8)} ${r.species.padEnd(28)} ` +
      `舊DBH=${(r.dbh_cm ?? '?').toString().padStart(5)} → 新DBH=${newDbh}cm  ` +
      `H=${newH}m V=${newV}m³ C=${newC}kg  (was winner=${r.winner_path})`)
    okCount++
  }
})

tx()

console.log()
console.log(`完成：${okCount} 棵覆寫，${skipCount} 棵跳過`)

const summary = db.prepare(`
  SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN winner_path='path0' THEN 1 ELSE 0 END) AS winner_path0,
    SUM(CASE WHEN path0_dbh_cm IS NOT NULL THEN 1 ELSE 0 END) AS path0_filled,
    ROUND(AVG(path0_dbh_cm), 2) AS avg_path0_dbh,
    ROUND(SUM(carbon_kg), 1) AS total_carbon_kg
  FROM trees
`).get()
console.log()
console.log('=== 覆寫後總覽 ===')
console.log(summary)

db.close()
