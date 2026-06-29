// dump_ee_allkeys.js — 把 -ee 全部欄位名稱寫到 /tmp/ee_keys.txt 供搜尋
const { exiftool } = require('exiftool-vendored')
const fs = require('fs')

async function main() {
  const file = '/tmp/IMG_5803_drive.mov'
  console.log(`讀取：${file}`)

  const tags = await exiftool.read(file, ['-G3', '-ee'])
  const keys = Object.keys(tags).filter(k => k !== 'errors' && k !== 'warnings' && !k.startsWith('_'))
  console.log(`總欄位數：${keys.length}`)

  // 寫出所有欄位名稱 + 值（完整，不截斷）
  const lines = keys.map(k => {
    const v = tags[k]
    const val = v === null || v === undefined ? '(null)' : (typeof v === 'object' ? JSON.stringify(v) : String(v))
    return `${k}: ${val}`
  })
  fs.writeFileSync('/tmp/ee_keys.txt', lines.join('\n'), 'utf8')
  console.log('已寫出 /tmp/ee_keys.txt')

  // 同時找數值型欄位（可能是 0–1 的馬達位置）
  console.log('\n=== 純數字欄位（可能是 0–1 馬達位置）===')
  const numericKeys = keys.filter(k => {
    const v = tags[k]
    return typeof v === 'number' && v >= 0 && v <= 1.5
  })
  numericKeys.forEach(k => console.log(`  ${k}: ${tags[k]}`))

  // 找包含 lens / focus / motor / position / distance 的欄位（不分大小寫）
  console.log('\n=== lens/focus/motor/position/distance 相關 ===')
  const motorKeys = keys.filter(k => /lens|focus|motor|position|distance|focal|aperture|dof|depth|v9/i.test(k))
  if (motorKeys.length) {
    motorKeys.forEach(k => console.log(`  ${k}: ${JSON.stringify(tags[k])}`))
  } else {
    console.log('  無')
  }

  // 列出所有包含 Apple 特殊前綴的欄位
  console.log('\n=== Apple QuickTime 特殊欄位 ===')
  const appleKeys = keys.filter(k => /apple|quicktime|sensor|track|timed/i.test(k))
  appleKeys.forEach(k => console.log(`  ${k}: ${JSON.stringify(tags[k])?.slice(0, 100)}`))

  await exiftool.end()
  console.log('\n完成。全欄位見 /tmp/ee_keys.txt')
}

main().catch(e => { console.error(e); process.exit(1) })
