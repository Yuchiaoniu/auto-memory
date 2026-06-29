.headers on
.mode column
.width 14 16 7 7 7 10 10 10 6
SELECT '=== 抽樣驗證 5 筆 ===' AS info;
SELECT substr(id,1,8) AS tree_id, video_original_name AS orig,
       manual_tape_circ_cm AS circ, manual_tape_dbh_cm AS dbh,
       manual_tape_frame_ts_sec AS ts, ROUND(path0_dbh_cm,1) AS p0_old,
       ROUND(pathA_dbh_cm,1) AS pA, ROUND(pathB_dbh_cm,1) AS pB, species
FROM trees
WHERE video_original_name IN ('IMG_5786.mov','IMG_5805.mov','IMG_5806.mov','IMG_5807.mov','IMG_5817.mov')
ORDER BY video_original_name;
SELECT '' AS sep;
SELECT '=== Metadata audit: 31 棵的填寫率 ===' AS info;
SELECT
  SUM(CASE WHEN gps IS NOT NULL AND gps != '' THEN 1 ELSE 0 END) AS gps,
  SUM(CASE WHEN focal_length_mm IS NOT NULL AND focal_length_mm > 0 THEN 1 ELSE 0 END) AS focal,
  SUM(CASE WHEN sensor_width_mm IS NOT NULL AND sensor_width_mm > 0 THEN 1 ELSE 0 END) AS sensor,
  SUM(CASE WHEN device_model IS NOT NULL AND device_model != '' THEN 1 ELSE 0 END) AS device,
  SUM(CASE WHEN illuminance_lux IS NOT NULL THEN 1 ELSE 0 END) AS lux,
  SUM(CASE WHEN altitude_m IS NOT NULL THEN 1 ELSE 0 END) AS alt,
  SUM(CASE WHEN duration_sec IS NOT NULL AND duration_sec > 0 THEN 1 ELSE 0 END) AS dur,
  SUM(CASE WHEN species IS NOT NULL AND species != '' THEN 1 ELSE 0 END) AS species,
  SUM(CASE WHEN pathA_dbh_cm IS NOT NULL THEN 1 ELSE 0 END) AS has_pA,
  SUM(CASE WHEN pathB_dbh_cm IS NOT NULL THEN 1 ELSE 0 END) AS has_pB,
  COUNT(*) AS total
FROM trees;
SELECT '' AS sep;
SELECT '=== 物種分布 ===' AS info;
SELECT species, COUNT(*) AS n FROM trees GROUP BY species ORDER BY n DESC;
