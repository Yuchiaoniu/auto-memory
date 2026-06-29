const db = require('./src/db/init').getDb()
const cols = db.prepare('PRAGMA table_info(trees)').all()
cols.forEach(c => console.log(c.cid, c.name, c.type, c.notnull ? 'NOT NULL' : '', c.dflt_value || ''))
