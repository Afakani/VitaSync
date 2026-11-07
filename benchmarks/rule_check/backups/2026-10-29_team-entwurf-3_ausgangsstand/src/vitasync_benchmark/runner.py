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
from pathlib import Path
from typing import Callable, Literal

from .config import Config, Rule
from .excel_io import PromptCase
from .llm_client import LLMClient, LLMError, LLMTimeout
from .prompt import build_request
from .schemas import VerdictError, decide, validate_verdict

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
    error_type: str | None = None
    error_message: str | None = None
    raw_response: str | None = None
    server_timing: dict = field(default_factory=dict)

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
                started_at_utc=started_at, request_duration_ms=(end_ns - start_ns) / 1_000_000)

    if exc is not None:
        outcome: Outcome = "timeout" if isinstance(exc, LLMTimeout) else "error"
        err_type = "timeout" if outcome == "timeout" else (
            "llm_error" if isinstance(exc, LLMError) else type(exc).__name__)
        return CaseResult(**base, outcome=outcome, error_type=err_type, error_message=str(exc))

    rule_ids = [r.id for r in rules]
    try:
        verdict = validate_verdict(reply.content, rule_ids)
    except VerdictError as err:
        return CaseResult(**base, outcome="invalid_response", error_type="invalid_response",
                          error_message=str(err), raw_response=reply.content,
                          server_timing=reply.server_timing)

    decided = decide(verdict, rule_ids)
    return CaseResult(**base, outcome="valid", decision=decided.decision,
                      checks=list(verdict.checks.items()),
                      blocked_by=decided.blocked_by, unclear_at=decided.unclear_at,
                      raw_response=reply.content, server_timing=reply.server_timing)


def result_record(result: CaseResult) -> dict:
    record = asdict(result)
    record["decision_correct"] = result.decision_correct
    record["blocking_rule_correct"] = result.blocking_rule_correct
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
