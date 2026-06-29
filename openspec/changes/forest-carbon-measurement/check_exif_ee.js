// check_exif_ee.js — 用 exiftool-vendored 的 -ee 旗標提取完整 timed metadata
const { exiftool } = require('exiftool-vendored')

async function main() {
  const file = '/tmp/IMG_5803_drive.mov'
  console.log(`分析：${file}\n`)

  // 標準模式
  const tags = await exiftool.read(file, ['-G3', '-ee'])
  const keys = Object.keys(tags).filter(k => k !== 'errors' && k !== 'warnings' && !k.startsWith('_'))
  console.log(`總欄位數（含 -ee）：${keys.length}`)

  // 找 focus / lens / motor / distance / depth / subject / v9 / range
  const keywords = /focus|lens|motor|v9|depth|subject|distance|zoom|range|dof|defoc|blur|aperture/i
  const interesting = keys.filter(k => keywords.test(k))
  if (interesting.length) {
    console.log('\n=== 對焦/距離相關欄位 ===')
    interesting.forEach(k => console.log(`  ${k}: ${JSON.stringify(tags[k])}`.slice(0, 120)))
  } else {
    console.log('\n對焦/距離相關欄位：無')
  }

  // 找 v9
  const v9Keys = keys.filter(k => /v9/i.test(k))
  if (v9Keys.length) {
    console.log('\n=== v9 相關 ===')
    v9Keys.forEach(k => console.log(`  ${k}: ${JSON.stringify(tags[k])}`))
  } else {
    console.log('v9：無')
  }

  // 印所有欄位名稱（每行 5 個）
  console.log('\n=== 全部欄位名稱 ===')
  for (let i = 0; i < keys.length; i += 5) {
    console.log(keys.slice(i, i+5).join('  |  '))
  }

  await exiftool.end()
}

main().catch(e => { console.error(e); process.exit(1) })
