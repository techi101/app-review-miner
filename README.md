# App Review Miner

Pulls recent Google Play reviews for an app, tags the 1 and 2 star ones by complaint theme (English, Hinglish and some Hindi keywords), and turns the numbers into a one page product brief.

First case study: the Delhivery consumer app (`com.delhiveryConsigneeApp`), 7,000 newest reviews from 17 Sep to 12 Nov 2026.

## What it found (Delhivery)

| Finding | Number |
|---|---|
| Reviews in the window that are 1 or 2 star | 41% (vs 20% across all 453,920 lifetime ratings) |
| 1-2 star reviews about delays or parcels stuck at a hub | 35.4% |
| Say the parcel was marked "customer unavailable" without a real call | 15.2% (421 reviews) |
| Could not reach a human (bot replies, dead numbers) | 12.1% |
| Marked unavailable and the agent then did not answer | 64 reviews |
| Median delay people quote | 5 days |

Brief with the proposed fix: [Delhivery_Review_Brief_1.pdf](Delhivery_Review_Brief_1.pdf). Summary numbers: [data/delhivery_summary.json](data/delhivery_summary.json).

## Proposed fix

1. **Proof of attempt:** the agent app can set "customer unavailable" only after a masked call that rang at least 20 seconds and a GPS ping near the address. Otherwise the parcel is re-queued.
2. **One tap "I was available":** a dispute link in the SMS and tracking page that books a priority re-attempt and counts toward that agent's false attempt rate.
3. **Human after two bot loops:** hand off when the same shipment is raised twice or is stuck more than 3 days.

## Run it

```
pip install google-play-scraper pandas matplotlib
python fetch.py com.delhiveryConsigneeApp 7000 data/delhivery.csv
python analyze.py data/delhivery.csv Delhivery
python report.py
```

`report.py` prints the PDF with headless Microsoft Edge.

## Limits

- Newest reviews from the English India listing, so recent but not a random sample of all users.
- Themes are keyword rules. A hand check of 30 reviews tagged "unavailable" found about 25 correct (~83%).
- Identical complaint texts posted by several accounts are counted once.
- Review text is the customer's account, not verified delivery data. Real rates would come from Delhivery's attempt logs.
- Raw review CSVs are not committed; `fetch.py` pulls them again.
