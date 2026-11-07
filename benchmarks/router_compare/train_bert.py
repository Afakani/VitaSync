"""BERT router experiment: fine-tune a German BERT on the ChatGPT batches and compare.

Split: train batch 01-14, validation 15-17 (epoch choice + block threshold), test 18-20 and S3-10.
Prints only counts and ids, never question texts. Synthetic data only.

    python train_bert.py        (own venv with torch/transformers, see README.md)
"""
from __future__ import annotations

import csv
import json
import random
import statistics
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

from common import GPT_BATCHES as GPT, HERE, S310, import_team_router

MODEL_DIR = HERE / "bert_model"
MODEL = "deepset/gbert-base"
SEED, MAXLEN, EPOCHS, LR, BS = 42, 128, 5, 3e-5, 16

import_team_router()
from vitasync_router.input_guard import InputGuard  # noqa: E402  (team CP1, unchanged)

SUBS = ["VALUE_EVALUATION", "SCORE_REQUEST", "COLOR_REQUEST", "PHARMACY_SUMMARY", "MEDICATION", "DIAGNOSIS_TRIAGE"]
CLASSES = ["DATA_QUERY", "HEALTH_QUESTION", "COMBINED", "APP_HELP", "EMERGENCY", "UNCLEAR"] + [f"OOS/{s}" for s in SUBS]
ROUTE = {"DATA_QUERY": "messdaten", "HEALTH_QUESTION": "allgemein", "COMBINED": "beides", "APP_HELP": "app",
         "EMERGENCY": "notfall", "UNCLEAR": "rueckfrage", **{f"OOS/{s}": "weiterleitung" for s in SUBS}}
ALLOWED = {"messdaten", "allgemein", "beides", "app"}
BLOCK_IDX = [i for i, c in enumerate(CLASSES) if ROUTE[c] in ("weiterleitung", "notfall")]


def label(intent: str, sub: str) -> str:
    intent = {"HEALTH_QUESTIONS": "HEALTH_QUESTION"}.get(intent.strip(), intent.strip())
    return f"OOS/{sub.strip()}" if intent == "OUT_OF_SCOPE" else intent


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    out = []
    for r in rows:
        r = {k: (v or "").strip() for k, v in r.items()}
        c = label(r["intent"], r["sub_label"])
        out.append({"id": r["id"], "text": r["question"], "y": CLASSES.index(c),
                    "contested": r["symptomatic"] == "yes" and ROUTE[c] in ALLOWED})
    return out


def batches(nums):
    return [row for n in nums for row in load(GPT / f"batch_{n:02d}.tsv")]


def encode(tok, rows):
    enc = tok([r["text"] for r in rows], truncation=True, max_length=MAXLEN, padding=True, return_tensors="pt")
    return [{"input_ids": enc["input_ids"][i], "attention_mask": enc["attention_mask"][i],
             "labels": torch.tensor(rows[i]["y"])} for i in range(len(rows))]


@torch.no_grad()
def predict(model, tok, rows, dev):
    model.eval()
    probs = []
    for i in range(0, len(rows), 64):
        enc = tok([r["text"] for r in rows[i:i + 64]], truncation=True, max_length=MAXLEN, padding=True,
                  return_tensors="pt").to(dev)
        probs.append(torch.softmax(model(**enc).logits.float(), -1).cpu().numpy())
    return np.concatenate(probs)


def routes(probs, block_t: float | None, rows=None, guard=None):
    """argmax; with block_t: if P(any blocking class) >= block_t, take the most likely blocking class.
    With guard: team CP1 first (emergency/crisis -> notfall, injection -> weiterleitung if allowed)."""
    out = []
    for i, p in enumerate(probs):
        k = int(p.argmax())
        if block_t is not None and ROUTE[CLASSES[k]] not in ("weiterleitung", "notfall") \
                and p[BLOCK_IDX].sum() >= block_t:
            k = BLOCK_IDX[int(p[BLOCK_IDX].argmax())]
        r = ROUTE[CLASSES[k]]
        if guard is not None:
            g = guard.check(rows[i]["text"])
            if g.emergency or g.crisis:
                r = "notfall"
            elif g.injection and r in ALLOWED:
                r = "weiterleitung"
        out.append(r)
    return out


def metrics(rows, pred):
    c = Counter()
    n = Counter()
    for r, p in zip(rows, pred):
        e = ROUTE[CLASSES[r["y"]]]
        n[e if e in ("notfall", "rueckfrage", "weiterleitung") else "allow"] += 1
        c["weg"] += p == e
        if e in ("weiterleitung", "notfall"):
            c["unter"] += p in ALLOWED
        if e == "notfall":
            c["notfall_verpasst"] += p != "notfall"
        if e in ALLOWED:
            c["ueber"] += p in ("weiterleitung", "notfall")
        if e == "rueckfrage":
            c["unklar"] += p == "rueckfrage"
    return c, n


def show(name, rows, pred):
    c, n = metrics(rows, pred)
    nb = n["weiterleitung"] + n["notfall"]
    line = (f"{name:34s} n={len(rows):4d}  Weg {c['weg']:4d} ({100 * c['weg'] / len(rows):.1f} %)  "
            f"unter-blockiert {c['unter']:2d}/{nb}  Notfall verpasst {c['notfall_verpasst']:2d}/{n['notfall']}  "
            f"über-blockiert {c['ueber']:3d}/{n['allow']}  UNCLEAR {c['unklar']}/{n['rueckfrage']}")
    print(line, flush=True)
    return c


def main():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    train, val, test = batches(range(1, 15)), batches(range(15, 18)), batches(range(18, 21))
    s310 = load(S310)
    print(f"Gerät {dev} | Training {len(train)} | Validierung {len(val)} | Test {len(test)} | S3-10 {len(s310)}")
    print("Klassen Training:", dict(Counter(CLASSES[r["y"]] for r in train)))

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=len(CLASSES)).to(dev)
    loader = DataLoader(encode(tok, train), batch_size=BS, shuffle=True,
                        generator=torch.Generator().manual_seed(SEED))
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    steps = EPOCHS * len(loader)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    scaler = torch.amp.GradScaler(enabled=dev == "cuda")

    best, best_state = None, None
    t0 = time.perf_counter()
    for ep in range(1, EPOCHS + 1):
        model.train()
        for b in loader:
            b = {k: v.to(dev) for k, v in b.items()}
            with torch.autocast(dev, enabled=dev == "cuda"):
                loss = model(**b).loss
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
        c = show(f"Epoche {ep} Validierung", val, routes(predict(model, tok, val, dev), None))
        score = (c["unter"], -c["weg"])  # fewest under-blocks first, then most correct routes
        if best is None or score < best:
            best, best_state = score, {k: v.detach().clone() for k, v in model.state_dict().items()}
            best_ep = ep
    print(f"Training {time.perf_counter() - t0:.0f} s, beste Epoche {best_ep}")
    model.load_state_dict(best_state)

    # Block threshold chosen on validation only: smallest under-blocking, then fewest over-blocks.
    pv = predict(model, tok, val, dev)
    cands = []
    for t in (None, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1, 0.05):
        c, _ = metrics(val, routes(pv, t))
        cands.append(((c["unter"], c["ueber"]), t))
    block_t = min(cands, key=lambda x: x[0])[1]
    print(f"Sperrschwelle (auf Validierung gewählt): {block_t}")

    guard = InputGuard()
    print("\n== Test Batch 18-20 (ungesehen) ==")
    pt = predict(model, tok, test, dev)
    show("BERT argmax", test, routes(pt, None))
    show(f"BERT Schwelle {block_t}", test, routes(pt, block_t))
    full = routes(pt, block_t, test, guard)
    show(f"CP1 + BERT Schwelle {block_t}", test, full)
    clean = [i for i, r in enumerate(test) if not r["contested"]]
    show("CP1 + BERT, ohne strittige", [test[i] for i in clean], [full[i] for i in clean])

    print("\n== S3-10 (vom Team geschrieben, anderer Stil, kein UNCLEAR) ==")
    ps = predict(model, tok, s310, dev)
    show("BERT argmax", s310, routes(ps, None))
    show(f"CP1 + BERT Schwelle {block_t}", s310, routes(ps, block_t, s310, guard))

    # Latency: one request at a time, as in the chat
    for d in (["cuda", "cpu"] if dev == "cuda" else ["cpu"]):
        model.to(d)
        lat = []
        for r in test[:100]:
            enc = tok(r["text"], truncation=True, max_length=MAXLEN, return_tensors="pt").to(d)
            t = time.perf_counter()
            with torch.no_grad():
                model(**enc)
            if d == "cuda":
                torch.cuda.synchronize()
            lat.append(time.perf_counter() - t)
        print(f"Latenz {d}: Median {1000 * statistics.median(lat[5:]):.1f} ms")

    # Ids of critical errors on the test batches, for manual review
    crit = []
    for r, p in zip(test, full):
        e = ROUTE[CLASSES[r["y"]]]
        if (e in ("weiterleitung", "notfall") and p in ALLOWED) or (e == "notfall" and p != "notfall"):
            crit.append((r["id"], CLASSES[r["y"]], p))
    print("\nKritische Fälle Test (id, Soll, Ist):", crit)
    model.save_pretrained(MODEL_DIR)
    tok.save_pretrained(MODEL_DIR)
    (MODEL_DIR / "run.json").write_text(json.dumps({"model": MODEL, "epoch": best_ep, "block_t": block_t,
                                                    "classes": CLASSES, "seed": SEED}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
