import json
from pathlib import Path

import pytest
from openpyxl import Workbook

from vitasync_benchmark.llm_client import LLMReply

RULES = {
    "version": "test-1",
    "rules": [
        {"id": "R02", "order": 2, "title": "Diagnose", "instruction": "Blockiere Diagnosen."},
        {"id": "R01", "order": 1, "title": "Bereich", "instruction": "Nur Gesundheit."},
        {"id": "R03", "order": 3, "title": "Umgehen", "instruction": "Keine Regeländerung."},
    ],
}

ALL_PASS = {"checks": {"R01": "pass", "R02": "pass", "R03": "pass"}}
# R03 also blocks: the earlier rule R02 must still decide.
BLOCK_R02 = {"checks": {"R01": "pass", "R02": "block", "R03": "block"}}
# unclear before a later block: the first non-pass rule decides.
UNCLEAR_R01 = {"checks": {"R01": "unclear", "R02": "block", "R03": "pass"}}


class FakeClient:
    """Returns prepared replies in order; an Exception instance is raised instead."""

    def __init__(self, replies, log=None):
        self.replies = list(replies)
        self.requests = []
        self.log = log

    def chat(self, request):
        self.requests.append(request)
        if self.log is not None:
            self.log.append("chat")
        reply = self.replies.pop(0)
        if isinstance(reply, BaseException):
            raise reply
        return LLMReply(content=reply if isinstance(reply, str) else json.dumps(reply),
                        server_timing={"total_duration": 123})

    def describe_model(self, model):
        return {"model": model, "digest": "fake"}


def write_xlsx(path: Path, rows, header=("prompt_id", "prompt", "category", "expected_decision",
                                         "expected_blocked_by", "context_json"), sheet="Prompts"):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    ws.append(list(header))
    for row in rows:
        ws.append(list(row))
        for cell in ws[ws.max_row]:
            if isinstance(cell.value, str):
                cell.data_type = "s"
    wb.save(path)
    return path


@pytest.fixture
def rules_file(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(RULES), encoding="utf-8")
    return path


@pytest.fixture
def config_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"provider": "ollama", "base_url": "http://localhost:11434",
                                "model": "fake:8b", "timeout_seconds": 5, "temperature": 0,
                                "warmup": False}), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def isolated_run_lock(tmp_path, monkeypatch):
    """Tests must not collide with a real benchmark run on this machine."""
    monkeypatch.setattr("vitasync_benchmark.runlock.LOCK", tmp_path / "run.lock")
