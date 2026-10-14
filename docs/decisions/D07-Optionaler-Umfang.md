---
id: D07
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D07 – Optionaler Umfang

**Status: Empfohlen, nicht bestätigt.**

## Empfehlung

Erst M1 und M2 vollständig, dann nach Restkapazität entscheiden. Bei 7 Personen mit etwa 10 h/Woche sind 74 Kern-Tasks bereits viel.

| Story | Empfehlung | Grund |
| --- | --- | --- |
| U017 Englisch | nicht einplanen | Verdoppelt Prompts, Wissensinhalte und Evals. |
| U014 Arztzusammenfassung PDF | nach M3, falls Zeit | Gute Demo-Wirkung, technisch überschaubar. |
| U015 Antworten bewerten | einplanen (klein) | Liefert Daten für Evals. |
| U016 Erinnerungen | nicht einplanen | Braucht Hintergrundjobs, wenig Demo-Wert. |
| U018 Medikamente als Kontext | gestrichen | D08. |
| U019 Gesundheitsprofil | nur minimal, falls M2 es braucht | |
| U020 Symptomverlauf | später | |
| U022 FHIR-JSON-Import | einplanen | Einfachster Weg, synthetische Daten hineinzubringen. |
| U029 / U030 Bewegung / Ernährung | U030 vor U029 | Ernährung passt zum Eisenmangel-Beispiel; nur allgemein (D08). |
| U032 Befunddokument auslesen | nach U022, falls Zeit | Nutzt Bildfähigkeit des Modells; nur Auslesen mit Bestätigung. |

Gestrichen nach D08: U002, U003, U018, U031.

## Betroffen

`planning/`, Spalte „Einplanung“ im Backlog.
