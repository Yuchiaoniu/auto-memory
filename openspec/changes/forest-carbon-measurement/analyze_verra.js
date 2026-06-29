// 門檻掃描 + Verra 不確定性指標（用中位數彙總）
const { getDb } = require('./src/db/init')
const CARD = 8.56
const median = a => { const v = [...a].sort((x, y) => x - y); return v[Math.floor(v.length / 2)] }
const rows = getDb().prepare("SELECT raw_result FROM trees WHERE winner_path IN ('p4','p4v2')").all()
const recs = []
for (const r of rows) {
  let rr; try { rr = JSON.parse(r.raw_result) } catch { continue }
  const ratios = (rr.ratios || []).filter(x => x > 0), tape = rr.manualTapeCm
  if (!ratios.length || !tape) continue
  const dbh = median(ratios) * CARD
  recs.push({ tape, dbh, errPct: Math.abs(dbh - tape) / tape * 100, errCm: dbh - tape })
}
const n = recs.length
// 門檻掃描
console.log('=== 中位數：不同門檻通過率 ===')
for (const th of [10, 15, 20, 25, 30]) {
  const p = recs.filter(r => r.errPct <= th).length
  console.log(`  ≤${th}%: ${p}/${n} = ${(p / n * 100).toFixed(0)}%`)
}
// Verra 不確定性（DBH 層級）
const meanTape = recs.reduce((s, r) => s + r.tape, 0) / n
const meanDbh = recs.reduce((s, r) => s + r.dbh, 0) / n
const bias = recs.reduce((s, r) => s + r.errCm, 0) / n
const stdErr = Math.sqrt(recs.reduce((s, r) => s + (r.errCm - bias) ** 2, 0) / (n - 1))
const SE = stdErr / Math.sqrt(n)
const t = 1.699 // df=29, alpha=0.1
const ciHalf = SE * t
const ciOverMeanDbh = ciHalf / meanDbh * 100
console.log('\n=== Verra §8.4 不確定性（DBH 層級）===')
console.log(`n=${n}`)
console.log(`mean tape = ${meanTape.toFixed(1)} cm`)
console.log(`mean DBH  = ${meanDbh.toFixed(1)} cm`)
console.log(`bias      = ${bias.toFixed(2)} cm (${(bias / meanTape * 100).toFixed(1)}%)`)
console.log(`std of error = ${stdErr.toFixed(2)} cm`)
console.log(`SE = ${SE.toFixed(2)} cm`)
console.log(`90% CI half-width = ${ciHalf.toFixed(2)} cm`)
console.log(`CI half-width / mean (DBH) = ${ciOverMeanDbh.toFixed(1)}%  (Verra 紅線 < 100%)`)
console.log(`AGB 層級約 (×2) = ${(ciOverMeanDbh * 2).toFixed(1)}%`)
