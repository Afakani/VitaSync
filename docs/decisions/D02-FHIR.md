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

## Offene Punkte

- Welche FHIR-Version und welche Ressourcen enthalten die vorhandenen Testdaten? Herkunft (selbst erstellt, Generator, Betreuung)?
- Sind die Daten nachweislich synthetisch? Wenn unklar: nicht verwenden.

## Betroffen

`contracts/fhir/`, `apps/api/src/vitasync/adapters/fhir/`, `features/health_data/`, `data/synthetic/`.
