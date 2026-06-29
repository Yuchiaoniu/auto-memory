// 逐棵明細：tape / 原始P4 / 各統計法 v2 誤差
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
  return { bimodal: gm > 1.5 * avgGap && Math.min(left.length, right.length) >= 2, big: left.length >= right.length ? left : right }
}
const IMG = { '1lpkf7TYbWLylUKtG0ABFdZDitkW2T0wN':'5786','13fgOJO--W4opami5ZVKoqIl7Nxk-Ec6F':'5787','1F0437umBsIGv_-oetcpKQokZW9KSXjcp':'5788','1LLyAp4BjgjwX5cPHdP42rmasGPcZSycH':'5789','1HrK9Iz2h2PqyeyC1b1rLvFipP6jpwD-P':'5790','1fFNvMJSiDo6h0cGK7VBfDW7_Q9pE7aL4':'5791','1oFUNweQ1E2BCJRuuEFgATXYRUV5rWzON':'5792','1ZVDRkpkw0M7RYwS03Fdf19pAJKT4AnZ5':'5793','1vk4A2WYgoGBxN581kf5H3vshPOimerGj':'5794','1mAsxJchl2JRrYMyxSWBz8yRzTTvNpDmD':'5795','1-yXWP7XWpgTeZBDQC9sHyOpIxljxm_tH':'5798','19hdCOLZKBOLf1F3rtZ1LLeukXUw2NAFy':'5799','1yvo9_vja1TJOFl8TTiHQDHi9vMNbRfTf':'5800','1vwIqBt4Zob3wno3999dgfQkF5SSggRi6':'5801','1lVacWtaNhrMq3oM2cfOgWYa7namSLlrK':'5802','1U3Mi5Gtu_BqsYV2CjAyVQB4wy6J2ZbAu':'5803','1z1kzhPx4kUOj6opGt4ZILyawIQjcSvyp':'5805','1ybyFmKlFRx3kuNFVSNYJBP4dMa2KfcL7':'5806','1EbJkGAZpmb9CbMm0YlnKQhqEKaJ9olzB':'5807','1Kzcy00bGk-kZjL8lQQ66wD1v-OZkOgAb':'5808','1DY1OV8PEPjR3XGIcyVne1AtO1QdpUHUF':'5809','1v6BthyaAo0uY4HvIs-yK5_YETJnWSV-5':'5810','1CgeLGT-k2NiW54MXdInjuI5OAlYsTlf5':'5811','1cbNBVVyqf0M0ShepbWT230yF4bddN4yA':'5812','1e5CytcJRc7XhbdK_j0UWuUiYkH6YqKrD':'5813','1DgPf1kPfqynAWSJBY44XM65dVkeLross':'5814','1hAJOWC6SO9urNIn0aLESVQ7u1JUfZeHT':'5815','1MYhIVJI2SBkbpAZFBoq7OdJgA4N5pog6':'5817','13qfRS4GWJvWL-ur4F54pndHzsCTl5a9H':'5818','1dFF4DF0JVlZqgxCQeOSxMSvnlybOCOfn':'5819' }
const OP4 = { '5786':8.0,'5787':2.2,'5788':null,'5789':15.2,'5790':15.5,'5791':0.7,'5792':19.2,'5793':41.2,'5794':5.4,'5795':30.0,'5798':14.5,'5799':27.1,'5800':11.4,'5801':0.6,'5802':22.3,'5803':45.6,'5805':9.5,'5806':22.7,'5807':11.7,'5808':21.4,'5809':29.4,'5810':3.7,'5811':4.6,'5812':4.2,'5813':4.6,'5814':51.2,'5815':1.2,'5817':4.9,'5818':11.4,'5819':7.9 }
const rows = getDb().prepare("SELECT raw_result FROM trees WHERE winner_path IN ('p4','p4v2')").all()
const out = []
for (const r of rows) {
  let rr; try { rr = JSON.parse(r.raw_result) } catch { continue }
  const ratios = (rr.ratios || []).filter(x => x > 0), tape = rr.manualTapeCm, img = IMG[rr.driveFileId] || '?'
  if (!ratios.length || !tape) continue
  const c = cluster(ratios)
  const e = m => { const dbh = m * CARD; return Math.abs(dbh - tape) / tape * 100 }
  out.push({ img, tape, op4: OP4[img], med: e(median(ratios)), trim: e(trim1(ratios)), cmed: e(median(c.big)), ctrim: e(trim1(c.big)), bi: e(c.bimodal ? trim1(ratios) : median(ratios)) })
}
out.sort((a, b) => a.img.localeCompare(b.img))
console.log('IMG\ttape\t原始P4\t中位數\t去頭去尾\t峰中位\t峰trim\t雙峰trim')
const f = x => x == null ? '-' : x.toFixed(0)
for (const o of out) console.log(`${o.img}\t${o.tape}\t${f(o.op4)}\t${f(o.med)}\t${f(o.trim)}\t${f(o.cmed)}\t${f(o.ctrim)}\t${f(o.bi)}`)
console.log(`\nn=${out.length}`)
