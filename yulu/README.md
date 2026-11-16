# Yulu: what 1 and 2 star Play Store reviews say (16 May to 15 Nov 2026)

I wrote a small script to pull the 5,000 newest Google Play reviews of the Yulu app (`app.yulu.bike`, India listing) and kept the last six months: 588 reviews, 312 of them 1 or 2 star. Each low review is tagged by keyword rules (English and Hinglish) and joined to the app version it was written on.

## What stands out

| Finding | Number |
|---|---|
| Reviews in the window that are 1 or 2 star | 53% (vs 15% across all 152,567 lifetime ratings) |
| Low reviews about plans, prices, penalties or extra charges | 22% (69) |
| Low reviews complaining about customer support (chat bot, no reply, no call back) | 18% (56) |
| Low reviews about batteries (swap, range, dead battery) | 15% (48) |
| Low reviews about refunds, deposits or wallet money | 13.5% (42), up from 10% in June to 13 to 18% a month from July to October |
| 1 and 2 star share on app version 4.6.2 vs 4.6.1 | 42% vs 68% (273 and 171 reviews) |
| Low reviews with a reply from Yulu | 34% |

So the newer build looks better, and the biggest complaints are about money: charges and penalties, deposits that do not come back, and nobody to talk to about it.

## If I were building the data side of this

1. A daily job that pulls new reviews, dedupes by review id, tags themes and writes them to a table keyed by date and app version.
2. Quality checks on every load: duplicate ids, empty text, unknown version share, row count against the previous day.
3. An alert when a theme's share of low reviews jumps (for example refund and deposit complaints in a week vs the 8 week average), so ops sees it before the rating does.
4. Join to internal refund and support ticket tables to check whether review spikes match real refund delays.

## Limits

- Newest reviews from the English India listing, so recent but not a random sample of riders.
- Themes are keyword rules. A hand check of 20 battery tagged reviews found 16 correct (about 80%); "charging" sometimes means price, not battery.
- May and November are partial months (24 and 17 low reviews).

## Run it

```
python fetch.py app.yulu.bike 5000 data/yulu.csv
python yulu/analyze_yulu.py
```

Outputs: `yulu/yulu_summary.json`, `yulu/themes_by_month.csv`, `yulu/by_version.csv`.
