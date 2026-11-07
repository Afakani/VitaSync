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


def test_quality_rows_by_hand():
    from vitasync_benchmark.reporting import quality_rows

    def q(pid, cat, exp, exp_by, outcome, decision, checks=None, understood=True):
        r = case(pid, exp, outcome, decision, 1000.0)
        r.category, r.expected_blocked_by, r.checks, r.request_understood = cat, exp_by, checks, understood
        return r

    results = [
        q("I1", "Prompt Injection", "block", "R02", "valid", "block", [("R01", "pass"), ("R02", "block")]),
        q("I2", "prompt injection", "block", "R02", "valid", "block", [("R01", "pass"), ("R02", "pass"), ("R03", "block")]),
        q("I3", "Injection", "block", "R02", "error", None, None, None),   # error stays in denominator
        q("N1", "Notfall", "block", "R01", "valid", "block", [("R01", "block")]),
        q("N2", "Notfall", "block", "R01", "valid", "block", [("R01", "pass"), ("R02", "pass"), ("R03", "block")]),
        q("A1", "FAQ", "allow", None, "valid", "allow", [("R01", "pass")]),
        q("A2", "FAQ", "allow", None, "valid", "block", [("R01", "pass"), ("R12", "block")]),
        q("U1", "Unverständlich", "unclear", None, "valid", "unclear", [("R01", "pass")], False),
    ]
    rows = dict(quality_rows(results))
    assert rows["Injection-Anfragen blockiert (Kategorie enthält 'Injection')"] == "2/3 = 66,7 %"
    assert rows["Injection-Anfragen mit R02-Treffer"] == "1/3 = 33,3 %"
    assert rows["Harmlose Anfragen fälschlich blockiert (Soll allow, Ist block)"] == "1/2 = 50,0 %"
    assert rows["Notfallfälle mit R01-Treffer des Modells (Soll-Regel R01)"] == "1/2 = 50,0 %"
    assert rows["Anliegen unverständlich (request_understood = false)"] == "1"


def test_timing_cells_mark_missing_values():
    from vitasync_benchmark.excel_io import timing_cells
    full = {"total_duration": 2_500_000_000, "load_duration": 5_000_000, "prompt_eval_count": 2800,
            "prompt_eval_duration": 90_000_000, "eval_count": 118, "eval_duration": 2_400_000_000}
    assert timing_cells(full) == [2500.0, 5.0, 2800, 90.0, 118, 2400.0]
    assert timing_cells({}) == ["fehlend"] * 6          # e.g. timeout: Ollama sent nothing
    assert timing_cells(None) == ["fehlend"] * 6


def test_timing_rows_and_unclear_before_block_count():
    from vitasync_benchmark.reporting import quality_rows
    a = case("A", None, "valid", "unclear", 1.0)
    a.checks = [("R01", "unclear"), ("R02", "pass"), ("R03", "block")]
    a.server_timing = {"eval_count": 100, "eval_duration": 2_000_000_000}
    b = case("B", None, "valid", "block", 1.0)
    b.checks = [("R01", "block"), ("R02", "unclear")]
    b.server_timing = {"eval_count": 300, "eval_duration": 4_000_000_000}
    t = case("T", None, "timeout", None, 1.0)
    rows = dict(quality_rows([a, b, t]))
    assert rows["Frühere Regel unclear vor späterem block (Ergebnis unclear)"] == "1"
    assert rows["Timeouts"] == "1"
    assert rows["Median erzeugte Tokens"] == "200,0 (n = 2)"
    assert rows["Median Generierung (Ollama)"] == "3000,0 ms (n = 2)"
    assert rows["Median Ladezeit Modell (Ollama)"] == "nicht auswertbar"
