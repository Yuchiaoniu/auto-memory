// 深查 pathA NULL 樹的 rawFrames fraction 欄位，看能否從像素寬度計算 ratio
const db = require('./src/db/init').getDb();
const nullA = db.prepare('SELECT id, species, video_original_name, path0_dbh_cm, image_width, image_height, raw_result FROM trees WHERE pathA_dbh_cm IS NULL ORDER BY created_at').all();

console.log('pathA NULL:', nullA.length, '棵\n');

const REFERENCE_SIZES = {
  creditcard: { width: 85.6 }, businesscard: { width: 90 },
  a4: { width: 210 }, a5: { width: 148 }, b5notebook: { width: 182 },
  ruler30: { width: 300 }, ruler100: { width: 1000 },
  banknote100: { width: 145 }, banknote500: { width: 155 }, banknote1000: { width: 160 },
};

let recoverable = 0, total = nullA.length;

nullA.forEach(t => {
  let rr = {};
  try { rr = JSON.parse(t.raw_result || '{}'); } catch(_) {}
  const frames = rr.rawFrames || [];
  const iw = t.image_width || rr.metadata?.imageWidth || 1920;
  const ih = t.image_height || rr.metadata?.imageHeight || 1080;

  console.log('---');
  console.log('id:', t.id.slice(0,8), t.video_original_name, '| p0:', t.path0_dbh_cm + 'cm');

  // 每個 frame 詳細分析
  const candidates = [];
  frames.forEach((f, i) => {
    if (!f.referenceDetected) return;
    const refType = f.referenceType;
    const refSize = REFERENCE_SIZES[refType];
    const trunkFrac = f.trunkWidthFraction || 0;
    const refFrac = f.referenceWidthFraction || 0;
    const trunkPx = Math.round(trunkFrac * iw);
    const refPx = Math.round(refFrac * iw);

    // ratio 來源：優先 Gemini 報告，fallback 像素比例
    let ratio = f.trunkToReferenceRatio || 0;
    let ratioSource = 'gemini';
    if (!(ratio > 0) && trunkPx > 0 && refPx > 0) {
      ratio = trunkPx / refPx;
      ratioSource = 'pixel';
    }

    let dbhCm = null;
    if (ratio > 0 && refSize) {
      dbhCm = Math.round(ratio * refSize.width / 10 * 10) / 10;
      if (dbhCm < 1 || dbhCm > 200) dbhCm = null; // sanity
    }

    console.log(`  frame[${i}] type=${refType} atTrunk=${f.referenceAtTrunk} conf=${f.referenceConfidence}`);
    console.log(`    trunkFrac=${trunkFrac} refFrac=${refFrac} ratio=${ratio.toFixed(3)}(${ratioSource}) → DBH=${dbhCm ?? 'reject'}cm`);

    if (dbhCm && f.referenceAtTrunk !== false) {
      candidates.push({ dbhCm, refType, ratio, ratioSource, conf: f.referenceConfidence || 0 });
    }
  });

  if (candidates.length > 0) {
    // 優先 creditcard，其次 conf 高的
    candidates.sort((a, b) => {
      if (a.refType === 'creditcard' && b.refType !== 'creditcard') return -1;
      if (b.refType === 'creditcard' && a.refType !== 'creditcard') return 1;
      return b.conf - a.conf;
    });
    const best = candidates[0];
    console.log(`  ✅ 可恢復: DBH=${best.dbhCm}cm (${best.refType}, ratio=${best.ratio.toFixed(2)}, source=${best.ratioSource}, conf=${best.conf})`);
    recoverable++;
  } else {
    console.log('  ❌ 無可用 reference 幀');
  }
});

console.log(`\n== 結果：${recoverable}/${total} 棵可從 rawFrames 恢復 pathA ==`);
