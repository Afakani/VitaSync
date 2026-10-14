---
tags: [vitasync, datenschutz]
status: entwurf
---

# Verzeichnis von Verarbeitungstätigkeiten (Art. 30 DSGVO)

**Probeweise ausgefüllter Entwurf.** Verantwortliche Stelle, Kontakte und Fristen mit Betreuung bzw. Datenschutzbeauftragtem der FH Aachen klären. Bei jeder neuen Verarbeitung im selben PR ergänzen.

- Verantwortlicher: <FH Aachen / Projektteam – klären>
- Datenschutzkontakt: <klären>
- Stand: 14.10.2026

| Nr. | Verarbeitung | Zweck | Daten | Betroffene | Rechtsgrundlage | Speicherdauer | Empfänger |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V1 | Konto und Anmeldung | Zugang zum Prototyp | Benutzername, Passwort-Hash, Sitzungs-ID | Tester | Art. 6 Abs. 1 a (Einwilligung) | bis Projektende oder Löschung | keine |
| V2 | Chat-Verarbeitung | Beantwortung von Gesundheitsfragen | Nachrichten, Antworten, Kontext im Chat | Tester | Art. 9 Abs. 2 a (ausdrückliche Einwilligung, U027) | 30 Tage (D06), sofort bei Löschung | keine; Modell lokal |
| V3 | Eigene Gesundheitsdaten | Anzeige und Berechnung | Messwerte, Einheiten, Zeitpunkte, Quelle | Tester (synthetische Daten) | Art. 9 Abs. 2 a, je Quelle (U023) | bis Widerruf oder Löschung | keine |
| V4 | Einwilligungsnachweis | Nachweis nach Art. 7 | Zweck, Textversion, Zeitpunkt, Status | Tester | Art. 6 Abs. 1 c (Nachweispflicht) | Dauer der Verarbeitung + Nachweisfrist <klären> | keine |
| V5 | Feedback | Fehleranalyse | Bewertung, Kommentar, Antwort-ID | Tester | Art. 6 Abs. 1 a | bis Projektende | Projektteam |
| V6 | Technische Logs | Betrieb und Fehlersuche | Request-ID, Zeit, Route, Dauer, Fehlercode; **keine Inhalte** | Tester | Art. 6 Abs. 1 f | 7 Tage <bestätigen> | keine |
| V7 | Dokument-Auslesung (optional, U032) | Werte aus eigenem Befund übernehmen | Bild/PDF, ausgelesene Werte | Tester (synthetische Befunde) | Art. 9 Abs. 2 a | Datei nach Auslesung löschen; Werte wie V3 | keine |

## Technische und organisatorische Maßnahmen
Siehe [[TOM]].

## Verknüpft
- [[D09-Datenschutz-EU]] · [[D05-Identitaet-Einwilligung]] · [[D06-Speicherung]]
