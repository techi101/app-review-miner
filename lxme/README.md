# LXME case study (small)

The 5,000 newest Google Play reviews of LXME (4,986 after removing repeated identical texts) (`com.lxme`), 4 Sep 2023 to 26 Nov 2026, loaded into SQLite and tagged with plain SQL (`themes.sql`). LXME has few reviews (7,236 ratings in total), so 1, 2 and 3 star reviews (382) count as unhappy here.

## What it shows

| Theme among unhappy reviews | Reviews |
|---|---|
| Slow, buggy or not working | 43 |
| Rewards: gold or coins could not be claimed | 37 |
| Cannot get in: login, OTP, "account not active" | 26 |
| UPI failures | 20 |
| Men who installed for an offer and found it is women-only | 11 |

- **Stuck before first use:** 40 unhappy reviewers never got past login, device checks or KYC. 49 got in and then hit rewards, UPI or money-out problems.
- **Reward-led installs bring in people who cannot use the offer.** Several reviews come from men who installed for the gold reward and were told only women can claim it. One review says: first open an account, then invest, and only then that gold is for women only.

## What I would test

Show who can claim the gold reward on the offer card and the first screen, before signup. Measure: share of new installs that reach a first investment, and 1-star reviews that mention rewards, against the current flow.

## Limits

Small sample, keyword rules, and the hand check was rough (about 9 of 14 "rewards" tags were real reward complaints). Review text is the user's account, not LXME data. Not affiliated with LXME.

Run: `python ../fetch.py com.lxme 5000 ../data/lxme.csv && python run_sql.py`
