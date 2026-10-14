---
tags: [vitasync, datenschutz, sicherheit]
status: entwurf
---

# Technische und organisatorische Maßnahmen (Art. 32 DSGVO)

**Probeweise ausgefüllter Entwurf.** Spalte „Stand“ erst auf „umgesetzt“ setzen, wenn ein Test oder Nachweis verlinkt ist.

| Bereich | Maßnahme | Umgesetzt in | Stand | Nachweis |
| --- | --- | --- | --- | --- |
| Zugangskontrolle | Anmeldung mit Passwort, gehasht (Argon2/bcrypt) | `security/`, F011, F018 | geplant | Test: Passwort nie im Klartext gespeichert |
| Zugriffskontrolle | Nutzer sehen nur eigene Daten, serverseitig geprüft | `security/`, U005 | geplant | Tests T-U005-02 |
| Einwilligung | Prüfung vor Datenzugriff und Modellaufruf | `security/`, U027, U023 | geplant | Tests T-U027-03 |
| Transport | HTTPS außerhalb der lokalen Entwicklung | `infra/`, F018 | geplant | Konfiguration + Prüfprotokoll |
| Speicherung | Verschlüsseltes Datenbank-Volume oder Feldverschlüsselung für Gesundheitsdaten | `adapters/db`, F018 | zu entscheiden | Entscheidung in F018 |
| Datenminimierung | Logs ohne Inhalte und Gesundheitswerte | `apps/api` Logging, F009 | geplant | Log-Stichprobe in DOD1-09 |
| Speicherbegrenzung | Automatische Löschung nach Frist, Löschung auf Anfrage | U024, D06 | geplant | Tests T-U024-03 |
| Trennung | Testdatenbank getrennt, nur synthetische Daten | `infra/`, `data/synthetic/` | geplant | README `data/synthetic` |
| Keine Drittlandübermittlung | Modell läuft lokal, keine externen KI-Dienste mit Nutzerdaten | `adapters/llm`, D03 | geplant | Netzwerkkonfiguration |
| Sichere Entwicklung | Review durch zweite Person, Abhängigkeitsprüfung in CI, keine Secrets im Repo | `.github/`, F004, F018 | teilweise | PR-Vorlage, CI-Lauf |
| Verfügbarkeit | Prototyp, keine Verfügbarkeitszusage; Daten aus `data/synthetic/` reproduzierbar | D06 | festgelegt | D06 |
| Organisation | Einweisung des Teams (Datenschutz, KI-Grenzen, AI Act Art. 4) | F017 | geplant | Teilnehmerliste mit Datum |

## Verknüpft
- [[Verarbeitungsverzeichnis]] · [[D09-Datenschutz-EU]] · [[Sicherheit-und-Grenzen]]
