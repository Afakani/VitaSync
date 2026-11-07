import pytest

from conftest import write_xlsx
from vitasync_benchmark.excel_io import InputError, read_prompts

IDS = ["R01", "R02", "R03"]


def test_reads_valid_rows_and_skips_empty(tmp_path):
    path = write_xlsx(tmp_path / "in.xlsx", [
        ("P1", "Frage eins", "FAQ", "allow", None, None),
        (None, None, None, None, None, None),
        ("P2", "Frage zwei", None, "block", "R02",
         '[{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hallo"}]'),
    ])
    cases = read_prompts(path, IDS)
    assert [c.prompt_id for c in cases] == ["P1", "P2"]
    assert cases[1].context[1] == {"role": "assistant", "content": "hallo"}


@pytest.mark.parametrize("row,reason", [
    (("P1", None, None, None, None, None), "prompt leer"),
    ((None, "Text", None, None, None, None), "prompt_id leer"),
    (("P1", "Text", None, "maybe", None, None), "expected_decision"),
    (("P1", "Text", None, "allow", "R02", None), "nicht block"),
    (("P1", "Text", None, "block", "R99", None), "keine geprüfte"),
    (("P1", "Text", None, None, None, '[{"role": "system", "content": "x"}]'), "nicht erlaubt"),
    (("P1", "Text", None, None, None, "kein json"), "context_json"),
])
def test_bad_rows_reported(tmp_path, row, reason):
    path = write_xlsx(tmp_path / "in.xlsx", [row])
    with pytest.raises(InputError, match=reason):
        read_prompts(path, IDS)


def test_duplicate_ids_reported(tmp_path):
    path = write_xlsx(tmp_path / "in.xlsx", [("P1", "a", None, None, None, None),
                                              ("P1", "b", None, None, None, None)])
    with pytest.raises(InputError, match="doppelt"):
        read_prompts(path, IDS)


def test_missing_sheet_and_columns(tmp_path):
    with pytest.raises(InputError, match="Blatt"):
        read_prompts(write_xlsx(tmp_path / "a.xlsx", [], sheet="Other"), IDS)
    with pytest.raises(InputError, match="Pflichtspalten"):
        read_prompts(write_xlsx(tmp_path / "b.xlsx", [("x",)], header=("prompt_id",)), IDS)
