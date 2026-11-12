"""Build a one-page HTML/PDF brief from the tagged Delhivery reviews."""
import json, base64, io, subprocess, os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

S = json.load(open("data/delhivery_summary.json"))
LIFETIME = {"ratings": 453920, "one_two": 83171 + 7096}
names = {"delay_stuck": "Parcel delayed / stuck at hub", "false_unavailable": "Marked 'customer unavailable' / fake attempt",
         "no_human_support": "Can't reach a human (bot loop, no number)", "agent_unreachable": "Delivery agent not answering",
         "damaged_wrong_lost": "Damaged, wrong or lost item", "rude_or_collect_yourself": "Rude agent / 'collect it from hub'",
         "money_extra_refund": "Extra charge or refund issue", "app_tracking_bug": "App or tracking bug", "pickup_return_failed": "Pickup or return failed"}
th = sorted(S["themes"].items(), key=lambda kv: kv[1]["pct"])

fig, ax = plt.subplots(figsize=(6.4, 3.0), dpi=160)
ax.barh([names[k] for k, _ in th], [v["pct"] for _, v in th], color=["#c2410c" if k == "false_unavailable" else "#94a3b8" for k, _ in th])
for i, (_, v) in enumerate(th):
    ax.text(v["pct"] + 0.5, i, f'{v["pct"]}%  ({v["n"]})', va="center", fontsize=7)
ax.set_xlabel("% of 1-2 star reviews mentioning it (a review can have several)", fontsize=7)
ax.tick_params(labelsize=7); ax.spines[["top", "right"]].set_visible(False); ax.set_xlim(0, 42)
plt.tight_layout(); buf = io.BytesIO(); plt.savefig(buf, format="png"); chart = base64.b64encode(buf.getvalue()).decode()

recent = S["share_negative"] * 100
life = 100 * LIFETIME["one_two"] / LIFETIME["ratings"]
fu = S["themes"]["false_unavailable"]

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Delhivery app reviews: what 1-star users say</title>
<style>
@page {{ size: A4; margin: 14mm 15mm; }}
body {{ font-family: Segoe UI, Arial, sans-serif; color:#0f172a; font-size:10.2px; line-height:1.42; margin:0; }}
h1 {{ font-size:17px; margin:0 0 2px; }} h2 {{ font-size:11.5px; margin:12px 0 4px; color:#c2410c; }}
.sub {{ color:#475569; font-size:9.5px; margin-bottom:8px; }}
.kpis {{ display:flex; gap:8px; margin:8px 0; }} .k {{ flex:1; border:1px solid #e2e8f0; border-radius:6px; padding:6px 8px; }}
.k b {{ font-size:15px; display:block; }} .k span {{ color:#475569; font-size:8.8px; }}
ul {{ margin:2px 0 0 16px; padding:0; }} li {{ margin:2px 0; }}
table {{ border-collapse:collapse; width:100%; font-size:9.3px; }} td,th {{ border:1px solid #e2e8f0; padding:3px 5px; text-align:left; vertical-align:top; }}
th {{ background:#f8fafc; }} .q {{ color:#334155; font-style:italic; }} .foot {{ color:#64748b; font-size:8.3px; margin-top:8px; }}
</style></head><body>
<h1>Delhivery app: what the last 8 weeks of 1-star reviews say, and one fix</h1>
<div class="sub">Nitesh Kumar Yadav, B.Tech ECE (AI &amp; ML), NSUT Delhi &middot; 13 Nov 2026 &middot; data: {S['reviews_total']:,} newest Google Play reviews of com.delhiveryConsigneeApp ({S['date_from']} to {S['date_to']}), pulled with google-play-scraper</div>

<div class="kpis">
<div class="k"><b>{recent:.0f}%</b><span>of reviews in this window are 1-2 star, vs {life:.0f}% across all {LIFETIME['ratings']:,} lifetime ratings</span></div>
<div class="k"><b>{fu['pct']}%</b><span>of 1-2 star reviews say the parcel was marked "customer unavailable" or a fake attempt ({fu['n']} reviews)</span></div>
<div class="k"><b>{S['median_days_mentioned']:.0f} days</b><span>median delay people quote, in the {S['reviews_with_days']} complaints that name a number of days</span></div>
<div class="k"><b>{S['themes']['no_human_support']['pct']}%</b><span>say they could not reach a human: bot replies, dead numbers, tickets closed</span></div>
</div>

<h2>What the complaints are about</h2>
<img src="data:image/png;base64,{chart}" style="width:100%;max-width:640px">
<div class="foot" style="margin-top:0">{S['untagged_pct']}% of negative reviews match no theme; about half of those are 8 words or fewer ("worst service").</div>

<h2>The pattern worth fixing first: the "customer unavailable" loop</h2>
<ul>
<li>Delays are the biggest bucket, but "marked unavailable without a call" is the one that turns a delay into anger. People describe the same sequence: out for delivery &rarr; no call or a one-second ring &rarr; status flips to "recipient unavailable" &rarr; repeat next day.</li>
<li>{S['false_unavailable_and_unreachable']} reviews say both: they were marked unavailable <i>and</i> the agent would not pick up when they called back.</li>
<li class="q">"delivery executives gives a 1 sec. missed call and report receiver unavailable or unreachable."</li>
<li class="q">"The app falsely showed that I had rejected the delivery. Later, it said I didn’t answer the call, even though I never received any call."</li>
<li>Each of these is a paid re-attempt for Delhivery, an RTO risk for the seller, and a 1-star review that sellers read when choosing a courier.</li>
</ul>

<h2>Proposed fix (small, testable)</h2>
<table>
<tr><th>Change</th><th>How</th><th>Metric to watch</th></tr>
<tr><td>Proof of attempt before "unavailable"</td><td>Agent app allows the status only after a masked call that rang at least 20 s and a GPS ping within ~200 m of the drop. Otherwise the status reads "attempt not made" and the parcel is re-queued.</td><td>Unavailable rate per 1,000 attempts; re-attempt cost</td></tr>
<tr><td>One-tap "I was available"</td><td>Link in the SMS and tracking page. A dispute auto-books a priority re-attempt and counts against that agent's false-attempt score.</td><td>Dispute rate per agent and per hub</td></tr>
<tr><td>Human after two bot loops</td><td>Hand off to a person when the same shipment is raised twice, or it has been stuck more than 3 days.</td><td>Repeat contacts per shipment</td></tr>
</table>
<div class="foot">Method and limits: newest {S['reviews_total']:,} reviews; the {S['negative_1_2_star']:,} 1-2 star ones were cut to {S['negative_unique_texts']:,} unique texts before tagging, since some complaints are posted word for word by several accounts (English store listing, India), so recent but not a random sample of all users. Themes are keyword rules in English, Hinglish and some Hindi; a hand check of 30 reviews tagged (on the first pull) "unavailable" found about 25 correct (~83%). Review text is the customer's account, not verified delivery data; the real rates would come from Delhivery's attempt logs. Code: fetch.py, analyze.py, report.py.</div>
</body></html>"""
open("Delhivery_Review_Brief_1.html", "w", encoding="utf-8").write(html)
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if os.path.exists(edge):
    subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={os.path.abspath('Delhivery_Review_Brief_1.pdf')}", os.path.abspath("Delhivery_Review_Brief_1.html")], check=False, timeout=60)
print("done")
