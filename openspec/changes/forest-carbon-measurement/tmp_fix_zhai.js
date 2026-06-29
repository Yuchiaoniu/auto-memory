const db = require('better-sqlite3')('/home/yuchi/forest-carbon-measurement/data.db');
const rows = db.prepare("SELECT id, markdown FROM stories WHERE markdown LIKE '%還債%'").all();
const upd  = db.prepare('UPDATE stories SET markdown=? WHERE id=?');
let fixed = 0;
rows.forEach(r => {
  // 移除整句（含前後可能的換行）
  const newMd = r.markdown
    .replace(/每多一棵這樣的樹，就是給大氣的一次小小還債。\n?/g, '')
    .replace(/\n{3,}/g, '\n\n'); // 避免留下多餘空行
  upd.run(newMd, r.id);
  fixed++;
});
console.log('已移除「還債」句共', fixed, '筆');
// 驗證
const remain = db.prepare("SELECT COUNT(*) as n FROM stories WHERE markdown LIKE '%還債%'").get();
console.log('殘留:', remain.n, '筆');
