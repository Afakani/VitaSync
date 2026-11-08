# Modul: Chat (Orchestrierung)

Zweck: Nimmt eine Nachricht an, ruft Erkennung, ggf. Daten und Hinweise auf, baut die Antwort, verwaltet Chatkontext und offene Rückfragen.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `input_guard`, `recognition`, `rule_pipeline`, `routing`, `safety_net`, `guidance`, `health_data`, `consent` (je öffentliche Funktionen), `core/`.
- Darf nicht: Selbst Gesundheitsinhalte formulieren; Profil- oder Messdaten zur Bewertung in den Prompt geben (R1–R6).

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- `route_message(text, guard, recognize, policy, net)`: CP1 → Erkennung (SLM oder LLM) → Regel-Pipeline → Routing → CP2 → `RouteDecision`. Bei CP1-Treffer kein Modellaufruf; ungültige LLM-Ausgabe → SAFE_DEFAULT. Reihenfolge wie Team-Router v0.5.

## Tests
- `apps/api/tests/features/chat/`. Verhalten testen, nicht Implementierung spiegeln.

## Fallen
- Wiederholte Anfrage (gleiche Request-ID) darf keine doppelte Antwort erzeugen.
- Kontext gilt nur innerhalb eines Chats.
