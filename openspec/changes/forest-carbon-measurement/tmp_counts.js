const db = require('better-sqlite3')('/home/yuchi/forest-carbon-measurement/data.db');
const total = db.prepare('SELECT COUNT(*) as n FROM trees').get().n;
const p4v2 = db.prepare("SELECT COUNT(*) as n FROM trees WHERE winner_path='p4v2'").get().n;
const withStory = db.prepare("SELECT COUNT(DISTINCT tree_id) as n FROM stories WHERE tree_id IN (SELECT id FROM trees)").get().n;
const orphan = db.prepare("SELECT COUNT(DISTINCT tree_id) as n FROM stories WHERE tree_id NOT IN (SELECT id FROM trees)").get().n;
console.log('trees 總數:', total);
console.log('winner_path=p4v2:', p4v2);
console.log('有故事且樹存在:', withStory);
console.log('孤兒故事(tree已不存在):', orphan);
