"""CP1 input guard: fixed patterns for emergency, crisis and prompt injection. No LLM.

Patterns are data, not code: a JSON file with sections `emergency`, `crisis`, `injection`, each a list
of {"id", "pattern"} (Python regex on normalised text). Default file: knowledge/rules/cp1_patterns.json
(team draft, not medically reviewed). A miss is never an all-clear.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from vitasync.core.intent import GuardResult

_UMLAUTS = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})
_SECTIONS = ("emergency", "crisis", "injection")


def normalise(text: str) -> str:
    """Lower case, umlauts as ae/oe/ue/ss, everything except a-z0-9 to single spaces."""
    text = (text or "").lower().translate(_UMLAUTS)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


class InputGuard:
    """Loaded CP1 patterns. Build once, call `check` per message."""

    def __init__(self, patterns: dict):
        """Args: patterns: parsed pattern file. Raises ValueError on a missing id or a bad regex."""
        self.version = str(patterns.get("version", "?"))
        self._sections: dict[str, list[tuple[str, re.Pattern]]] = {}
        for section in _SECTIONS:
            compiled = []
            for entry in patterns.get(section, []):
                if not entry.get("id"):
                    raise ValueError(f"CP1 pattern without id in section {section}")
                try:
                    compiled.append((entry["id"], re.compile(entry["pattern"])))
                except (KeyError, re.error) as e:
                    raise ValueError(f"CP1 pattern {entry['id']} invalid: {e}") from e
            self._sections[section] = compiled

    @classmethod
    def from_file(cls, path: Path | str) -> "InputGuard":
        """Load patterns from a JSON file. Raises OSError, json.JSONDecodeError or ValueError."""
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def check(self, text: str) -> GuardResult:
        """Return the ids of all patterns that hit. The text itself is not stored."""
        norm = normalise(text)
        hits = {s: tuple(pid for pid, rx in self._sections[s] if rx.search(norm)) for s in _SECTIONS}
        return GuardResult(**hits)
