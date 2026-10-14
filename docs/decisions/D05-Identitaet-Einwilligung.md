---
id: D05
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D05 – Identität, Einwilligung, Datenfluss und Logs

**Status: Empfohlen, nicht bestätigt.**

## Empfehlung

- **Anmeldung:** einfache Benutzer/Passwort-Anmeldung mit serverseitiger Sitzung (HttpOnly-Cookie) und festen Demo-Konten. Kein externer Login-Dienst im Prototyp – spart viel Aufwand, ohne die Regeln zu verletzen.
- **Identität** ausschließlich aus der Sitzung. Jede Datenabfrage filtert serverseitig auf den angemeldeten Nutzer (U005).
- **Einwilligung als eigene Daten:** pro Nutzer und Zweck (`chat_processing`, `source:<id>`) mit Zeitpunkt, Textversion und Status. Prüfung zentral in `security/`, aufgerufen vor Datenzugriff und vor Modellaufruf.
- **Drei getrennte Abläufe:** Chat-Freigabe widerrufen, Datenquelle widerrufen, Daten löschen. Nicht vermischen.
- **Logs:** keine Nachrichteninhalte, keine Gesundheitswerte, keine Prompts. Nur Request-ID, Zeitstempel, Route, Dauer, Fehlercode.
- **Datenfluss:** Website → API → (Consent-Prüfung) → Feature → lokales Modell. Keine Daten an externe Dienste; das Modell läuft lokal.

## Offene Punkte

- Wortlaut der Einwilligungstexte (mit Betreuung abstimmen).
- Gesundheitsdaten sind besondere Kategorien nach DSGVO Art. 9 – im Prototyp nur synthetisch, trotzdem so bauen, als wären sie echt.

Weitere EU-Pflichten (Auskunft/Export, Verzeichnis, TOM, Datenschutzhinweis): [D09](D09-Datenschutz-EU.md).

## Betroffen

`apps/api/src/vitasync/security/`, `features/consent/`, `features/health_data/`, U005, U023, U024, U027.
