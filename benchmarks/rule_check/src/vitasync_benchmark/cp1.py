"""CP1 prototype: fixed emergency and crisis patterns checked in code, before any model judgement.

A hit always routes to the emergency notice, whatever the model answers; a miss is
no all-clear. The patterns are unchecked benchmark material, not product content.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import ConfigError


class Cp1:
    def __init__(self, patterns: dict[str, str]):
        self._patterns = {name: re.compile(p, re.IGNORECASE) for name, p in patterns.items()}

    @classmethod
    def load(cls, path: Path) -> "Cp1":
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            return cls(data["muster"])
        except (OSError, KeyError, json.JSONDecodeError, re.error) as exc:
            raise ConfigError(f"CP1-Musterdatei unbrauchbar ({path}): {exc}") from exc

    def match(self, text: str) -> str | None:
        """Name of the first matching category, or None."""
        for name, pattern in self._patterns.items():
            if pattern.search(text):
                return name
        return None
