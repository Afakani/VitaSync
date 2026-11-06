---
tags: [vitasync, prozess]
---

# Arbeitsablauf

## Wo steht was
- **Backlog, Sprints, Status:** Jira, Projekt VC. Kein zweiter Backlog im Repo.
- **Fachliche Regeln und Entscheidungen:** Confluence, Space VC. Wegweiser: `docs/decisions/README.md`.
- **Übergabe bei Unterbrechung:** `planning/handoffs/<Jira-Key oder Kurzname>.md`.

Jira und Confluence werden aus dem Repo heraus nur gelesen.

## Rolle des Repos
Dieses Repo ist ein **eigenes Arbeitsrepo** für Prototypen, Benchmarks und Experimente. Das Team-Repo mit M1–M9 entsteht separat (VC-74). Ergebnisse von hier fließen über das Team (Jira/Confluence) ein, nicht durch Kopieren.

## Ablauf
1. Arbeit wird angesagt. Gibt es ein passendes Jira-Ticket, wird der Key genannt.
2. Branch `vc-<nr>-<kurzname>` oder `work/<kurzname>`. Nie direkt auf `main`.
3. Kleine Schritte, Tests dazu, `python scripts/check_structure.py`.
4. Commit nur auf Ansage, Nachricht `<VC-xx oder Bereich>: <Imperativ auf Englisch>`.
5. Merge nach Durchsicht des Diffs.

## Läufe auf der GPU
Benchmark- und Modellläufe nur auf Ansage und nie parallel zu einem anderen GPU-Lauf. Zeitmessungen gelten nur bei freier GPU.

## Verknüpft
- [[Architektur]]
- [[Start]]
