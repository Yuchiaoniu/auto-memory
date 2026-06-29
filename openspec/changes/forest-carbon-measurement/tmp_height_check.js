const db = require('better-sqlite3')('/home/yuchi/forest-carbon-measurement/data.db');

// 查樹高計算來源
const sample = db.prepare(`
  SELECT video_original_name,
         json_extract(raw_result, '$.carbon.heightM') as height_m,
         json_extract(raw_result, '$.calibratedDbhCm') as dbh_cm,
         json_extract(raw_result, '$.species.primary') as species
  FROM trees WHERE winner_path='p4v2' LIMIT 8
`).all();
sample.forEach(r => console.log(r.video_original_name, 'DBH:', r.dbh_cm?.toFixed(1), 'H:', r.height_m?.toFixed(1), 'm =', r.height_m ? (r.height_m/3).toFixed(1) : '?', '樓', r.species));

// 查「還債」句子在幾棵樹的故事裡
const bad = db.prepare("SELECT COUNT(*) as n FROM stories WHERE markdown LIKE '%還債%'").get();
console.log('\n「還債」出現在故事裡:', bad.n, '筆');
