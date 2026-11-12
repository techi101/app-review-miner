"""Tag 1-2 star Play reviews with complaint themes (English + Hinglish keywords) and summarise."""
import re, sys, json
import pandas as pd, warnings
warnings.filterwarnings("ignore")

sys.stdout.reconfigure(encoding="utf-8")

THEMES = {
    "false_unavailable": r"(unavailable|not available|nobody was available|no one was available|customer (not )?avail|recipient (un|not )avail|"
                         r"marked (me )?(as )?(un|not)|rejected|no ?one (was )?(at|available)|avaiable|unavaliable|(single|one|1) ring|rescheduled without|fake return|उपलब्ध नहीं|मिला ही नही|"
                         r"nobody (came|comes)|false(ly)? (attempt|marked|status|update)|fake (attempt|update|status)|"
                         r"door (was )?locked|address not found|without (calling|call|contact)|didn'?t (even )?call|did not (even )?call|never call|no call|"
                         r"koi (bhi )?nahi aa|call (bhi )?nahi (kiya|karte|aaya))",
    "agent_unreachable": r"(not (picking|picks|pick|answering|answer|responding|receiv)|doesn'?t (pick|answer)|didn'?t (pick|answer)|"
                         r"switch(ed)? off|not reachable|unreachable|call forward|no incoming|phone (is )?off|blocked my number|"
                         r"call (receive|recieve|utha) nahi|phone nahi utha)",
    "delay_stuck": r"(delay|late|stuck|still not (received|deliver)|not (yet )?(received|delivered)|haven'?t (received|got)|"
                   r"\b\d+\s*(days?|din)\b|same (hub|facility|location)|out for delivery (for|since)|week|"
                   r"nahi mila|abhi tak)",
    "no_human_support": r"(no (customer )?(care|support|human|live agent|call support|helpline|contact)|customer (care|support|service) (is )?(not|useless|worst|pathetic|bad)|"
                        r"\bbot\b|chatbot|automated|\bai\b|auto(matic)? (reply|response)|ticket|no (one|body) (to )?(talk|help|respond)|"
                        r"help (me )?section|no number|number (does not|doesn'?t) exist|can'?t (contact|reach)|unable to (contact|reach))",
    "rude_or_collect_yourself": r"(rude|misbehav|abus|attitude|shout|threat|gangster|come (to|and) (the |his )?(office|hub|warehouse)|"
                                r"collect (it )?(from|at) (the )?(office|hub|warehouse)|pick (it )?up (from|at) (the |his )?(office|hub|warehouse))",
    "pickup_return_failed": r"(pick ?up (was |is )?(not|failed|cancel|refus)|reverse pickup|return pickup|pickup executive|exchange|"
                            r"pickup (attempt|request))",
    "damaged_wrong_lost": r"(damag|broken|wrong (product|item|parcel|size)|lost|missing|empty (box|package)|tamper|open(ed)? (box|package)|"
                          r"different product|inferior)",
    "money_extra_refund": r"(extra (money|charge|amount)|charge extra|paid twice|took (the )?payment|\bcod\b|cash on delivery|refund|oil money|bribe|\btip\b|asked (for )?(money|extra)|money (was )?deducted)",
    "app_tracking_bug": r"(tracking (is |not )?(wrong|not updat|incorrect|glitch)|not updat|glitch|app (is )?(crash|not work|useless)|"
                        r"otp|login|status (is )?(wrong|incorrect|fake))",
}
POSITIVE_REPLY = r"(delighted|happy to know|kind words|glad you|enjoying|positive experience|thrilled)"


def tag(df):
    low = df.text.fillna("").str.lower()
    for k, pat in THEMES.items():
        df[k] = low.str.contains(pat, regex=True)
    df["any_theme"] = df[list(THEMES)].any(axis=1)
    df["days_mentioned"] = low.str.extract(r"(\d{1,2})\s*(?:days?|din)\b")[0].astype(float)
    return df


def main(path, label):
    d = pd.read_csv(path)
    d["date"] = pd.to_datetime(d.date)
    raw_neg = d[d.score <= 2]
    neg = tag(raw_neg.drop_duplicates("text").copy())
    out = {"label": label, "reviews_total": len(d), "date_from": str(d.date.min().date()), "date_to": str(d.date.max().date()),
           "negative_1_2_star": len(raw_neg), "negative_unique_texts": len(neg), "share_negative": round(len(raw_neg) / len(d), 3),
           "short_positive_share_le5_words": round((d[d.score >= 4].text.fillna("").str.split().str.len() <= 5).mean(), 3),
           "themes": {k: {"n": int(neg[k].sum()), "pct": round(100 * neg[k].mean(), 1)} for k in THEMES},
           "untagged_pct": round(100 * (~neg.any_theme).mean(), 1),
           "median_days_mentioned": float(neg.days_mentioned.median()) if neg.days_mentioned.notna().any() else None,
           "reviews_with_days": int(neg.days_mentioned.notna().sum())}
    # co-occurrence: false 'unavailable' together with agent not answering
    out["false_unavailable_and_unreachable"] = int((neg.false_unavailable & neg.agent_unreachable).sum())
    rep = neg.reply.fillna("")
    out["neg_replied_pct"] = round(100 * (rep != "").mean(), 1)
    out["neg_with_positive_toned_reply"] = int(rep.str.lower().str.contains(POSITIVE_REPLY).sum())
    top_templates = rep[rep != ""].str[:70].value_counts()
    out["top_reply_templates"] = top_templates.head(3).to_dict()
    out["top2_template_share_pct"] = round(100 * top_templates.head(2).sum() / (rep != "").sum(), 1)
    # weekly trend of the top theme
    wk = neg.set_index("date").resample("W")["false_unavailable"].agg(["sum", "count"])
    out["weekly_false_unavailable"] = {str(i.date()): f"{int(r['sum'])}/{int(r['count'])}" for i, r in wk.iterrows()}
    neg.to_csv(path.replace(".csv", "_tagged.csv"), index=False)
    json.dump(out, open(path.replace(".csv", "_summary.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
