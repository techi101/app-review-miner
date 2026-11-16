"""Yulu Play Store reviews: complaint themes by month and by app version (keyword rules, English + Hinglish)."""
import re, json, warnings, pandas as pd
warnings.filterwarnings('ignore')
d = pd.read_csv('data/yulu.csv', parse_dates=['date'])
d['text'] = d['text'].fillna('').astype(str)
before = len(d); d = d.drop_duplicates('id'); 
d['low'] = d.score <= 2
T = {
 'refund_deposit_wallet': r'refund|deposit|wallet|money (is )?(stuck|locked|not)|paisa|paise|security amount|refond|reufnd',
 'support_no_human': r'support|customer care|care cent|chat ?bot|executive|no response|not respond|no reply|call (nahi|not)|helpline',
 'unlock_qr_app_bug': r'unlock|qr|scan|white screen|crash|stuck|not (able|working)|otp|login|lag|update|server',
 'battery_range': r'batt?e?ry|battry|batteries|discharg|charging|swap|range',
 'vehicle_fault': r'fault|damage|brake|puncture|tyre|tire|stopped|break ?down|broke|wheel',
 'plan_pricing': r'plan|price|pricing|expens|costly|unlimited|227|charged|charges|penalt|fine|recharge|rent',
 'kyc_verification': r'kyc|verif|aadhaar|aadhar|licen[cs]e|govt\.? id|document',
}
for k, p in T.items():
    d[k] = d.text.str.lower().str.contains(p, regex=True)
win = d[d.date >= '2026-05-16']
low = win[win.low]
out = {'fetched': before, 'window': f"{win.date.min().date()} to {win.date.max().date()}", 'reviews_in_window': len(win),
       'low_share_in_window': round(win.low.mean(), 3), 'low_reviews': len(low),
       'theme_share_of_low': {k: round(low[k].mean(), 3) for k in T},
       'theme_counts_low': {k: int(low[k].sum()) for k in T},
       'yulu_replied_share_low': round(low.replied.mean(), 3)}
m = low.assign(month=low.date.dt.to_period('M').astype(str)).groupby('month')[list(T)].mean().round(3)
v = win.assign(ver=win.version.fillna('unknown').astype(str).str.extract(r'^(\d+\.\d+\.\d+)')[0].fillna('unknown'))
vt = v.groupby('ver').agg(n=('id','size'), low_share=('low','mean'), unlock_bug_share=('unlock_qr_app_bug', 'mean')).query('n>=40').round(3)
print(json.dumps(out, indent=1)); print(m.to_string()); print(vt.sort_index().to_string())
json.dump(out, open('yulu/yulu_summary.json', 'w'), indent=1)
m.to_csv('yulu/themes_by_month.csv'); vt.to_csv('yulu/by_version.csv')
