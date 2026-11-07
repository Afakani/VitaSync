"""Load and validate the run configuration and the rule file."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


class ConfigError(Exception):
    """Configuration or rule file is unusable; raised before any model call."""


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: Literal["ollama"]
    base_url: str = Field(min_length=1)
    model: str = Field(min_length=1)
    timeout_seconds: float = Field(gt=0)
    temperature: float = Field(default=0, ge=0)
    think: bool = False
    warmup: bool = False

    @field_validator("model")
    @classmethod
    def _model_set(cls, value: str) -> str:
        if value.startswith("<"):
            raise ValueError("Modellname ist noch der Platzhalter; in der Config einen echten Namen setzen, z. B. qwen3:8b")
        return value


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")
    order: int
    title: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    # "input" rules judge the user message; "answer" rules need a finished chatbot
    # answer, which this benchmark never produces, so they are reported but not sent.
    scope: Literal["input", "answer"] = "input"
    allowed_examples: tuple[str, ...] = ()
    blocked_examples: tuple[str, ...] = ()
    unclear_examples: tuple[str, ...] = ()

    @field_validator("title", "instruction")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("darf nicht leer sein")
        return value


class RuleSet(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    version: str = Field(min_length=1)
    rules: tuple[Rule, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique(self) -> "RuleSet":
        ids = [r.id for r in self.rules]
        orders = [r.order for r in self.rules]
        if len(set(ids)) != len(ids):
            raise ValueError(f"doppelte Regel-IDs: {sorted({i for i in ids if ids.count(i) > 1})}")
        if len(set(orders)) != len(orders):
            raise ValueError(f"doppelte order-Werte: {sorted({o for o in orders if orders.count(o) > 1})}")
        if not self.input_rules:
            raise ValueError("keine Eingaberegel (scope 'input') vorhanden")
        return self

    @property
    def ordered(self) -> tuple[Rule, ...]:
        return tuple(sorted(self.rules, key=lambda r: r.order))

    @property
    def input_rules(self) -> tuple[Rule, ...]:
        return tuple(r for r in self.ordered if r.scope == "input")

    @property
    def answer_rules(self) -> tuple[Rule, ...]:
        return tuple(r for r in self.ordered if r.scope == "answer")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_json(path: Path, what: str) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"{what} nicht gefunden: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{what} ist kein gültiges JSON: {path}: {exc}") from exc


def load_config(path: Path) -> Config:
    try:
        return Config.model_validate(_load_json(path, "Config"))
    except ValidationError as exc:
        raise ConfigError(f"Config ungültig ({path}):\n{exc}") from exc


def load_rules(path: Path) -> tuple[RuleSet, str]:
    """Return the validated rule set and the SHA-256 of the exact file that was read."""
    raw = Path(path).read_bytes() if Path(path).is_file() else None
    if raw is None:
        raise ConfigError(f"Regeldatei nicht gefunden: {path}")
    try:
        ruleset = RuleSet.model_validate(json.loads(raw.decode("utf-8")))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Regeldatei ist kein gültiges JSON: {exc}") from exc
    except ValidationError as exc:
        raise ConfigError(f"Regeldatei ungültig ({path}):\n{exc}") from exc
    return ruleset, hashlib.sha256(raw).hexdigest()
