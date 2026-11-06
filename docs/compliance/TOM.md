---
tags: [vitasync, datenschutz, sicherheit]
status: entwurf
---

# Technische und organisatorische Maßnahmen (Art. 32 DSGVO)

**Probeweise ausgefüllter Entwurf.** Spalte „Stand“ erst auf „umgesetzt“ setzen, wenn ein Test oder Nachweis verlinkt ist.

| Bereich | Maßnahme | Umgesetzt in | Stand | Nachweis |
| --- | --- | --- | --- | --- |
| Zugangskontrolle | Anmeldung mit Passwort, gehasht (Argon2/bcrypt) | `security/` | geplant | Test: Passwort nie im Klartext gespeichert |
| Zugriffskontrolle | Nutzer sehen nur eigene Daten, serverseitig geprüft | `security/` | geplant | Tests offen |
| Einwilligung | Prüfung vor Datenzugriff und Modellaufruf | `security/`, I3 | geplant | Tests offen |
| Transport | HTTPS außerhalb der lokalen Entwicklung | `infra/`, Hosting-ADR (VC-82) | geplant | Konfiguration + Prüfprotokoll |
| Speicherung | Verschlüsseltes Datenbank-Volume oder Feldverschlüsselung für Gesundheitsdaten | `adapters/db` | zu entscheiden | Hosting-ADR (VC-82) |
| Datenminimierung | Logs ohne Inhalte und Gesundheitswerte | `apps/api` Logging, I5 | geplant | Log-Stichprobe |
| Speicherbegrenzung | Automatische Löschung nach Frist, Löschung auf Anfrage | Speicherkonzept (VC-83) | geplant | Tests offen |
| Trennung | Testdatenbank getrennt, nur synthetische Daten | `infra/`, `data/synthetic/` | geplant | README `data/synthetic` |
| Keine Drittlandübermittlung | Modell läuft lokal, keine externen KI-Dienste mit Nutzerdaten | `adapters/llm`, Modell-ADR | geplant | Netzwerkkonfiguration |
| Sichere Entwicklung | Review durch zweite Person, Abhängigkeitsprüfung in CI, keine Secrets im Repo | `.github/` | teilweise | PR-Vorlage, CI-Lauf |
| Verfügbarkeit | Prototyp, keine Verfügbarkeitszusage; Daten aus `data/synthetic/` reproduzierbar | Speicherkonzept | festgelegt | Speicherkonzept |
| Organisation | Einweisung des Teams (Datenschutz, KI-Grenzen, AI Act Art. 4) | Team | geplant | Teilnehmerliste mit Datum |

## Verknüpft
- [[Verarbeitungsverzeichnis]] · Datenschutz (DSGVO-Recherche) · [[Sicherheit-und-Grenzen]]
