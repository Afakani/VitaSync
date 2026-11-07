"""Run cases sequentially, one model call each, and measure the request duration.

Measurement window: from immediately before ``client.chat`` to immediately after
it returns or raises. Request building happens before, JSON validation, JSONL
writing and Excel export after the window. The value therefore covers client
call, transfer, server queueing, model processing and SDK handling of the reply;
it is neither pure model compute time nor a time per rule.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Callable, Literal

from .config import Config, Rule
from .excel_io import PromptCase
from .llm_client import LLMClient, LLMError, LLMTimeout
from .prompt import build_request
from .cp1 import Cp1
from .schemas import Outcome as Decided, VerdictError, decide, route_for, validate_verdict

Outcome = Literal["valid", "invalid_response", "timeout", "error"]


@dataclass
class CaseResult:
    run_id: str
    prompt_id: str
    prompt: str
    category: str | None
    expected_decision: str | None
    expected_blocked_by: str | None
    outcome: Outcome
    started_at_utc: str
    request_duration_ms: float
    decision: str | None = None
    checks: list[tuple[str, str]] | None = None
    blocked_by: str | None = None
    unclear_at: str | None = None
    request_understood: bool | None = None
    decision_reason: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    raw_response: str | None = None
    server_timing: dict = field(default_factory=dict)
    expected_route: str | None = None
    review_flag: str | None = None
    route_proposed: str | None = None
    route: str | None = None
    route_reason: str | None = None
    info: dict | None = None
    cp1_hit: str | None = None
    model_decision: str | None = None  # before CP1; equals decision when CP1 is off or did not hit

    @property
    def route_correct(self) -> bool | None:
        if self.expected_route is None or self.outcome != "valid" or self.route is None:
            return None
        return self.route == self.expected_route

    @property
    def decision_correct(self) -> bool | None:
        """None = not applicable (no expected value, or no valid decision)."""
        if self.expected_decision is None or self.outcome != "valid":
            return None
        return self.decision == self.expected_decision

    @property
    def blocking_rule_correct(self) -> bool | None:
        if (self.outcome != "valid" or self.expected_decision != "block"
                or self.decision != "block" or not self.expected_blocked_by):
            return None
        return self.blocked_by == self.expected_blocked_by


@lru_cache(maxsize=4)
def _cp1(path: str) -> Cp1:
    return Cp1.load(Path(path))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class JsonlWriter:
    """Appends one line per attempt and flushes it to disk immediately."""

    def __init__(self, path: Path):
        self._fh = open(path, "x", encoding="utf-8")

    def write(self, record: dict) -> None:
        self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())

    def close(self) -> None:
        self._fh.close()


def run_one(case: PromptCase, run_id: str, config: Config, rules: tuple[Rule, ...],
            client: LLMClient, clock: Callable[[], int] = time.perf_counter_ns,
            now: Callable[[], str] = utc_now) -> CaseResult:
    request = build_request(config, rules, case.prompt, case.context)
    started_at = now()

    start_ns = clock()
    try:
        reply, exc = client.chat(request), None
    except Exception as caught:  # KeyboardInterrupt is not caught on purpose
        reply, exc = None, caught
    end_ns = clock()

    base = dict(run_id=run_id, prompt_id=case.prompt_id, prompt=case.prompt, category=case.category,
                expected_decision=case.expected_decision, expected_blocked_by=case.expected_blocked_by,
                started_at_utc=started_at, request_duration_ms=(end_ns - start_ns) / 1_000_000,
                expected_route=case.expected_route, review_flag=case.review_flag)

    if exc is not None:
        outcome: Outcome = "timeout" if isinstance(exc, LLMTimeout) else "error"
        err_type = "timeout" if outcome == "timeout" else (
            "llm_error" if isinstance(exc, LLMError) else type(exc).__name__)
        return CaseResult(**base, outcome=outcome, error_type=err_type, error_message=str(exc))

    # A prompt that filled the whole context was probably truncated: rules may be missing.
    prompt_tokens = (reply.server_timing or {}).get("prompt_eval_count")
    if isinstance(prompt_tokens, int) and prompt_tokens >= config.num_ctx:
        return CaseResult(**base, outcome="error", error_type="context_limit",
                          error_message=f"Prompt füllt den Kontext ({prompt_tokens} >= num_ctx {config.num_ctx}); "
                                        "vermutlich abgeschnitten. num_ctx in der Config erhöhen.",
                          raw_response=reply.content, server_timing=reply.server_timing)

    rule_ids = [r.id for r in rules]
    try:
        verdict = validate_verdict(reply.content, rule_ids, config.request_understood, config.router,
                                   config.router_layout == "vor_regeln_klein")
    except VerdictError as err:
        return CaseResult(**base, outcome="invalid_response", error_type="invalid_response",
                          error_message=str(err), raw_response=reply.content,
                          server_timing=reply.server_timing)

    decided = decide(verdict, rule_ids)
    base["model_decision"] = decided.decision
    if config.router:
        # The rule files put the emergency rule first (order 1).
        route, route_reason = route_for(decided, verdict, rule_ids[0])
        base.update(route_proposed=verdict.route, route=route, route_reason=route_reason,
                    info=verdict.info.model_dump())
    # The model is still called on a CP1 hit, so its own result stays measurable.
    hit = _cp1(config.cp1_patterns).match(case.prompt) if config.cp1_patterns else None
    if hit:
        decided = Decided("block", "CP1", None, f"CP1: {hit}")
        base.update(cp1_hit=hit, **({"route": "notfall", "route_reason": f"CP1: {hit}"} if config.router else {}))
    return CaseResult(**base, outcome="valid", decision=decided.decision,
                      checks=list(verdict.checks.items()),
                      blocked_by=decided.blocked_by, unclear_at=decided.unclear_at,
                      request_understood=verdict.request_understood, decision_reason=decided.reason,
                      raw_response=reply.content, server_timing=reply.server_timing)


def result_record(result: CaseResult) -> dict:
    record = asdict(result)
    record["decision_correct"] = result.decision_correct
    record["blocking_rule_correct"] = result.blocking_rule_correct
    record["route_correct"] = result.route_correct
    return record


def run_cases(cases: list[PromptCase], run_id: str, config: Config, rules: tuple[Rule, ...],
              client: LLMClient, writer: JsonlWriter, results: list[CaseResult],
              clock: Callable[[], int] = time.perf_counter_ns,
              progress: Callable[[int, int, CaseResult], None] | None = None) -> None:
    """Run all cases in order; each case is independent (no shared history).

    Results are appended to ``results`` as they arrive so a caller still holds
    everything finished so far if the run is interrupted.
    """
    for index, case in enumerate(cases, start=1):
        result = run_one(case, run_id, config, rules, client, clock=clock)
        writer.write(result_record(result))
        results.append(result)
        if progress:
            progress(index, len(cases), result)


def warmup(config: Config, rules: tuple[Rule, ...], client: LLMClient,
           clock: Callable[[], int] = time.perf_counter_ns) -> dict:
    """One separate call to load the model; never part of the case statistics."""
    case = PromptCase(row=0, prompt_id="__warmup__", prompt="Wie viele Schritte bin ich heute gegangen?")
    result = run_one(case, "warmup", config, rules, client, clock=clock)
    return {"outcome": result.outcome, "request_duration_ms": round(result.request_duration_ms, 3),
            "error_message": result.error_message}
