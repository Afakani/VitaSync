---
id: D09
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D09 – Datenschutz und EU-Recht

**Status: Empfohlen, nicht bestätigt.** Keine Rechtsberatung. Mit Betreuung und, falls vorhanden, dem Datenschutzbeauftragten der FH Aachen abstimmen. Stand der Recherche: 14.10.2026.

## Welche Regeln gelten

| Regelwerk | Gilt für VitaSync? | Folge |
| --- | --- | --- |
| **DSGVO** | Ja, sobald personenbezogene Daten verarbeitet werden. Synthetische Gesundheitsdaten sind keine personenbezogenen Daten, aber Testkonten, Chats echter Tester, Feedback und Logs können es sein. | Wir bauen so, als wären die Gesundheitsdaten echt (Art. 9: besondere Kategorien). |
| **EU AI Act, Art. 50** (Transparenz) | Ja, gilt seit 2. August 2026 für Chatbots. Hochschulprototypen können unter die Forschungsausnahme fallen; wir halten Art. 50 trotzdem ein. | Nutzer erfahren, dass sie mit einer KI sprechen (U028). KI-Ausgaben zusätzlich maschinenlesbar kennzeichnen (T-U028-03). |
| **AI Act, Hochrisiko** | Nein, solange D08 gilt. Systeme zur Triage von Notfallpatienten sind Hochrisiko (Anhang III Nr. 5 d). Diese Funktion haben wir mit D08 ausgeschlossen. | Keine Dringlichkeitseinstufung einbauen, auch nicht später „klein“. |
| **AI Act, Art. 4** (KI-Kompetenz) | Ja, für Anbieter und Betreiber. | Kurze Teameinweisung zu Grenzen des Modells, dokumentiert in `docs/compliance/`. |
| **MDR** (Medizinprodukte) | Nein, wegen D08. | Siehe D08. |
| **TDDDG** (Cookies, früher TTDSG) | Ja, für die Website. | Nur technisch notwendiges Sitzungs-Cookie, dann kein Cookie-Banner nötig. Kein Tracking, keine Analyse-Tools. |
| **Cyber Resilience Act** | Nicht, solange nichts in Verkehr gebracht wird. | Sichere Entwicklung trotzdem: Abhängigkeitsprüfung, keine bekannten Lücken. |
| **Europäischer Gesundheitsdatenraum (EHDS)** | Erst relevant, wenn ein Produkt mit Anbindung an elektronische Patientenakten entsteht. | Für den Prototyp nichts zu tun, bei Produktreife prüfen. |

## DSGVO: was umgesetzt sein muss

| Pflicht | Artikel | Wo im Projekt |
| --- | --- | --- |
| Rechtsgrundlage: ausdrückliche Einwilligung für Gesundheitsdaten | Art. 6, Art. 9 Abs. 2 a | U027, U023, F016 |
| Einwilligung nachweisbar, widerrufbar, so einfach wie erteilt | Art. 7 | U027 (Version, Zeitpunkt), U023 |
| Datenschutzhinweis vor der Verarbeitung | Art. 13 | F016, `docs/compliance/Datenschutzhinweis.md` |
| Auskunft und Datenübertragbarkeit (Export) | Art. 15, Art. 20 | **U033 (neu)** |
| Berichtigung | Art. 16 | U012, U019 |
| Löschung | Art. 17 | U024 |
| Datenschutz durch Technik, Datenminimierung | Art. 5, Art. 25 | D05, D06, Logs ohne Inhalte, lokales Modell |
| Verzeichnis von Verarbeitungstätigkeiten | Art. 30 | F017, `docs/compliance/Verarbeitungsverzeichnis.md` |
| Technische und organisatorische Maßnahmen (TOM) | Art. 32 | F018, `docs/compliance/TOM.md` |
| Meldung von Datenpannen (72 h) | Art. 33, 34 | F017, `docs/compliance/Datenpanne.md` |
| Datenschutz-Folgenabschätzung | Art. 35 | F017: Schwellwertprüfung; bei echten Gesundheitsdaten in größerem Umfang wahrscheinlich Pflicht |
| Keine Übermittlung in Drittländer | Art. 44 ff. | Modell läuft lokal; keine externen KI-Dienste mit Nutzerdaten |

## Empfehlungen für die Technik

- Transportverschlüsselung (HTTPS) überall außer lokal auf dem eigenen Rechner.
- Passwörter nur gehasht (Argon2 oder bcrypt).
- Datenbank-Volume verschlüsselt oder Gesundheitsfelder verschlüsselt speichern. Zu prüfen in F018.
- Rollen: Nutzer sehen nur eigene Daten (U005). Admin-Zugriff auf Inhalte nur für Löschung und Fehleranalyse, protokolliert.
- Abhängigkeiten automatisch auf bekannte Sicherheitslücken prüfen (CI, F018).
- Entwicklungswerkzeuge (Claude, Codex, GitHub) bekommen nie echte personenbezogene Daten.

## Betroffen

F016, F017, F018, T-U028-03, U033, `docs/compliance/`, `security/`, `features/consent/`.
