---
tags: [vitasync, prozess]
---

# Arbeitsablauf im Team

## Wo steht was
- **Plan:** `planning/VitaSync_Coding_Backlog.xlsx` (Stories, Tasks, Briefings). Wird selten geändert.
- **Status:** Spalte „Status“ im Blatt **Tasks** des Backlogs. Genau eine Statusquelle. GitHub Issues sind optional und dienen der Diskussion, nicht der Statusführung.
- **Auftrag an Claude/Codex:** Issue-Text oder `planning/work-orders/<TASK-ID>.md`.
- **Übergabe bei Unterbrechung:** `planning/handoffs/<TASK-ID>.md`.

## Ablauf pro Task
1. Task ist „Bereit“: Voraussetzungen erledigt, nötige Entscheidungen bestätigt.
2. Mensch weist sich (oder Claude/Codex mit sich als Verantwortlichem) im Issue zu.
3. Branch `task/<TASK-ID>-<kurzname>`, Arbeit, Tests.
4. PR mit Vorlage. Im selben PR die eigene Zeile im Blatt Tasks auf „Im Review“ setzen.
5. Andere Person reviewt. CODEOWNERS fordert automatisch den Modulverantwortlichen an.
6. Nach der Freigabe im selben PR ein letzter Commit: Status „Erledigt“, PR-Nummer in die Spalte „Änderung“. Danach mergen. Kein eigener PR nur für die Statusänderung.

## Testlauf

Solange [[D10-Testlauf]] gilt, übernimmt **eine Person alle Rollen**: Umsetzung, Review und Merge.

- **Review heißt dann: die eigene Durchsicht des Diffs im PR vor dem Merge.** Nicht übersprungen, nur von
  derselben Person. Was auffällt, wird vor dem Merge behoben oder im PR als offener Punkt benannt.
- **Branch und PR bleiben Pflicht**, auch für reine Doku- und Prüfaufträge. Der PR ist der Ort, an dem der
  Diff am Stück lesbar ist; ohne ihn gibt es keine Durchsicht.
- **Branch-Schutz wird erst mit CI eingerichtet** (F004). Vorher würde er nur den einzigen Weg blockieren,
  ohne etwas zu prüfen.
- Fachliche Inhalte mit `status: testfreigabe` sind **nicht** fachlich geprüft. Sie werden nur bei
  `APP_ENV=development` geladen und in der Antwort gekennzeichnet. Die Durchsicht durch eine Person
  ersetzt keine fachliche Freigabe nach [[D04-Fachinhalte]].

Sobald eine fachliche Reviewerin oder ein fachlicher Reviewer benannt ist, endet der Testlauf und dieser
Abschnitt entfällt.

## Parallel arbeiten
Tasks in verschiedenen Fachbereichen (`features/<x>`) können parallel laufen. Tasks im selben Fachbereich oder mit Änderungen an `contracts/` oder `core/` vorher im Team abstimmen.

## Verknüpft
- [[Architektur]]
- [[Start]]
- [[D10-Testlauf]]
