import re, csv
from collections import Counter

HIGH = [r"\bcurrent(ly)?\b", r"\blatest\b", r"\btoday\b", r"\bnow\b", r"\bthis (week|month|year)\b",
        r"\bprice\b", r"\bexchange rate\b", r"\bweather\b", r"\bdeadline\b", r"\bCEO\b", r"\bpresident\b",
        r"\bnewest\b", r"\brecent(ly)?\b", r"\b20(2[5-9])\b", r"\bscore\b", r"\bstill\b"]
AMBIG = [r"\bpolicy\b", r"\brequire(d|ments?)?\b", r"\bfee\b", r"\btuition\b", r"\bversion\b",
         r"\brules?\b", r"\blaw\b", r"\bcurriculum\b", r"\bschedule\b", r"\bbest\b"]

def route(q):
    if any(re.search(p, q, re.I) for p in HIGH): return "HIGH"
    if any(re.search(p, q, re.I) for p in AMBIG): return "AMBIGUOUS"
    return "LOW"

rows = list(csv.DictReader(open("pilot_questions.csv")))
correct = 0; conf = Counter(); misses = []
for r in rows:
    p = route(r["question"]); conf[(r["label"], p)] += 1
    if p == r["label"]: correct += 1
    else: misses.append((r["question"], r["label"], p))
n = len(rows)
print(f"accuracy {correct}/{n} = {correct/n:.0%}")
labels = ["LOW","AMBIGUOUS","HIGH"]
print("true\\pred", labels)
for t in labels: print(t, [conf[(t,p)] for p in labels])
high = [r for r in rows if r["label"]=="HIGH"]
caught = sum(route(r["question"])=="HIGH" for r in high)
print(f"HIGH recall {caught}/{len(high)}")
searches = sum(route(r["question"])=="HIGH" for r in rows)
print(f"searches triggered {searches}/{n}")
for m in misses: print("MISS", m)
