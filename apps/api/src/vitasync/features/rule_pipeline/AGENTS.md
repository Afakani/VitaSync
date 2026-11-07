# Modul: Regel-Pipeline

Zweck: Macht aus den geprüften Flags der Erkennung das Regelergebnis (Regel-JSON): `crisis | emergency | block | allow | unclear`, mit Regel (R1, R2, R4, R5, R6), Sub-Label und Gründen. Wählt keinen Weg.
Zuständig: Atakan Cubukcu

## Grenzen
- Darf nutzen: `core/intent.py` (Flags, `RuleResult`, `Policy`).
- Darf nicht: LLM aufrufen; Text der Nachricht lesen; einen Weg (DATA_QUERY …) wählen, das macht `routing`; andere Features importieren.

## Verträge
- Öffentlich: `check_rules(flags, policy) -> RuleResult`. `RuleResult.to_dict()` ist das Regel-JSON.
- Reihenfolge: Krise → Notfall → ausdrückliche verbotene Frage (Priorität `SUB_LABEL_PRIORITY`) → Symptom ohne verbotene Frage (Policy) → eigene Erkrankung genannt (Policy) → erlaubt oder unklar.
- Logik 1:1 aus dem Team-Router (`vitasync-router.zip`, `rule_route`). Gleichheit am 07.11.2026 geprüft: 1000/1000 aufgezeichnete Fälle (Batch 1 streng und gelockert, Batch 2 und 3 gelockert) mit gleicher Route und gleichem Sub-Label.
- Policy-Schalter für offene Teamentscheidungen (ADR-0004, VC-84): `ROUTER_POLICY` in `.env`.

## Tests
- `cd apps/api && .venv/Scripts/python.exe -m pytest tests/features/rule_pipeline`

## Fallen
- Krise und Notfall müssen vor allen anderen Prüfungen stehen; eine verbotene Frage darf einen Notfall nie verdecken.
- Fehlt ein Flag, ist das ein Fehler (`KeyError`), kein `false`: Flags kommen nur geprüft aus `recognition`.
