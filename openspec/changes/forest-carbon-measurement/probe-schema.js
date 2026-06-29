const db = require('better-sqlite3')('data.db')

const envCount = db.prepare('SELECT COUNT(*) AS n FROM environmental_context').get().n
console.log('environmental_context rows: ' + envCount)

const treeCols = db.prepare('PRAGMA table_info(trees)').all()
console.log('trees: ' + treeCols.length + ' columns')
const expectedNewCols = [
  'create_date', 'frame_rate', 'image_width', 'image_height',
  'altitude_m', 'illuminance_lux', 'duration_sec', 'video_codec',
  'orientation', 'gps_img_direction_deg', 'device_pressure_hpa', 'device_ambient_temp_c'
]
expectedNewCols.forEach(name => {
  const found = treeCols.find(c => c.name === name)
  console.log('  ' + (found ? '[OK]  ' : '[MISS]') + '  ' + name)
})

console.log('\ntrees rows: ' + db.prepare('SELECT COUNT(*) AS n FROM trees').get().n)
const latestTrees = db.prepare("SELECT id, species, dbh_cm, gps, create_date, altitude_m, datetime(created_at,'unixepoch','localtime') AS ct FROM trees ORDER BY created_at DESC LIMIT 5").all()
console.log('\nLatest 5 trees:')
latestTrees.forEach(t => console.log('  ' + t.id.slice(0, 8) + '  ' + t.species + '  dbh=' + t.dbh_cm + '  gps=' + (t.gps || 'n/a') + '  alt=' + (t.altitude_m || 'n/a') + '  ' + t.ct))
