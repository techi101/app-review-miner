-- LXME Play Store reviews: where users get stuck, in SQL (SQLite). 1-3 stars count as unhappy here because the app has few reviews.
DROP VIEW IF EXISTS low;
CREATE VIEW low AS SELECT id, date, substr(date,1,7) AS month, score, thumbs, lower(text) AS t FROM reviews WHERE score <= 3;

DROP TABLE IF EXISTS tags;
CREATE TABLE tags AS SELECT id, month, score,
 (t LIKE '%login%' OR t LIKE '%log in%' OR t LIKE '%otp%' OR t LIKE '%not active%' OR t LIKE '%inactive%' OR t LIKE '%verify mobile%' OR t LIKE '%password%' OR t LIKE '%sign up%' OR t LIKE '%signup%' OR t LIKE '%keeps loading%' OR t LIKE '%not open%' OR t LIKE '%can''t open%' OR t LIKE '%unable to open%') AS cannot_get_in,
 (t LIKE '%root%' OR t LIKE '%security risk%' OR t LIKE '%accessibility%' OR t LIKE '%developer option%' OR t LIKE '%permission%' OR t LIKE '%secure%device%') AS device_block,
 (t LIKE '%reward%' OR t LIKE '%gold%' OR t LIKE '%coin%' OR t LIKE '%cashback%' OR t LIKE '%claim%' OR t LIKE '%offer%' OR t LIKE '%redeem%') AS rewards,
 (t LIKE '%upi%') AS upi,
 (t LIKE '%withdraw%' OR t LIKE '%money stuck%' OR t LIKE '%stuck%' OR t LIKE '%not credited%' OR t LIKE '%deducted%' OR t LIKE '%sell%') AS money_out,
 (t LIKE '%kyc%' OR t LIKE '%bank account%' OR t LIKE '%aadhaar%' OR t LIKE '%aadhar%' OR t LIKE '%pan %') AS kyc_bank,
 (t LIKE '%male%' OR t LIKE '% men %' OR t LIKE '%not woman%' OR t LIKE '%only for women%' OR t LIKE '%only for female%' OR t LIKE '%guys%') AS men_excluded,
 (t LIKE '%slow%' OR t LIKE '%bug%' OR t LIKE '%crash%' OR t LIKE '%hang%' OR t LIKE '%not working%' OR t LIKE '%error%') AS slow_or_buggy
FROM low;

-- 1. Themes among unhappy reviews
SELECT 'cannot_get_in' AS theme, SUM(cannot_get_in) n, ROUND(100.0*SUM(cannot_get_in)/COUNT(*),1) pct FROM tags
UNION ALL SELECT 'device_block', SUM(device_block), ROUND(100.0*SUM(device_block)/COUNT(*),1) FROM tags
UNION ALL SELECT 'rewards', SUM(rewards), ROUND(100.0*SUM(rewards)/COUNT(*),1) FROM tags
UNION ALL SELECT 'upi', SUM(upi), ROUND(100.0*SUM(upi)/COUNT(*),1) FROM tags
UNION ALL SELECT 'money_out', SUM(money_out), ROUND(100.0*SUM(money_out)/COUNT(*),1) FROM tags
UNION ALL SELECT 'kyc_bank', SUM(kyc_bank), ROUND(100.0*SUM(kyc_bank)/COUNT(*),1) FROM tags
UNION ALL SELECT 'men_excluded', SUM(men_excluded), ROUND(100.0*SUM(men_excluded)/COUNT(*),1) FROM tags
UNION ALL SELECT 'slow_or_buggy', SUM(slow_or_buggy), ROUND(100.0*SUM(slow_or_buggy)/COUNT(*),1) FROM tags
ORDER BY n DESC;

-- 2. Funnel stage: stuck before first use (cannot get in, device block, KYC) vs after (rewards, UPI, money out)
SELECT SUM(cannot_get_in OR device_block OR kyc_bank) AS before_first_use,
       SUM((rewards OR upi OR money_out) AND NOT (cannot_get_in OR device_block OR kyc_bank)) AS after_first_use,
       COUNT(*) AS unhappy FROM tags;

-- 3. Review volume and unhappy share by month (last 15 months)
SELECT substr(date,1,7) AS month, COUNT(*) AS reviews, SUM(score<=3) AS unhappy, ROUND(100.0*SUM(score<=3)/COUNT(*),1) AS pct_unhappy,
       ROUND(AVG(length(text)),0) AS avg_chars
FROM reviews WHERE date >= '2025-09-01' GROUP BY month ORDER BY month;
