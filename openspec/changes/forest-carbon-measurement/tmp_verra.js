const db = require('better-sqlite3')('/home/yuchi/forest-carbon-measurement/data.db');
// p4v2 樹：calibratedDbhCm 在 raw_result 頂層
const rows = db.prepare(`
  SELECT video_original_name,
         manual_tape_dbh_cm,
         json_extract(raw_result, '$.calibratedDbhCm') as p4_dbh
  FROM trees
  WHERE winner_path = 'p4v2'
    AND manual_tape_dbh_cm IS NOT NULL
    AND json_extract(raw_result, '$.calibratedDbhCm') IS NOT NULL
`).all();
console.log('可比對棵數:', rows.length);
const errors = rows.map(r => r.p4_dbh - r.manual_tape_dbh_cm);
const mean_tape = rows.reduce((s,r) => s + r.manual_tape_dbh_cm, 0) / rows.length;
const mean_p4   = rows.reduce((s,r) => s + r.p4_dbh, 0) / rows.length;
const bias = errors.reduce((s,e) => s + e, 0) / rows.length;
const std = Math.sqrt(errors.map(e => (e - bias)**2).reduce((s,v) => s+v, 0) / (errors.length - 1));
const se = std / Math.sqrt(rows.length);
const df = rows.length - 1;
// t(α=0.1) 臨界值：df=27→1.703, df=28→1.701, df=29→1.699
const t_table = {27:1.703, 28:1.701, 29:1.699, 30:1.697};
const t_val = t_table[df] || 1.699;
const ci = se * t_val;
console.log('mean tape:', mean_tape.toFixed(2), 'cm');
console.log('mean P4:', mean_p4.toFixed(2), 'cm');
console.log('bias:', bias.toFixed(2), 'cm (', (bias/mean_tape*100).toFixed(1), '%)');
console.log('std of error:', std.toFixed(2), 'cm');
console.log('SE = std/√n:', se.toFixed(3), 'cm');
console.log('df:', df, '  t:', t_val);
console.log('90% CI half-width:', ci.toFixed(2), 'cm');
console.log('CI/mean:', (ci/mean_tape*100).toFixed(1), '%');
