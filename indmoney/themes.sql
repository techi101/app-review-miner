-- INDmoney Play Store reviews: complaint themes in SQL (SQLite).
-- reviews(id, date, score, version, thumbs, replied, text, reply) is loaded by run_sql.py.
-- Low = 1 or 2 stars. Each theme is a set of LIKE rules on lower-cased text; one review can hit several themes.

DROP VIEW IF EXISTS low;
CREATE VIEW low AS
SELECT id, date, substr(date,1,7) AS month, score, version, thumbs, replied, lower(text) AS t
FROM reviews WHERE score <= 2;

DROP TABLE IF EXISTS tags;
CREATE TABLE tags AS
SELECT id, month, thumbs,
  -- money debited / deposited / withdrawn but not reflected
  (t LIKE '%stuck%' OR t LIKE '%not reflect%' OR t LIKE '%not credited%' OR t LIKE '%pending%'
   OR t LIKE '%deducted%' OR t LIKE '%debited%' OR t LIKE '%withdraw%' OR t LIKE '%refund%'
   OR t LIKE '%froze%' OR t LIKE '%frozen%' OR t LIKE '%freeze%' OR t LIKE '%add fund%' OR t LIKE '%added fund%'
   OR t LIKE '%swift%' OR t LIKE '%paisa%' OR t LIKE '%money not%') AS money_stuck,
  -- support cannot be reached or closes tickets without fixing
  (t LIKE '%customer care%' OR t LIKE '%customer support%' OR t LIKE '%customer service%' OR t LIKE '%support team%'
   OR t LIKE '%ticket%' OR t LIKE '%no response%' OR t LIKE '%not respond%' OR t LIKE '%no reply%'
   OR t LIKE '%call back%' OR t LIKE '%callback%' OR t LIKE '%will call%' OR t LIKE '%agent%' OR t LIKE '%chat support%') AS support,
  -- app crashes or freezes, especially while trading
  (t LIKE '%crash%' OR t LIKE '%hang%' OR t LIKE '%not working%' OR t LIKE '%server%' OR t LIKE '%glitch%'
   OR t LIKE '%bug%' OR t LIKE '%error%' OR t LIKE '%unable to exit%' OR t LIKE '%could not exit%' OR t LIKE '%stop loss%' OR t LIKE '%stoploss%' OR t LIKE '%stop-loss%') AS crash_or_error,
  -- trading loss blamed on the app
  ((t LIKE '%loss%' OR t LIKE '%lost%') AND (t LIKE '%crash%' OR t LIKE '%server%' OR t LIKE '%exit%' OR t LIKE '%technical%' OR t LIKE '%glitch%' OR t LIKE '%stop%')) AS loss_from_outage,
  -- KYC, bank linking, account activation loops
  (t LIKE '%kyc%' OR t LIKE '%aadhaar%' OR t LIKE '%aadhar%' OR t LIKE '%verification%' OR t LIKE '%bank statement%'
   OR t LIKE '%activation%' OR t LIKE '%account opening%' OR t LIKE '%add my bank%' OR t LIKE '%federal bank%') AS kyc_onboarding,
  -- cross-sell, calls, permissions, pre-selected add-ons
  (t LIKE '%insurance%' OR t LIKE '%spam%' OR t LIKE '%promot%' OR t LIKE '%daily call%' OR t LIKE '%calls%'
   OR t LIKE '%permission%' OR t LIKE '%pre-selected%' OR t LIKE '%preselected%' OR t LIKE '%dark pattern%' OR t LIKE '%instant cash%' OR t LIKE '%pay later%') AS pushy_crosssell,
  -- charges and hidden fees
  (t LIKE '%charge%' OR t LIKE '%hidden%' OR t LIKE '%brokerage%' OR t LIKE '%fee%' OR t LIKE '%forex%' OR t LIKE '%markup%') AS charges,
  -- new UI / redesign complaints
  (t LIKE '%new ui%' OR t LIKE '%new update%' OR t LIKE '%new version%' OR t LIKE '%old version%' OR t LIKE '%interface%'
   OR t LIKE '%cluttered%' OR t LIKE '%dashboard%' OR t LIKE '%ui %') AS ui_change
FROM low;

-- 1. Theme share among low reviews, and how many people agreed (thumbs up)
SELECT 'money_stuck' AS theme, SUM(money_stuck) AS n, ROUND(100.0*SUM(money_stuck)/COUNT(*),1) AS pct_low, SUM(money_stuck*thumbs) AS thumbs FROM tags
UNION ALL SELECT 'support', SUM(support), ROUND(100.0*SUM(support)/COUNT(*),1), SUM(support*thumbs) FROM tags
UNION ALL SELECT 'crash_or_error', SUM(crash_or_error), ROUND(100.0*SUM(crash_or_error)/COUNT(*),1), SUM(crash_or_error*thumbs) FROM tags
UNION ALL SELECT 'loss_from_outage', SUM(loss_from_outage), ROUND(100.0*SUM(loss_from_outage)/COUNT(*),1), SUM(loss_from_outage*thumbs) FROM tags
UNION ALL SELECT 'kyc_onboarding', SUM(kyc_onboarding), ROUND(100.0*SUM(kyc_onboarding)/COUNT(*),1), SUM(kyc_onboarding*thumbs) FROM tags
UNION ALL SELECT 'pushy_crosssell', SUM(pushy_crosssell), ROUND(100.0*SUM(pushy_crosssell)/COUNT(*),1), SUM(pushy_crosssell*thumbs) FROM tags
UNION ALL SELECT 'charges', SUM(charges), ROUND(100.0*SUM(charges)/COUNT(*),1), SUM(charges*thumbs) FROM tags
UNION ALL SELECT 'ui_change', SUM(ui_change), ROUND(100.0*SUM(ui_change)/COUNT(*),1), SUM(ui_change*thumbs) FROM tags
ORDER BY n DESC;

-- 2. The combination that matters: money stuck AND support could not fix it
SELECT COUNT(*) AS low_reviews, SUM(money_stuck AND support) AS stuck_and_support,
       ROUND(100.0*SUM(money_stuck AND support)/COUNT(*),1) AS pct_low,
       ROUND(100.0*SUM(money_stuck AND support)/NULLIF(SUM(money_stuck),0),1) AS pct_of_money_stuck
FROM tags;

-- 3. Monthly trend of low reviews and the top two themes
SELECT month, COUNT(*) AS low_reviews, SUM(money_stuck) AS money_stuck, SUM(support) AS support
FROM tags GROUP BY month ORDER BY month;

-- 4. Share of all reviews that are 1-2 star, per month (volume check)
SELECT substr(date,1,7) AS month, COUNT(*) AS all_reviews, ROUND(100.0*SUM(score<=2)/COUNT(*),1) AS pct_low
FROM reviews GROUP BY month ORDER BY month;

-- 5. Did the company reply? Reply rate on low reviews by theme
SELECT 'money_stuck' AS theme, ROUND(100.0*AVG(r.replied),1) AS reply_pct FROM tags g JOIN reviews r USING(id) WHERE g.money_stuck
UNION ALL SELECT 'support', ROUND(100.0*AVG(r.replied),1) FROM tags g JOIN reviews r USING(id) WHERE g.support
UNION ALL SELECT 'all_low', ROUND(100.0*AVG(r.replied),1) FROM tags g JOIN reviews r USING(id);

-- 6. Crash/error complaints by month, and how many name market hours, expiry, or a time like 9:15
SELECT g.month, COUNT(*) AS low_reviews, SUM(g.crash_or_error) AS crash_or_error,
       ROUND(100.0*SUM(g.crash_or_error)/COUNT(*),1) AS pct_low,
       SUM(g.crash_or_error AND (l.t LIKE '%market hour%' OR l.t LIKE '%market time%' OR l.t LIKE '%live market%' OR l.t LIKE '%expiry%'
            OR l.t LIKE '%9:1%' OR l.t LIKE '%9.1%' OR l.t LIKE '%market open%' OR l.t LIKE '%intraday%' OR l.t LIKE '%exit%')) AS during_trading
FROM tags g JOIN low l USING(id) GROUP BY g.month ORDER BY g.month;

-- 7. Busiest days for crash/error complaints (finds single-day outages)
SELECT r.date, COUNT(*) AS all_reviews, SUM(r.score<=2) AS low, SUM(COALESCE(g.crash_or_error,0)) AS crash_or_error
FROM reviews r LEFT JOIN tags g USING(id) GROUP BY r.date ORDER BY crash_or_error DESC, low DESC LIMIT 6;
