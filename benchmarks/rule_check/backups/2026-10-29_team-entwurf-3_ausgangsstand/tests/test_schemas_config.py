import json

import pytest

from conftest import ALL_PASS, BLOCK_R02, UNCLEAR_R01
from vitasync_benchmark.config import ConfigError, load_config, load_rules
from vitasync_benchmark.schemas import VerdictError, decide, response_json_schema, validate_verdict

IDS = ["R01", "R02", "R03"]


@pytest.mark.parametrize("verdict,decision,blocked_by,unclear_at", [
    (ALL_PASS, "allow", None, None),
    (BLOCK_R02, "block", "R02", None),
    (UNCLEAR_R01, "unclear", None, "R01"),
    ({"checks": {"R01": "pass", "R02": "pass", "R03": "block"}}, "block", "R03", None),
])
def test_first_non_pass_rule_decides(verdict, decision, blocked_by, unclear_at):
    outcome = decide(validate_verdict(json.dumps(verdict), IDS), IDS)
    assert (outcome.decision, outcome.blocked_by, outcome.unclear_at) == (decision, blocked_by, unclear_at)


@pytest.mark.parametrize("raw,reason", [
    ('{"checks": {"R01": "pass", "R02": "pass", "R03": "pass", "R09": "pass"}}', "unbekannte"),
    ('{"checks": {"R01": "pass", "R03": "block"}}', "fehlen"),
    ('{"checks": {"R02": "pass", "R01": "pass", "R03": "pass"}}', "Regelreihenfolge"),
    ('{"checks": {"R01": "pass", "R01": "block", "R02": "pass", "R03": "pass"}}', "doppelte"),
    ('{"checks": {"R01": "pass", "R02": "maybe", "R03": "pass"}}', "Schema"),
])
def test_inconsistent_verdicts_rejected(raw, reason):
    with pytest.raises(VerdictError, match=reason):
        validate_verdict(raw, IDS)


@pytest.mark.parametrize("raw", ["kein json", "```json\n{}\n```", "{}",
                                 json.dumps({**ALL_PASS, "decision": "allow"}),
                                 json.dumps({"checks": [{"rule_id": "R01", "status": "pass"}]})])
def test_malformed_or_extra_fields_rejected(raw):
    with pytest.raises(VerdictError):
        validate_verdict(raw, IDS)


def test_schema_requires_all_rules_in_order():
    checks = response_json_schema(IDS)["properties"]["checks"]
    assert list(checks["properties"]) == IDS and checks["required"] == IDS
    assert checks["additionalProperties"] is False


def test_rules_sorted_and_hashed(rules_file):
    ruleset, digest = load_rules(rules_file)
    assert [r.id for r in ruleset.input_rules] == IDS
    assert len(digest) == 64


@pytest.mark.parametrize("rules", [
    [],
    [{"id": "R01", "order": 1, "title": "a", "instruction": "b"},
     {"id": "R01", "order": 2, "title": "a", "instruction": "b"}],
    [{"id": "R01", "order": 1, "title": "a", "instruction": "b"},
     {"id": "R02", "order": 1, "title": "a", "instruction": "b"}],
    [{"id": "R01", "order": 1, "title": "a", "instruction": "   "}],
    [{"id": "R01", "order": 1, "title": "a"}],
    [{"id": "A01", "order": 1, "title": "a", "instruction": "b", "scope": "answer"}],
])
def test_bad_rule_files_rejected(tmp_path, rules):
    path = tmp_path / "r.json"
    path.write_text(json.dumps({"version": "x", "rules": rules}), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_rules(path)


def test_answer_rules_kept_apart(tmp_path):
    path = tmp_path / "r.json"
    path.write_text(json.dumps({"version": "x", "rules": [
        {"id": "R01", "order": 1, "title": "a", "instruction": "b"},
        {"id": "A01", "order": 2, "title": "a", "instruction": "b", "scope": "answer"}]}), encoding="utf-8")
    ruleset, _ = load_rules(path)
    assert [r.id for r in ruleset.input_rules] == ["R01"]
    assert [r.id for r in ruleset.answer_rules] == ["A01"]


def test_placeholder_model_rejected(tmp_path):
    path = tmp_path / "c.json"
    path.write_text(json.dumps({"provider": "ollama", "base_url": "x", "model": "<MODELLNAME-SETZEN>",
                                "timeout_seconds": 5}), encoding="utf-8")
    with pytest.raises(ConfigError, match="Platzhalter"):
        load_config(path)
