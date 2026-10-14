---
tags: [vitasync, prozess]
---

# Arbeitsablauf im Team

## Wo steht was
- **Plan:** `planning/VitaSync_Coding_Backlog.xlsx` (Stories, Tasks, Briefings). Wird selten geändert.
- **Status und Zuweisung:** GitHub Issues, ein Issue pro Task-ID (Vorlage „Task“). Assignee = wer arbeitet. Das GitHub-Projektboard zeigt die Statusspalten. Damit gibt es genau eine Statusquelle.
- **Auftrag an Claude/Codex:** Issue-Text oder `planning/work-orders/<TASK-ID>.md`.
- **Übergabe bei Unterbrechung:** `planning/handoffs/<TASK-ID>.md`.

## Ablauf pro Task
1. Task ist „Bereit“: Voraussetzungen erledigt, nötige Entscheidungen bestätigt.
2. Mensch weist sich (oder Claude/Codex mit sich als Verantwortlichem) im Issue zu.
3. Branch `task/<TASK-ID>-<kurzname>`, Arbeit, Tests.
4. PR mit Vorlage, verknüpft mit dem Issue. Status „Im Review“.
5. Andere Person reviewt. CODEOWNERS fordert automatisch den Modulverantwortlichen an.
6. Merge → Issue schließt → „Erledigt“.

## Parallel arbeiten
Tasks in verschiedenen Fachbereichen (`features/<x>`) können parallel laufen. Tasks im selben Fachbereich oder mit Änderungen an `contracts/` oder `core/` vorher im Team abstimmen.

## Verknüpft
- [[Architektur]]
- [[Start]]
