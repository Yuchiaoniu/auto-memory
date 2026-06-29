// v2 彙總法 + 校準因子分析
const { getDb } = require('./src/db/init')
const CARD = 8.56
const mean = a => a.reduce((s, x) => s + x, 0) / a.length
const median = a => { const v = [...a].sort((x, y) => x - y); return v[Math.floor(v.length / 2)] }
const trim1 = a => { const v = [...a].sort((x, y) => x - y); const t = v.length > 2 ? v.slice(1, -1) : v; return mean(t) }
function cluster(a) {
  const v = [...a].sort((x, y) => x - y); let gi = 0, gm = -1
  for (let i = 0; i < v.length - 1; i++) { const g = v[i + 1] - v[i]; if (g > gm) { gm = g; gi = i } }
  const left = v.slice(0, gi + 1), right = v.slice(gi + 1)
  const range = v[v.length - 1] - v[0], avgGap = range / (v.length - 1)
  const bimodal = gm > 1.5 * avgGap && Math.min(left.length, right.length) >= 2
  return { bimodal, big: left.length >= right.length ? left : right }
}
const methods = ['median', 'trimAll', 'cluMed', 'cluTrim', 'biTrim']
const rows = getDb().prepare("SELECT raw_result FROM trees WHERE winner_path IN ('p4','p4v2')").all()
const data = []
for (const r of rows) {
  let rr; try { rr = JSON.parse(r.raw_result) } catch { continue }
  const ratios = (rr.ratios || []).filter(x => x > 0), tape = rr.manualTapeCm
  if (!ratios.length || !tape) continue
  const c = cluster(ratios)
  data.push({ tape, agg: { median: median(ratios), trimAll: trim1(ratios), cluMed: median(c.big), cluTrim: trim1(c.big), biTrim: c.bimodal ? trim1(ratios) : median(ratios) }, bimodal: c.bimodal })
}
const n = data.length
console.log(`n=${n} 棵\n`)
console.log('方法\t原始PASS\t原始平均誤差\t校準因子\t校準後PASS\t校準後平均誤差')
for (const m of methods) {
  let pass = 0, sumErr = 0, sumTape = 0, sumDbh = 0
  for (const d of data) { const dbh = d.agg[m] * CARD; const e = Math.abs(dbh - d.tape) / d.tape * 100; sumErr += e; if (e <= 15) pass++; sumTape += d.tape; sumDbh += dbh }
  const factor = sumTape / sumDbh
  let pass2 = 0, sumErr2 = 0
  for (const d of data) { const dbh = d.agg[m] * CARD * factor; const e = Math.abs(dbh - d.tape) / d.tape * 100; sumErr2 += e; if (e <= 15) pass2++ }
  console.log(`${m}\t${pass}/${n}=${(pass / n * 100).toFixed(0)}%\t${(sumErr / n).toFixed(1)}%\t×${factor.toFixed(3)}\t${pass2}/${n}=${(pass2 / n * 100).toFixed(0)}%\t${(sumErr2 / n).toFixed(1)}%`)
}
const biN = data.filter(d => d.bimodal).length
console.log(`\n雙峰樹: ${biN}/${n}`)
