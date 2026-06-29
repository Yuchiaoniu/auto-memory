const db = require('./src/db/init').getDb();
const nullA = db.prepare('SELECT id, species, video_original_name, path0_dbh_cm, pathB_dbh_cm, tmp_frames_dir, raw_result FROM trees WHERE pathA_dbh_cm IS NULL ORDER BY created_at').all();
console.log('pathA NULL:', nullA.length);
nullA.forEach(t => {
  let rr = {};
  try { rr = JSON.parse(t.raw_result || '{}'); } catch(_) {}
  const frames = rr.rawFrames || [];
  const ref = frames.filter(f => f.referenceDetected);
  const atTrunk = ref.filter(f => f.referenceAtTrunk);
  console.log('---');
  console.log('id:', t.id.slice(0,8), t.video_original_name || '?');
  console.log('p0:', t.path0_dbh_cm + 'cm', 'pB:', t.pathB_dbh_cm + 'cm');
  console.log('frames:', frames.length, 'ref:', ref.length, 'atTrunk:', atTrunk.length);
  console.log('tmpDir:', t.tmp_frames_dir || 'NULL');
  ref.forEach((f,i) => console.log('  ref['+i+']:', f.referenceType, 'ratio='+f.trunkToReferenceRatio, 'atTrunk='+f.referenceAtTrunk, 'conf='+f.referenceConfidence));
});
