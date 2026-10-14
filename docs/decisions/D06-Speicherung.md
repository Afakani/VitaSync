---
id: D06
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D06 – Speicherung, Kontextlebensdauer und Sicherungen

**Status: Empfohlen, nicht bestätigt.**

## Empfehlung

- **PostgreSQL** lokal per Docker. Schemaänderungen nur über Migrationen (Alembic) in `apps/api/migrations/`.
- **Getrennt speichern:** Chatverläufe, Einwilligungen, eigene App-Daten (Profil, Symptomtagebuch). Externe FHIR-Daten werden gelesen, nicht dauerhaft kopiert.
- **Gesprächskontext** gilt nur innerhalb eines Chats (U025), nicht chatübergreifend.
- **Aufbewahrung:** Chats nach 30 Tagen automatisch löschen (Startwert, im Team bestätigen); sofort bei Nutzerlöschung (U024).
- **Sicherungen:** im Prototyp keine Backups mit Nutzerdaten. Daten sind synthetisch und reproduzierbar aus `data/synthetic/`.
- **Tests** laufen gegen eine eigene Test-Datenbank, nie gegen eine gemeinsam genutzte.

## Offene Punkte

- Löschfrist bestätigen.

## Betroffen

`apps/api/migrations/`, `adapters/db/`, `features/chat/`, `features/consent/`, `infra/`.
