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
| U017 Englisch | **eingeplant** (Entscheidung 14.10.2026) | Siehe unten. Die frühere Einschätzung „nicht einplanen – verdoppelt Prompts, Wissensinhalte und Evals“ ist überholt. |
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

## U017 Deutsch und Englisch (Entscheidung Atakan, 14.10.2026)

U017 ist **eingeplant** und damit Kern, nicht optional. Begründung:

- Der befürchtete Mehraufwand entsteht vor allem bei den Fachinhalten. Der entfällt hier, weil
  **nie zur Laufzeit übersetzt wird** (harte Regel 12 in `AGENTS.md`). Eine englische Fassung ist ein
  eigener, eigens geprüfter Eintrag in `knowledge/` mit derselben `id` und `sprache: en`.
- Fehlt die geprüfte Fassung in der gewählten Sprache, erscheint die **deutsche Fassung mit Hinweis**.
  Die Sprachwahl darf also nie dazu führen, dass ein Inhalt maschinell übersetzt oder weggelassen wird.
- Damit ist der Umfang beherrschbar: Oberfläche und Rahmentexte zweisprachig (T-U017-01 bis -03), die
  Fachinhalte folgen einzeln und geprüft (T-U017-04).

Der API-Vertrag trägt die Unterscheidung bereits: `language` ist die gewählte Sprache der Anfrage,
`content_language` die Sprache, in der ein freigegebener Inhalt tatsächlich vorliegt
(`contracts/api/draft/chat-v1.openapi.yaml`).

## Betroffen

`planning/`, Spalte „Einplanung“ im Backlog.
