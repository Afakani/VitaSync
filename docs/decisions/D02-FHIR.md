---
id: D02
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D02 – FHIR-Version, Ressourcen und erste Messgrößen

**Status: Empfohlen, nicht bestätigt.**

## Ausgangslage

Das Team hat bereits synthetische FHIR-Testdaten. Diese sind die Grundlage; es werden keine eigenen Testdaten generiert, solange die vorhandenen reichen.

## Empfehlung

- **FHIR-Version aus den vorhandenen Testdaten übernehmen** (vermutlich R4). Nicht mischen.
- **Ressourcen im ersten Schritt nur:** `Patient`, `Observation`. Weitere nur, wenn sie in den Testdaten vorkommen und eine eingeplante Story sie braucht.
- **Codierung:** so übernehmen, wie sie in den Testdaten steht (üblich: LOINC für Messgrößen, UCUM für Einheiten). Wert, Einheit, Zeitpunkt und Herkunft immer mitführen.
- **Erste Messgröße:** eine, die in den Testdaten häufig und mit mehreren Zeitpunkten vorkommt. Sie wird **nur angezeigt und rechnerisch ausgewertet**, nicht medizinisch bewertet (siehe Zweckbestimmung: kein Medizinprodukt).
- **Ablage:** Testdaten nach `data/synthetic/fhir/`, mit Herkunftsangabe in `data/synthetic/README.md`.
- **Testserver:** nur falls die Daten über eine FHIR-Schnittstelle gelesen werden sollen, HAPI FHIR per Docker in `infra/`. Sonst reicht das Einlesen der JSON-Dateien (U022).
- **Intern** nicht mit FHIR-Objekten rechnen: `adapters/fhir` übersetzt in interne Modelle aus `core/`.

## FHIR und OMOP (Vorgabe Team, 2026-10-21)

VitaSync nutzt **beide** Standards. Das ist Vorgabe des Teams, nicht nur Empfehlung.

- **FHIR** für Austausch und Abruf einzelner Ressourcen (Patient, Messwerte, Befunde).
- **OMOP CDM** (SQL-Datenbank) für strukturierte, präzise Abfragen über Gesundheitsdaten, z. B. Laborwerte im Zeitverlauf.
- Beide sind **Quelldaten und nur lesbar** (harte Regel 14): VitaSync ruft ab und liest, es schreibt, ändert oder löscht nichts.
- **Eigener Adapter** `adapters/omop` neben `adapters/fhir`; beide übersetzen in dieselben internen Modelle aus `core/`. Features kennen weder FHIR- noch OMOP-Strukturen.
- Herkunft bleibt unterscheidbar (harte Regel 9): jeder Wert trägt, ob er aus FHIR oder OMOP stammt.
- Ablage synthetischer OMOP-Testdaten unter `data/synthetic/omop/`, wie bei FHIR mit Herkunftsangabe.
- Medikationstabellen (z. B. `DRUG_EXPOSURE`) werden nicht abgefragt, solange D08 Medikamente ausschließt.

## Offene Punkte

- Welche FHIR-Version und welche Ressourcen enthalten die vorhandenen Testdaten? Herkunft (selbst erstellt, Generator, Betreuung)?
- Sind die Daten nachweislich synthetisch? Wenn unklar: nicht verwenden.
- OMOP: Welche CDM-Version (vermutlich 5.4), welche Datenbank, woher kommen synthetische OMOP-Testdaten? Wer welche Frage über FHIR und wer über OMOP beantwortet, legt ein eigener Task fest.
- Ordner `adapters/omop` mit `AGENTS.md` wird mit dem ersten OMOP-Task angelegt.

## Betroffen

`contracts/fhir/`, `apps/api/src/vitasync/adapters/fhir/`, `apps/api/src/vitasync/adapters/omop/` (folgt), `features/health_data/`, `data/synthetic/`.
