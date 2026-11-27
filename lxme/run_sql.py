"""Load the review CSV into SQLite and run themes.sql, printing every result set."""
import csv, sqlite3, sys
src = sys.argv[1] if len(sys.argv) > 1 else "../data/lxme.csv"
db = sqlite3.connect("lxme.db")
db.execute("DROP TABLE IF EXISTS reviews")
db.execute("CREATE TABLE reviews(id TEXT PRIMARY KEY, date TEXT, score INT, version TEXT, thumbs INT, replied INT, text TEXT, reply TEXT)")
rows = []; seen_text = set()
for r in csv.DictReader(open(src, encoding="utf-8")):
    key = r["text"].strip().lower()
    if len(key) > 40 and key in seen_text: continue   # identical long texts from several accounts counted once
    seen_text.add(key)
    rows.append((r["id"], r["date"], int(r["score"]), r["version"], int(r["thumbs"]), r["replied"] == "True", r["text"], r["reply"]))
db.executemany("INSERT OR IGNORE INTO reviews VALUES (?,?,?,?,?,?,?,?)", rows)
script = chr(10).join(l for l in open("themes.sql", encoding="utf-8").read().splitlines() if not l.strip().startswith("--"))
for stmt in [s.strip() for s in script.split(";") if s.strip()]:
    body = "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("--")).strip()
    cur = db.execute(stmt)
    if body.upper().startswith("SELECT"):
        cols = [c[0] for c in cur.description]; print("\n" + " | ".join(cols))
        for row in cur.fetchall(): print(" | ".join(str(x) for x in row))
db.commit()
