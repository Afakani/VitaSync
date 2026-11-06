# Modul: Evaluationen

Zweck: Versionierte Testsätze mit Soll-Ergebnis: `recognition/` (Intent, Entitäten, Verneinung), `answers/` (Grenzen nach R1–R6: keine Diagnose, keine Bewertung, keine Dringlichkeitseinstufung; Notfallhinweis bei Stichwort), `documents/` (Auslesen von Befunden, U032).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: synthetische Beispielnachrichten, JSON Lines (`*.jsonl`), eine Zeile pro Fall.
- Darf nicht: Echte Nachrichten; Fälle nachträglich ändern, damit ein Modell besser aussieht.

## Verträge
- Format je Zeile: `id`, `input`, `expected`, `notiz`, `sprache` (`de` | `en`).
- Erwartete Werte für Fachinhalte nur nach fachlicher Prüfung.
- **Testsätze in beiden Sprachen** (Deutsch und Englisch, [Umfang (Jira)](../docs/decisions/README.md)). Jede Sprache hat eigene Fälle mit eigenen Erwartungswerten; Fälle werden nicht maschinell übersetzt, sonst prüft der Satz die Übersetzung statt das Verhalten.
- Ein Fall deckt auch den Rückfall ab: gewählte Sprache `en`, geprüfter Inhalt nur auf Deutsch → deutsche Fassung mit Hinweis, keine Übersetzung (keine Laufzeitübersetzung freigegebener Texte).

## Tests
- Runner: Team-Modul M9 (VC-79); lokal `benchmarks/`. Ergebnis (Trefferquote, Anteil gültiger Ausgaben) im PR angeben.

## Fallen
- Jeder gefundene Fehler im Betrieb wird zuerst ein Eval-Fall, dann behoben.
