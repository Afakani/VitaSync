# Modul: LLM-Adapter

Zweck: Implementiert den LLM-Port für die lokale Laufzeit und einen Fake für Tests; lädt versionierte Prompts.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `core/`, Schemas aus `contracts/llm/`.
- Darf nicht: Fachentscheidungen treffen; Prompts mit echten Gesundheitsdaten als Beispiel.

## Verträge
- Siehe [Modell (ADR Self-hosted LLM, VC-62)](../../../../../../docs/decisions/README.md).
- `OllamaIntentExtractor` implementiert `IntentExtractorPort` (nur Rohausgabe; geprüft wird in `features/recognition`). `FakeIntentExtractor` + `flags_json` für Tests.
- Prompt `prompts/intent_flags.v1.md` (wortgleich aus dem Team-Router), Schema `contracts/llm/intent_flags.v1.schema.json`.
- Prompts in `prompts/`, Dateiname mit Version (`intent_flags.v1.md`). Geänderter Prompt = neue Version, alte bleibt bis zur Umstellung.

## Tests
- Fake-Adapter für Unit-Tests. Prompt-Änderungen gegen `evals/` prüfen und Ergebnis im PR nennen.

## Fallen
- Timeout und ungültiges JSON sind Normalfälle, keine Ausnahmen.
- Modellname, Endpunkt und Grenzen nur aus der Konfiguration (`.env`), nie im Code. Modellwechsel = Konfiguration ändern + Evals laufen lassen.
- Kein Feature darf Eigenheiten eines bestimmten Modells voraussetzen (Sonderformate, Tags). Solche Anpassungen bleiben in diesem Adapter.
- Unter Windows nie `localhost` als Ollama-Adresse: "localhost" wird zuerst als IPv6 `::1` aufgelöst, Ollama hört nur auf IPv4, jeder Aufruf wartet ~2,1 s. Immer `http://127.0.0.1:11434` (gemessen 08.11.2026: 2.123 ms gegenüber 82 ms je Embedding).
