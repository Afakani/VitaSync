"""Run the router modules of apps/api (features/chat.route_message) on a question batch.

Development tool, not part of the application. Prints only ids and counts, never question texts.
Output CSV has the columns of the team router runs, so benchmarks/router_compare/compare.py can read it.

    apps/api/.venv/Scripts/python.exe scripts/run_router_batch.py <batch.tsv> <out.csv>
        [--recognizer slm|llm] [--policy "symptom_with_data=allow,..."] [--model qwen3:8b]
        [--emb-cache <file.json>]

Settings come from the environment or the repo's .env (read here, never printed): LLM_BASE_URL,
LLM_MODEL, CP1_PATTERNS, CP2_PATTERNS, SLM_WEIGHTS, EMBED_BACKEND, EMBED_MODEL (+ VITASYNC_API_* for api).
SLM: embeddings from local Ollama by default; EMBED_BACKEND=api only on explicit request.
--emb-cache stores one vector per question (key: sha1 of the text), so a second run with another
policy needs no new embedding calls. Never run in parallel with another model run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from vitasync.adapters.embedding import ApiEmbedder, OllamaEmbedder  # noqa: E402
from vitasync.adapters.llm import OllamaIntentExtractor  # noqa: E402
from vitasync.core.config import load_settings  # noqa: E402
from vitasync.core.intent import Policy  # noqa: E402
from vitasync.features.chat import route_message  # noqa: E402
from vitasync.features.input_guard import InputGuard  # noqa: E402
from vitasync.features.recognition import SLM_MIN_CONFIDENCE, LlmRecognizer, SlmRecognizer, SlmWeights  # noqa: E402
from vitasync.features.safety_net import SafetyNet  # noqa: E402

COLS = ["id", "expected", "expected_sub", "stage", "final_pred", "final_sub", "rule_decision", "rule",
        "llm_pred", "llm_sub", "confidence", "latency_s", "flags", "reasons", "error"]


def read_env() -> dict[str, str]:
    """Process environment, completed from the repo's .env (values never printed)."""
    env = dict(os.environ)
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


class CachedEmbedder:
    """Wraps an embedder; vectors are stored per text hash in a JSON file."""

    def __init__(self, inner, path: Path):
        self.inner, self.path, self.model = inner, path, inner.model
        self.cache = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        self.calls = 0

    @staticmethod
    def key(text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]

    def embed(self, texts):
        missing = [t for t in texts if self.key(t) not in self.cache]
        if missing:
            self.calls += 1
            for t, v in zip(missing, self.inner.embed(missing)):
                self.cache[self.key(t)] = v
        return [self.cache[self.key(t)] for t in texts]

    def prefetch(self, texts):
        """Embed all missing texts in batches of 32 and save once."""
        self.embed(list(dict.fromkeys(texts)))
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.cache), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--recognizer", choices=["slm", "llm"], default=None, help="overrides RECOGNIZER")
    ap.add_argument("--policy", default=None, help="overrides ROUTER_POLICY")
    ap.add_argument("--model", default=None, help="LLM model, overrides LLM_MODEL")
    ap.add_argument("--emb-cache", type=Path, default=None)
    ap.add_argument("--prefetch", action="store_true",
                    help="embed the whole batch first (fast, but no realistic per-question latency)")
    ap.add_argument("--embed-backend", choices=["ollama", "api"], default=None, help="overrides EMBED_BACKEND")
    ap.add_argument("--embed-model", default=None, help="overrides EMBED_MODEL")
    a = ap.parse_args()

    env = read_env()
    s = load_settings(env)
    kind = a.recognizer or s.recognizer
    spec = a.policy if a.policy is not None else s.router_policy
    policy = Policy.from_string(spec)
    if kind == "slm" and "min_confidence" not in spec:
        policy = replace(policy, min_confidence=SLM_MIN_CONFIDENCE)
    guard = InputGuard.from_file(ROOT / s.cp1_patterns)
    net = SafetyNet.from_file(ROOT / s.cp2_patterns)

    with a.batch.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))

    if kind == "slm":
        backend = a.embed_backend or s.embed_backend
        model = a.embed_model or s.embed_model
        inner = (ApiEmbedder(model, s.embed_api_base, env.get("VITASYNC_API_KEY", ""))
                 if backend == "api" else OllamaEmbedder(model, s.llm_base_url))
        embedder = CachedEmbedder(inner, a.emb_cache) if a.emb_cache else inner
        if a.emb_cache and a.prefetch:
            t0 = time.perf_counter()
            embedder.prefetch([(r["question"] or "")[:1000] for r in rows])
            print(f"Embeddings bereit ({time.perf_counter() - t0:.1f} s, {len(embedder.cache)} im Cache)", flush=True)
        recognize = SlmRecognizer(embedder, SlmWeights.from_file(ROOT / s.slm_weights))
    else:
        ext = OllamaIntentExtractor(model=a.model or s.llm_model or "qwen3:8b", base_url=s.llm_base_url,
                                    timeout_s=s.llm_timeout_s)
        ext.extract_raw("Wie viele Schritte bin ich gestern gelaufen?")  # warm-up, not measured
        recognize = LlmRecognizer(ext)
    if kind == "slm":
        print(f"Embeddings: {backend}, Modell {model}", flush=True)
    print(f"Erkenner {kind}, Policy min_confidence={policy.min_confidence}, "
          f"symptom_with_data={policy.symptom_with_data}, CP2 {'an' if policy.safety_net else 'aus'}", flush=True)

    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for i, r in enumerate(rows, 1):
            t0 = time.perf_counter()
            d = route_message(r["question"], guard, recognize, policy, net)
            w.writerow({
                "id": r["id"], "expected": r["intent"].strip(), "expected_sub": (r.get("sub_label") or "").strip(),
                "stage": d.stage, "final_pred": d.route, "final_sub": d.sub_label or "",
                "rule_decision": d.rule.decision if d.rule else "", "rule": (d.rule.rule or "") if d.rule else "",
                "llm_pred": d.llm_intent or "", "llm_sub": d.llm_sub_label or "",
                "confidence": "" if d.confidence is None else f"{d.confidence:.3f}",
                "latency_s": f"{time.perf_counter() - t0:.3f}",
                "flags": " ".join(d.rule.flags) if d.rule else "", "reasons": " ".join(d.reasons),
                "error": d.error or ""})
            fh.flush()
            if a.emb_cache and kind == "slm" and i % 50 == 0:
                embedder.save()
            if i % 50 == 0 or i == len(rows):
                print(f"[{i}/{len(rows)}]", flush=True)
    if a.emb_cache and kind == "slm":
        embedder.save()


if __name__ == "__main__":
    main()
