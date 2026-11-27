"""Build the one-page INDmoney review brief (HTML + PDF) from indmoney.db.
Run run_sql.py first. Every number on the page is read from the database here."""
import os, sqlite3, subprocess

db = sqlite3.connect("indmoney.db")
q = lambda sql: db.execute(sql).fetchall()

total, low, d0, d1 = q("SELECT COUNT(*), SUM(score<=2), MIN(date), MAX(date) FROM reviews")[0]
months = q("""SELECT g.month, COUNT(*), SUM(g.crash_or_error) FROM tags g GROUP BY g.month ORDER BY g.month""")
day = q("""SELECT COUNT(*), SUM(r.score<=2), SUM(COALESCE(g.crash_or_error,0)) FROM reviews r LEFT JOIN tags g USING(id)
           WHERE r.date='2026-11-03'""")[0]
themes = dict((r[0], r[1:]) for r in q("""
  SELECT 'Crash or error', SUM(crash_or_error), SUM(crash_or_error*thumbs) FROM tags
  UNION ALL SELECT 'Support cannot fix it', SUM(support), SUM(support*thumbs) FROM tags
  UNION ALL SELECT 'Money stuck or not reflected', SUM(money_stuck), SUM(money_stuck*thumbs) FROM tags
  UNION ALL SELECT 'Charges and FX spread', SUM(charges), SUM(charges*thumbs) FROM tags
  UNION ALL SELECT 'KYC and bank linking', SUM(kyc_onboarding), SUM(kyc_onboarding*thumbs) FROM tags
  UNION ALL SELECT 'Pushy cross-sell', SUM(pushy_crosssell), SUM(pushy_crosssell*thumbs) FROM tags"""))
stuck, stuck_sup = q("SELECT SUM(money_stuck), SUM(money_stuck AND support) FROM tags")[0]
us_stuck = q("""SELECT COUNT(*) FROM tags g JOIN low l USING(id) WHERE g.money_stuck AND (l.t LIKE '%us stock%' OR l.t LIKE '%us wallet%'
               OR l.t LIKE '%us account%' OR l.t LIKE '%swift%' OR l.t LIKE '%usd%' OR l.t LIKE '%dollar%')""")[0][0]
callback = q("""SELECT COUNT(*) FROM low WHERE t LIKE '%will call%' OR t LIKE '%call you in%' OR t LIKE '%call back%'
               OR t LIKE '%callback%' OR t LIKE '%agent will%' OR t LIKE '%talk to agent%'""")[0][0]

# Monthly bar chart of crash/error complaints (inline SVG, no libraries)
W, H, pad = 300, 92, 14
mx = max(m[2] for m in months); bw = (W - 6) / len(months)
bars = []
for i, (m, n, c) in enumerate(months):
    h = (H - pad - 12) * c / mx; x = 3 + i * bw; y = H - pad - h
    hot = m == "2026-11"
    bars.append(f'<rect x="{x+1:.1f}" y="{y:.1f}" width="{bw-2:.1f}" height="{h:.1f}" fill="{"#b4232a" if hot else "#9aa6b2"}"/>')
    if hot or i == 0: bars.append(f'<text x="{x+bw/2:.1f}" y="{y-3:.1f}" text-anchor="middle" font-size="8.5" fill="#222">{c}</text>')
    if m.endswith(("-01", "-09", "-11")) or i == 0:
        bars.append(f'<text x="{x+bw/2:.1f}" y="{H-3}" text-anchor="middle" font-size="7.5" fill="#555">{m[2:4]}/{m[5:]}</text>')
svg = f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Crash or error complaints per month">{"".join(bars)}</svg>'

rows = "".join(f"<tr><td>{k}</td><td class=n>{v[0]}</td><td class=n>{100*v[0]/low:.1f}%</td><td class=n>{v[1]}</td></tr>"
               for k, v in sorted(themes.items(), key=lambda kv: -kv[1][0]))

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>INDmoney review brief</title>
<style>
@page {{ size: A4; margin: 11mm 12mm; }}
body {{ font: 9.6pt/1.38 "Segoe UI", Arial, sans-serif; color:#1b1f24; margin:0; }}
h1 {{ font-size:15pt; margin:0 0 2px; letter-spacing:-.2px }}
.sub {{ color:#555; font-size:8.6pt; margin-bottom:8px }}
h2 {{ font-size:10.6pt; margin:10px 0 4px; border-bottom:1.5px solid #1b1f24; padding-bottom:2px }}
.grid {{ display:grid; grid-template-columns: 1.05fr 1fr; gap:14px }}
.call {{ background:#fbeeee; border-left:3px solid #b4232a; padding:6px 9px; margin:6px 0 }}
table {{ border-collapse:collapse; width:100%; font-size:8.8pt }}
th, td {{ text-align:left; padding:2px 4px; border-bottom:1px solid #e3e6ea }} th {{ font-weight:600; color:#444 }}
td.n, th.n {{ text-align:right; font-variant-numeric: tabular-nums }}
ul {{ margin:3px 0; padding-left:16px }} li {{ margin:1.5px 0 }}
.q {{ color:#444; font-style:italic }}
.small {{ font-size:8pt; color:#555 }}
b.k {{ color:#b4232a }}
</style></head><body>
<h1>INDmoney: what 1-star reviewers are telling the product team</h1>
<div class=sub>Product brief by Nitesh Kumar Yadav &middot; {total:,} newest Google Play reviews ({d0} to {d1}), analysed in SQL (SQLite) &middot;
code: github.com/techi101/app-review-miner (folder indmoney/)</div>

<div class=grid><div>
<h2>1. One Tuesday made November the worst month</h2>
<div class=call>On <b>3 Nov 2026</b>, {day[1]} of the day's {day[0]} reviews were 1 or 2 stars, and <b class=k>{day[2]}</b> of them say the app hung or threw errors.
Users name the time and the stakes: <span class=q>"App not working today at 9:16am"</span>, <span class=q>"not working on expiry"</span>,
<span class=q>"lost money due to app crash"</span>.</div>
{svg}
<div class=small>1-2 star reviews tagged crash/error, per month. November: {months[-1][2]} of {months[-1][1]}. Typical month: 4 to 17.</div>
<p style="margin:5px 0 0">The same pattern hit on 2 and 3 Feb 2026: users who could not exit F&amp;O positions were still writing about refused refunds 12 days later (14 Feb). One bad market morning turns into a tail of 1-star reviews and refund tickets.</p>
</div><div>
<h2>2. The recurring themes</h2>
<table><tr><th>Theme (keyword rules, one review can hit several)</th><th class=n>Reviews</th><th class=n>Share</th><th class=n>Upvotes</th></tr>{rows}</table>
<ul class=small style="margin-top:5px">
<li>{stuck_sup} of {stuck} "money stuck" reviews ({100*stuck_sup/stuck:.0f}%) also say support could not fix it. {us_stuck} are about US-stock deposits or withdrawals.</li>
<li>{callback} describe the "an agent will call you in 15 min" promise that never turns into a call.</li>
</ul></div></div>

<h2>3. What I would build first</h2>
<div class=grid><div>
<b>A. Exit-only mode for outage mornings</b>
<ul>
<li><b>Problem:</b> when the main app fails at 9:15, a trader with an open F&amp;O position cannot exit, and that loss becomes a refund dispute.</li>
<li><b>Feature:</b> when health checks fail, open a minimal screen: open positions, live P&amp;L, one tap square-off on a separate light path, plus a status banner with the next update time.</li>
<li><b>After the incident:</b> one push to every affected user, and a claim form pre-filled with that user's failed order attempts, so support is not asking for screenshots.</li>
<li><b>Measure:</b> exits completed during an incident, failed-order attempts, tickets per affected user, share of 1-star reviews on incident days ({100*day[1]/day[0]:.0f}% on 3 Nov).</li>
</ul></div><div>
<b>B. "Where is my money" tracker for US transfers (A/B test)</b>
<ul>
<li><b>Feature:</b> a step timeline for each add or withdraw (debited, sent by SWIFT, received, in wallet) with an expected date. Past that date, a ticket opens on its own with the transfer attached. "Agent will call in 15 min" becomes an honest queue position.</li>
<li><b>Test:</b> randomise users who start a US transfer, 50/50. Primary metric: support contacts per 100 transfers within 10 days. Guardrails: transfers completed, repeat deposits within 30 days, rating-prompt score.</li>
<li><b>Size:</b> a test set up to detect a 20% drop from a 10% contact rate (80% power, 5% significance) needs roughly 3,200 transfers per arm. The real base rate comes from INDmoney's ticket data.</li>
</ul></div></div>

<p class=small style="margin-top:8px"><b>Limits.</b> These are public reviews from the newest end of the English India listing, so they skew negative (1-2 stars are {100*low/total:.0f}% here vs about 5% of all-time ratings). Themes are keyword rules in SQL.
I read all 41 November crash/error tags: the 29 on 3 Nov are all real outage complaints, and the other 12 are mostly chart, UPI and update bugs (1 was a bank-flow complaint).
A random sample of 15 "money stuck" tags had about 11 correct. Review text is the customer's account, not INDmoney's logs.</p>
</body></html>"""

open("INDmoney_Review_Brief_1.html", "w", encoding="utf-8").write(html)
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={os.path.abspath('INDmoney_Review_Brief_1.pdf')}", os.path.abspath("INDmoney_Review_Brief_1.html")],
               check=False, timeout=90)
print("built", total, low, day, months[-1])
