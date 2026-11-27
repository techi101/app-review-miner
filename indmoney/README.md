# INDmoney case study

6,000 newest Google Play reviews of INDmoney (`in.indwealth`), 12 Sep 2025 to 26 Nov 2026, loaded into SQLite and analysed with plain SQL.

**Brief:** [INDmoney_Review_Brief_1.pdf](INDmoney_Review_Brief_1.pdf)

## What it found

- **3 Nov 2026 outage:** 45 of the day's 57 reviews were 1 or 2 stars; 29 say the app hung or threw errors during market hours ("not working today at 9:16am", "not working on expiry"). That one day made November the worst month in the window: 41 of 96 low reviews are crash/error complaints, against 4 to 17 in a typical month.
- **Recurring themes** among 1,235 low reviews: crash or error 183, support cannot fix it 173, money stuck or not reflected 133, charges 110, KYC and bank linking 81, pushy cross-sell 42.
- 38 of 133 "money stuck" reviews also say support could not fix it; 30 are about US-stock deposits or withdrawals.

## Proposals in the brief

A. An exit-only mode for outage mornings, plus a pre-filled claim form after an incident.
B. A "where is my money" tracker for US transfers, with an A/B test design (metric, guardrails, rough sample size).

## Run it

```
python ../fetch.py in.indwealth 6000 ../data/indmoney.csv
python run_sql.py          # loads SQLite, runs themes.sql, prints every result
python build_brief.py      # writes the HTML and PDF brief from the database
```

## Limits

- Newest reviews from the English India listing, so they skew negative (21% are 1-2 star here vs about 5% of all-time ratings).
- Themes are keyword rules (`themes.sql`). I read all 41 November crash/error tags: the 29 on 3 Nov are real outage complaints. A random sample of 15 "money stuck" tags had about 11 correct.
- Review text is the customer's account, not INDmoney's logs. Not affiliated with INDmoney.
