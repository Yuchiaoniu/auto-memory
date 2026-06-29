(async () => {
  const weather = require('./src/services/weatherService')
  const phenology = require('./src/services/phenologyService')
  const solar = require('./src/services/solarService')

  const lat = 22.7353, lng = 121.0666, alt = 250
  const unixTs = Math.floor(Date.now() / 1000) - 86400
  console.log('Testing env snapshot @', new Date(unixTs * 1000).toISOString(), 'lat=', lat, 'lng=', lng, 'alt=', alt)

  const sun = solar.getSunPosition(lat, lng, unixTs)
  console.log('\n[solar]', JSON.stringify(sun, null, 2))

  const tags = phenology.inferPhenologyTags({ unixTs, lat, altitudeM: alt })
  const zone = phenology.inferForestZone(alt)
  const month = new Date(unixTs * 1000).getMonth() + 1
  const season = phenology.inferSeason(month, lat)
  console.log('\n[phenology] zone=', zone, ' season=', season, ' month=', month)
  console.log('[phenology] tags=', tags)
  console.log('[phenology] desc=', phenology.describePhenology(tags))

  console.log('\n[open-meteo] fetching...')
  const snap = await weather.getEnvironmentSnapshot(lat, lng, unixTs, alt)
  if (!snap) {
    console.log('  -> snapshot NULL (open-meteo failed)')
    return
  }
  const { rawOpenmeteoJson, ...summary } = snap
  console.log(JSON.stringify(summary, null, 2))
  console.log('\n[OK] env snapshot complete')
})().catch(e => { console.error('ERR:', e.message); process.exit(1) })
