# Modul: Evaluationen

Zweck: Versionierte Testsätze mit Soll-Ergebnis: `recognition/` (Intent, Entitäten, Verneinung), `answers/` (Grenzen nach D08: keine Diagnose, keine Bewertung, keine Dringlichkeitseinstufung; Notfallhinweis bei Stichwort), `documents/` (Auslesen von Befunden, U032).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: synthetische Beispielnachrichten, JSON Lines (`*.jsonl`), eine Zeile pro Fall.
- Darf nicht: Echte Nachrichten; Fälle nachträglich ändern, damit ein Modell besser aussieht.

## Verträge
- Format je Zeile: `id`, `input`, `expected`, `notiz`.
- Erwartete Werte für Fachinhalte nur nach D04-Freigabe.

## Tests
- Runner folgt mit Task F004/F008. Ergebnis (Trefferquote, Anteil gültiger Ausgaben) im PR angeben.

## Fallen
- Jeder gefundene Fehler im Betrieb wird zuerst ein Eval-Fall, dann behoben.
