from openpyxl import load_workbook

from conftest import ALL_PASS, BLOCK_R02, FakeClient, write_xlsx
from vitasync_benchmark import cli
from vitasync_benchmark.reporting import NOT_EVALUABLE, OVERVIEW_NOTE, overview
from vitasync_benchmark.runner import CaseResult


def case(pid, expected, outcome, decision, ms):
    return CaseResult(run_id="r", prompt_id=pid, prompt="x", category=None, expected_decision=expected,
                      expected_blocked_by=None, outcome=outcome, started_at_utc="t",
                      request_duration_ms=ms, decision=decision)


def test_overview_numbers_by_hand():
    results = [
        case("A", "allow", "valid", "allow", 1000.0),   # correct
        case("B", "allow", "valid", "block", 3000.0),   # wrong
        case("C", "block", "valid", "block", 2000.0),   # correct
        case("D", "block", "timeout", None, 5000.0),    # technical error stays in the denominator
        case("E", None, "valid", "allow", 4000.0),      # no expected value
    ]
    rows = dict(overview(results, loaded=6))            # one loaded case not executed
    assert rows["Geladene Testfälle"] == "6"
    assert rows["Ausgeführte Testfälle"] == "5"
    assert rows["Nicht ausgeführte Testfälle"] == "1"
    assert rows["Technisch gültige Antworten"] == "4/5 = 80,0 %"
    assert rows["Technische Fehler"] == "invalid_response 0, timeout 1, error 0"
    assert rows["Fälle ohne Sollwert (nicht in Entscheidungsquoten)"] == "1"
    assert rows["Entscheidung entspricht dem eingetragenen Sollwert"] == "2/4 = 50,0 %"
    assert rows["Erlaubte Anfragen korrekt zugelassen"] == "1/2 = 50,0 %"
    assert rows["Zu blockierende Anfragen tatsächlich blockiert"] == "1/2 = 50,0 %"
    assert rows["Mehrdeutige Anfragen als unclear erkannt"] == NOT_EVALUABLE  # class not represented
    # durations of the four valid calls only: 1, 3, 2, 4 s; the 5 s timeout is excluded
    n = "(n = 4 gültige Aufrufe)"
    assert rows["Durchschnittliche Aufrufdauer"] == f"2,500 s {n}"
    assert rows["Median der Aufrufdauer"] == f"2,500 s {n}"
    assert rows["Minimale / maximale Aufrufdauer"] == f"1,000 s / 4,000 s {n}"


def test_overview_one_decimal_and_empty_run():
    results = [case(p, "allow", "valid", "allow" if i < 2 else "block", 1234.5678) for i, p in enumerate("XYZ")]
    rows = dict(overview(results, 3))
    assert rows["Erlaubte Anfragen korrekt zugelassen"] == "2/3 = 66,7 %"
    assert rows["Median der Aufrufdauer"].startswith("1,235 s")
    empty = dict(overview([], 0))
    assert empty["Technisch gültige Antworten"] == NOT_EVALUABLE
    assert empty["Durchschnittliche Aufrufdauer"] == NOT_EVALUABLE


def test_overview_on_top_of_summary_sheet(tmp_path, rules_file, config_file):
    inp = write_xlsx(tmp_path / "in.xlsx", [("P1", "a", None, "allow", None, None),
                                            ("P2", "b", None, "block", "R02", None)])
    cli.main(["--input", str(inp), "--rules", str(rules_file), "--config", str(config_file),
              "--output-dir", str(tmp_path / "out")], client_factory=lambda c: FakeClient([ALL_PASS, BLOCK_R02]))
    ws = load_workbook(next((tmp_path / "out").iterdir()) / "results.xlsx")["Summary"]
    column_a = [c.value for c in ws["A"]]
    assert (ws["A1"].value, ws["B1"].value) == ("Kennzahl", "Ergebnis")
    assert ws["B8"].value == "2/2 = 100,0 %"  # decision matches expected value
    assert OVERVIEW_NOTE in column_a
    detail = column_a.index("Bereich")  # detail table kept below the overview
    assert detail > column_a.index(OVERVIEW_NOTE) and "Umfang" in column_a[detail:]
