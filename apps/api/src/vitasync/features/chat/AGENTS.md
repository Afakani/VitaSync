# Modul: Chat (Orchestrierung)

Zweck: Nimmt eine Nachricht an, ruft Erkennung, ggf. Daten und Hinweise auf, baut die Antwort, verwaltet Chatkontext und offene Rückfragen.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `recognition`, `guidance`, `health_data`, `consent` (je öffentliche Funktionen), `core/ports.py`.
- Darf nicht: Selbst Gesundheitsinhalte formulieren; Profil- oder Messdaten zur Bewertung in den Prompt geben (D08).

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- Stories: U010, U012, U013, U015, U021, U025

## Tests
- `apps/api/tests/features/chat/`. Verhalten testen, nicht Implementierung spiegeln.

## Fallen
- Wiederholte Anfrage (gleiche Request-ID) darf keine doppelte Antwort erzeugen.
- Kontext gilt nur innerhalb eines Chats.
