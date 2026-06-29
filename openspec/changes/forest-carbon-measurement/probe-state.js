const db = require('better-sqlite3')('data.db')
const fs = require('fs')

const treeCount = db.prepare('SELECT COUNT(*) AS n FROM trees').get().n
const envCount = db.prepare('SELECT COUNT(*) AS n FROM environmental_context').get().n
const storyCount = db.prepare('SELECT COUNT(*) AS n FROM stories').get().n
const eventCount = db.prepare('SELECT COUNT(*) AS n FROM events').get().n
const gtCount = db.prepare('SELECT COUNT(*) AS n FROM ground_truth').get().n
const cfCount = db.prepare('SELECT COUNT(*) AS n FROM correction_factor_log').get().n

console.log('=== SQLite ===')
console.log('trees:                  ' + treeCount)
console.log('environmental_context:  ' + envCount)
console.log('stories:                ' + storyCount)
console.log('events:                 ' + eventCount)
console.log('ground_truth:           ' + gtCount)
console.log('correction_factor_log:  ' + cfCount)

const latest = db.prepare("SELECT id, species, dbh_cm, datetime(created_at,'unixepoch','localtime') AS ct FROM trees ORDER BY created_at DESC LIMIT 3").all()
console.log('\nLatest 3 trees:')
latest.forEach(t => console.log('  ' + t.ct + '  ' + t.species + '  dbh=' + t.dbh_cm))

console.log('\n=== Files ===')
const dirs = ['uploads', 'tmp_frames', 'evidence']
dirs.forEach(d => {
  try {
    const items = fs.readdirSync(d)
    console.log(d + '/: ' + items.length + ' items')
  } catch (e) {
    console.log(d + '/: (missing)')
  }
})
