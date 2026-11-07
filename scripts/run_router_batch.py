"""Run the router modules of apps/api (features/chat.route_message) on a question batch with a real model.

Development tool, not part of the application. Prints only ids and counts, never question texts.
Output CSV has the columns of the team router runs, so benchmarks/router_compare/compare.py can read it.

    apps/api/.venv/Scripts/python.exe scripts/run_router_batch.py <batch.tsv> <out.csv>
        [--policy "symptom_with_data=allow,..."] [--model qwen3:8b]

Model URL, model and CP1 file come from the environment (LLM_BASE_URL, LLM_MODEL, CP1_PATTERNS) or
the defaults in core/config.py. Run only on a free GPU; never in parallel with another model run.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from vitasync.adapters.llm import OllamaIntentExtractor  # noqa: E402
from vitasync.core.config import load_settings  # noqa: E402
from vitasync.core.intent import Policy  # noqa: E402
from vitasync.features.chat import route_message  # noqa: E402
from vitasync.features.input_guard import InputGuard  # noqa: E402

COLS = ["id", "expected", "expected_sub", "stage", "final_pred", "final_sub", "rule_decision", "rule",
        "llm_pred", "llm_sub", "confidence", "latency_s", "flags", "reasons", "error"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--policy", default=None, help="overrides ROUTER_POLICY")
    ap.add_argument("--model", default=None, help="overrides LLM_MODEL")
    a = ap.parse_args()

    s = load_settings()
    policy = Policy.from_string(a.policy if a.policy is not None else s.router_policy)
    model = a.model or s.llm_model or "qwen3:8b"
    guard = InputGuard.from_file(ROOT / s.cp1_patterns)
    ext = OllamaIntentExtractor(model=model, base_url=s.llm_base_url, timeout_s=s.llm_timeout_s)
    ext.extract_raw("Wie viele Schritte bin ich gestern gelaufen?")  # warm-up, not measured

    with a.batch.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            t0 = time.perf_counter()
            d = route_message(r["question"], guard, ext, policy)
            w.writerow({
                "id": r["id"], "expected": r["intent"].strip(), "expected_sub": (r.get("sub_label") or "").strip(),
                "stage": d.stage, "final_pred": d.route, "final_sub": d.sub_label or "",
                "rule_decision": d.rule.decision if d.rule else "", "rule": d.rule.rule or "" if d.rule else "",
                "llm_pred": d.llm_intent or "", "llm_sub": d.llm_sub_label or "",
                "confidence": "" if d.confidence is None else f"{d.confidence:.2f}",
                "latency_s": f"{time.perf_counter() - t0:.3f}",
                "flags": " ".join(d.rule.flags) if d.rule else "", "reasons": " ".join(d.reasons),
                "error": d.error or ""})
            fh.flush()
            print(f"[{i}/{len(rows)}] {r['id']} {d.stage} {d.route}", flush=True)


if __name__ == "__main__":
    main()
