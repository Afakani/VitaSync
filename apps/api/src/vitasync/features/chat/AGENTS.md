# Modul: Chat (Orchestrierung)

Zweck: Nimmt eine Nachricht an, ruft Erkennung, ggf. Daten und Hinweise auf, baut die Antwort, verwaltet Chatkontext und offene Rückfragen.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `input_guard`, `recognition`, `rule_pipeline`, `routing`, `guidance`, `health_data`, `consent` (je öffentliche Funktionen), `core/`.
- Darf nicht: Selbst Gesundheitsinhalte formulieren; Profil- oder Messdaten zur Bewertung in den Prompt geben (R1–R6).

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- `route_message(text, guard, extractor, policy)`: CP1 → Erkennung (eine Wiederholung) → Regel-Pipeline → Routing → `RouteDecision`. Bei CP1-Treffer kein Modellaufruf; ungültige Modellausgabe → SAFE_DEFAULT.

## Tests
- `apps/api/tests/features/chat/`. Verhalten testen, nicht Implementierung spiegeln.

## Fallen
- Wiederholte Anfrage (gleiche Request-ID) darf keine doppelte Antwort erzeugen.
- Kontext gilt nur innerhalb eines Chats.
