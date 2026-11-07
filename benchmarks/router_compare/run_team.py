"""Run the team router (vitasync-router) on a question set, optionally with other JSON key names.

Only the key names of the 17 flags change: same order, descriptions, examples and rules. The answer is
mapped back to the original names before the unchanged validator and router see it.
Policy: relaxed (symptom_with_data=allow, symptom_with_tip=allow, condition_named=general_plus_referral).

    python run_team.py <lang|kurz|zahl> <questions .tsv/.csv/.xlsx> <out.csv> [--model qwen3:8b]

Prints only counts and ids, never question texts. Needs a free GPU for valid timings.
"""
import argparse
import csv
import json
from pathlib import Path

from common import import_team_router, load_questions

import_team_router()
from vitasync_router import extractor as X  # noqa: E402
from vitasync_router import labels as L  # noqa: E402
from vitasync_router.pipeline import RouterPipeline  # noqa: E402
from vitasync_router.router import Policy  # noqa: E402

SHORT = {
    "symptom_mentioned": "symptom", "asks_cause_or_diagnosis": "ursache", "asks_value_evaluation": "bewertung",
    "asks_score_or_rating": "score", "asks_color_coding": "farbe", "asks_medication_advice": "medikament",
    "asks_pharmacy_interpretation": "apotheke_deutung", "asks_own_data": "eigene_daten",
    "asks_symptom_logging": "tagebuch", "asks_compilation_for_appointment": "export", "asks_general_knowledge": "wissen",
    "asks_lifestyle_tip": "tipp", "asks_app_help": "app", "own_condition_named": "erkrankung",
    "acute_danger_signs": "notfall", "self_harm_or_crisis": "krise", "message_unclear": "unklar",
}
VARIANTS = {
    "lang": {f: f for f in X.FLAGS},
    "kurz": SHORT,
    "zahl": {f: str(i) for i, f in enumerate(X.FLAGS, 1)},
}


class KeyedExtractor(X.OllamaExtractor):
    """Team extractor with renamed flag keys in prompt and schema; answers are mapped back."""

    def __init__(self, names: dict[str, str], **kw):
        super().__init__(**kw)
        self.names = names
        self.back = {v: k for k, v in names.items()}
        assert len(self.back) == len(names)
        prompt = X.system_prompt()
        for long in sorted(names, key=len, reverse=True):  # longest first: no partial replacements
            prompt = prompt.replace(long, names[long])
        self._system = prompt
        schema = X.json_schema()
        schema["properties"] = {names.get(k, k): v for k, v in schema["properties"].items()}
        schema["required"] = [names.get(k, k) for k in schema["required"]]
        self._schema = schema
        self.last = None

    def extract(self, text):
        t0 = X.time.perf_counter()
        resp = self._post("/api/chat", self._payload(text))
        latency = X.time.perf_counter() - t0
        content = (resp.get("message") or {}).get("content", "")
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise X.ExtractionError(f"invalid JSON: {e}") from e
        mapped = json.dumps({self.back.get(k, k): v for k, v in data.items()})
        flags, intent, sub, conf = X.parse_and_validate(mapped)
        self.last = (resp.get("prompt_eval_count"), resp.get("eval_count"), resp.get("eval_duration"))
        return X.Extraction(flags, intent, sub, conf, latency, resp.get("prompt_eval_count"),
                            resp.get("eval_count"), content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=sorted(VARIANTS))
    ap.add_argument("questions", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--model", default="qwen3:8b")
    a = ap.parse_args()
    policy = Policy.from_overrides(["symptom_with_data=allow", "symptom_with_tip=allow",
                                    "condition_named=general_plus_referral"])
    ext = KeyedExtractor(VARIANTS[a.variant], model=a.model)
    router = RouterPipeline(policy=policy, extractor=ext)
    ext.warmup()
    rows = load_questions(a.questions)
    cols = ["id", "expected", "final_pred", "final_sub", "stage", "latency_s", "prompt_tokens",
            "output_tokens", "gen_s", "flags", "reasons", "error"]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for i, row in enumerate(rows, 1):
            ext.last = None
            res = router.route(row["question"])
            pt, ot, ed = ext.last or (None, None, None)
            w.writerow({"id": row["id"], "expected": L.normalise_intent(row["intent"]), "final_pred": res.route,
                        "final_sub": res.sub_label or "", "stage": res.stage,
                        "latency_s": f"{res.latency_s:.3f}" if res.latency_s is not None else "",
                        "prompt_tokens": pt or "", "output_tokens": ot or "",
                        "gen_s": f"{ed / 1e9:.3f}" if ed else "", "flags": " ".join(res.flags),
                        "reasons": " ".join(res.reasons), "error": res.error or ""})
            fh.flush()
            print(f"[{a.variant} {i}/{len(rows)}] {row['id']} {res.stage} {res.route}", flush=True)


if __name__ == "__main__":
    main()
