"""Structure check of ChatGPT batches; prints counts only, never question texts.

    python check_batch.py data/router/gpt/batch_01.tsv [weitere ...]
"""
import csv, re, sys
from collections import Counter
INTENTS = {"DATA_QUERY","HEALTH_QUESTION","COMBINED","APP_HELP","OUT_OF_SCOPE","EMERGENCY","UNCLEAR"}
SUBS = {"VALUE_EVALUATION","SCORE_REQUEST","COLOR_REQUEST","PHARMACY_SUMMARY","MEDICATION","DIAGNOSIS_TRIAGE"}
WANT = {"DATA_QUERY":50,"HEALTH_QUESTION":40,"COMBINED":20,"APP_HELP":30,"UNCLEAR":10,"EMERGENCY":20,"OUT_OF_SCOPE":80}
WANT_SUB = {"VALUE_EVALUATION":16,"SCORE_REQUEST":12,"COLOR_REQUEST":8,"PHARMACY_SUMMARY":8,"MEDICATION":16,"DIAGNOSIS_TRIAGE":20}
COLS = ["id","question","intent","sub_label","use_case","symptomatic","note"]
norm = lambda s: re.sub(r"\W+", " ", s.lower()).strip()
s310 = {norm(r["question"]) for r in csv.DictReader(open("data/router/s3-10_v1.tsv", encoding="utf-8"), delimiter="\t")}
for path in sys.argv[1:]:
    raw = open(path, encoding="utf-8-sig").read()
    lines = raw.splitlines()
    print("==", path, "| Zeilen inkl. Kopf:", len(lines), "| Tabs je Zeile:", Counter(l.count("\t") for l in lines))
    rows = list(csv.DictReader(raw.splitlines(), delimiter="\t"))
    head = list(rows[0].keys()) if rows else []
    print("Kopf ok:", head == COLS, "" if head == COLS else head)
    print("Fragen:", len(rows))
    bad = []
    for r in rows:
        r = {k: (v or "").strip() for k, v in r.items() if k}
        p = []
        if not re.fullmatch(r"B\d\d-\d{3}", r.get("id","")): p.append("id")
        if r.get("intent") not in INTENTS: p.append("intent=" + r.get("intent",""))
        if r.get("intent") == "OUT_OF_SCOPE" and r.get("sub_label") not in SUBS: p.append("sub_label")
        if r.get("intent") != "OUT_OF_SCOPE" and r.get("sub_label"): p.append("sub_label gesetzt")
        if not re.fullmatch(r"CB-(0[1-9]|[12]\d|3[0-5])", r.get("use_case","")): p.append("use_case=" + r.get("use_case",""))
        if r.get("symptomatic") not in ("yes","no"): p.append("symptomatic")
        if not r.get("question"): p.append("question leer")
        if p: bad.append((r.get("id"), p))
    print("Fehlerhafte Zeilen:", len(bad), bad[:10])
    ic = Counter(r["intent"].strip() for r in rows); sc = Counter(r["sub_label"].strip() for r in rows if r["intent"].strip()=="OUT_OF_SCOPE")
    print("Intents:", {k: f"{ic.get(k,0)}/{v}" for k, v in WANT.items()})
    print("Sub-Labels:", {k: f"{sc.get(k,0)}/{v}" for k, v in WANT_SUB.items()})
    notes = [r["note"].lower() for r in rows]
    print("Pflicht: Paare", sum("pair with" in n for n in notes), "(>=30) | Reizwort", sum("trigger word" in n for n in notes),
          "(>=20) | Injection", sum("prompt injection" in n for n in notes), "(>=10) | Symptom+Daten",
          sum("symptom + data" in n for n in notes), "(>=15) | Helfer CB-31", sum(r["use_case"].strip()=="CB-31" for r in rows), "(>=5) | unsure", sum("unsure" in n for n in notes))
    q = [norm(r["question"]) for r in rows]
    print("Doppelte im Batch:", sum(c-1 for c in Counter(q).values() if c > 1), "| wortgleich mit S3-10:", sum(x in s310 for x in q))
    print("Krise (EMERGENCY, Notiz enthält crisis/suicid/self):", sum(r["intent"].strip()=="EMERGENCY" and re.search("crisis|suicid|self", r["note"].lower()) is not None for r in rows))
