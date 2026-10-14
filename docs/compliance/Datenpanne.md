---
tags: [vitasync, datenschutz]
status: entwurf
---

# Ablauf bei Datenpannen (Art. 33/34 DSGVO)

**Probeweise ausgefüllter Entwurf.**

1. Wer etwas bemerkt (z. B. echte Daten im Repo, Zugriff auf fremde Daten, Secret veröffentlicht), meldet es sofort an <Teamleitung> und <Betreuung>.
2. Sofortmaßnahme: betroffenen Zugang sperren, Secret austauschen, Daten entfernen. Nichts löschen, was zur Aufklärung nötig ist.
3. Dokumentieren: Was, wann, welche Daten, wie viele Personen, welche Maßnahmen.
4. Betreuung bzw. Datenschutzbeauftragter entscheidet über eine Meldung an die Aufsichtsbehörde (innerhalb von 72 Stunden ab Kenntnis).
5. Ursache beheben, Regel in der passenden `AGENTS.md` unter „Fallen“ ergänzen.

## DSFA-Schwellwertprüfung (Art. 35)

| Frage | Prototyp mit synthetischen Daten | Mit echten Gesundheitsdaten |
| --- | --- | --- |
| Besondere Kategorien (Gesundheit)? | nein (synthetisch) | ja |
| Neue Technologie (KI)? | ja | ja |
| Umfangreiche Verarbeitung? | nein | abhängig |
| **Ergebnis** | DSFA voraussichtlich nicht erforderlich; Begründung dokumentieren | DSFA voraussichtlich erforderlich |

## Verknüpft
- [[D09-Datenschutz-EU]] · [[TOM]]
