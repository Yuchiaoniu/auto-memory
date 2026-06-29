const db = require('better-sqlite3')('/home/yuchi/forest-carbon-measurement/data.db');
const r = db.prepare("SELECT markdown FROM stories WHERE markdown LIKE '%台灣欅%' LIMIT 1").get();
if (r) console.log(r.markdown.slice(0, 300));
const rows = db.prepare('SELECT id, markdown FROM stories').all();
const stillBad = rows.filter(r => r.markdown && /\d+\.\d{4,}/.test(r.markdown));
console.log('仍有問題筆數:', stillBad.length);
