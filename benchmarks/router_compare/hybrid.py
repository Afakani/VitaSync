"""Hybrid offline: CP1 -> BERT blocks only if very sure (OOS class, p>=T) -> else team router result.

    python hybrid.py <team result CSV on prompts.xlsx from run_team.py>
Prints only counts and ids, never prompt texts. No new LLM calls.
"""
import csv
import sys

from transformers import AutoModelForSequenceClassification, AutoTokenizer

import eval_prompts as E
import train_bert as T

data = E.rows()
team = {r["id"]: r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8-sig"))}
tok = AutoTokenizer.from_pretrained(E.MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(E.MODEL_DIR).to("cuda")
probs = T.predict(model, tok, [{"text": r["question"]} for r in data], "cuda")
OOS = [i for i, c in enumerate(T.CLASSES) if c.startswith("OOS/")]
for t in (0.5, 0.8, 0.9, 0.95, 0.98, 0.99):
    pred, cut, saved, wrong_cut = {}, 0, 0.0, []
    for r, p in zip(data, probs):
        tr = team[r["id"]]
        k = int(p.argmax())
        if tr["stage"] != "CP1" and k in OOS and p[k] >= t:
            pred[r["id"]] = "block"
            cut += 1
            saved += float(tr["latency_s"] or 0)
            if E.TEAM[tr["final_pred"]] != "block":
                wrong_cut.append((r["id"], r["category"], r["expected_decision"], tr["final_pred"]))
        else:
            pred[r["id"]] = E.TEAM[tr["final_pred"]]
    E.score(f"Hybrid T={t}: BERT faengt {cut}/750 ab, spart {saved / 60:.0f} min LLM-Zeit", data, pred)
    print("  BERT entscheidet anders als Team:", wrong_cut)
