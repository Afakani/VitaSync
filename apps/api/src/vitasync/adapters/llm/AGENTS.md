# Modul: LLM-Adapter

Zweck: Implementiert den LLM-Port für die lokale Laufzeit und einen Fake für Tests; lädt versionierte Prompts.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `core/`, Schemas aus `contracts/llm/`.
- Darf nicht: Fachentscheidungen treffen; Prompts mit echten Gesundheitsdaten als Beispiel.

## Verträge
- Siehe [D03](../../../../../../docs/decisions/D03-Modell.md).
- Prompts in `prompts/`, Dateiname mit Version (`recognition.v1.md`). Geänderter Prompt = neue Version, alte bleibt bis zur Umstellung.

## Tests
- Fake-Adapter für Unit-Tests. Prompt-Änderungen gegen `evals/` prüfen und Ergebnis im PR nennen.

## Fallen
- Timeout und ungültiges JSON sind Normalfälle, keine Ausnahmen.
- Modellname, Endpunkt und Grenzen nur aus der Konfiguration (`.env`), nie im Code. Modellwechsel = Konfiguration ändern + Evals laufen lassen.
- Kein Feature darf Eigenheiten eines bestimmten Modells voraussetzen (Sonderformate, Tags). Solche Anpassungen bleiben in diesem Adapter.
