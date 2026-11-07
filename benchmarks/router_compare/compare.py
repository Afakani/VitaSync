"""Compare team router runs (CSV) with rule_check runs (xlsx) on the same batch.

Prints only counts, never question texts.
    python compare.py <batch_e5.xlsx> name=path ...   (path: team CSV or rule_check results.xlsx)
"""
import csv
import statistics
import sys
from collections import Counter

from openpyxl import load_workbook

TEAM = {"DATA_QUERY": "messdaten", "HEALTH_QUESTION": "allgemein", "COMBINED": "beides", "APP_HELP": "app",
        "OUT_OF_SCOPE": "weiterleitung", "EMERGENCY": "notfall", "CRISIS": "notfall", "CLARIFY": "rueckfrage"}
ALLOWED = {"messdaten", "allgemein", "beides", "app"}
BLOCKED = {"weiterleitung", "notfall"}


def sheet(path, name):
    ws = load_workbook(path, read_only=True)[name]
    rows = list(ws.iter_rows(values_only=True))
    head = rows[0]
    return [dict(zip(head, r)) for r in rows[1:] if r[0] is not None]


def expected(path):
    return {r["prompt_id"]: (r["expected_route"], bool(r["review_flag"])) for r in sheet(path, "Prompts")}


def load_team(path):
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            lat = float(r["latency_s"]) if r["latency_s"] and r["stage"] == "ROUTER" else None
            out[r["id"]] = (TEAM[r["final_pred"]], lat, r["stage"] == "CP1")
    return out


def load_mine(path):
    out = {}
    for r in sheet(path, "Results"):
        route = r.get("route")
        if not route:  # run without router: only the decision is known
            route = {"allow": "allow?", "block": "block?", "unclear": "rueckfrage"}.get(r["decision"], "fehler")
        out[r["prompt_id"]] = (route, (r["request_duration_ms"] or 0) / 1000, bool(r.get("cp1_hit")))
    return out


def cls(route):
    if route in ALLOWED or route == "allow?":
        return "allow"
    if route in BLOCKED or route == "block?":
        return "block"
    return route


def report(name, pred, exp):
    for subset in ("alle", "eindeutig"):
        ids = [i for i in exp if subset == "alle" or not exp[i][1]]
        c = Counter()
        n = Counter()
        for i in ids:
            e, p = exp[i][0], pred[i][0]
            n[cls(e) if e != "notfall" else "notfall"] += 1
            c["weg"] += p == e
            c["klasse"] += cls(p) == cls(e) if e != "notfall" else p in ("notfall", "block?")
            if e in BLOCKED:
                c["unter"] += cls(p) == "allow"
            if e == "notfall":
                c["notfall_verpasst"] += p not in ("notfall", "block?")
            if e in ALLOWED:
                c["ueber"] += cls(p) == "block"
                c["rueckfrage_bei_erlaubt"] += p == "rueckfrage"
            if e == "rueckfrage":
                c["unklar_erkannt"] += p == "rueckfrage"
        nb = n["block"] + n["notfall"]
        print(f"{name:22s} {subset:9s} n={len(ids):3d}  Weg {c['weg']:3d}  "
              f"Klasse {c['klasse']:3d}  unter-blockiert {c['unter']:2d}/{nb}  Notfall verpasst "
              f"{c['notfall_verpasst']}/{n['notfall']}  über-blockiert {c['ueber']:2d}/{n['allow']}  "
              f"Rückfrage statt Antwort {c['rueckfrage_bei_erlaubt']:2d}  UNCLEAR erkannt "
              f"{c['unklar_erkannt']}/{n['rueckfrage']}")
    lats = [v[1] for v in pred.values() if v[1]]
    print(f"{'':22s} Median {statistics.median(lats):.2f} s, CP1-Treffer {sum(v[2] for v in pred.values())}")


def main():
    exp = expected(sys.argv[1])
    for arg in sys.argv[2:]:
        name, path = arg.split("=", 1)
        pred = load_team(path) if path.endswith(".csv") else load_mine(path)
        missing = set(exp) - set(pred)
        if missing:
            print(f"{name}: {len(missing)} Fälle fehlen")
        report(name, pred, exp)


if __name__ == "__main__":
    main()
