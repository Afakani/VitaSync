# Modul: Fachwissen

Zweck: Fachlich freigegebene Inhalte: Themen (`topics/`), Warnzeichen-Stichworte mit festem Notfallhinweis (`rules/`), Anlaufstellen (`care_paths/`).
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Markdown mit Kopfdaten nach `TEMPLATE.md`.
- Darf nicht: Inhalte ohne Quelle; Status `geprueft` ohne Reviewer setzen; Diagnosen, Medikamente, Dosierungen, Referenzbereiche zur Bewertung, Dringlichkeitsstufen ([R1–R6](../docs/decisions/README.md)). Alles ist allgemein formuliert, für alle Nutzer gleich.

## Verträge
- Pflichtfelder im Kopf: `id`, `titel`, `status`, `sprache`, `version`, `herausgeber`, `quelle`, `reviewer`, `review_datum`.
- Dateiname: `<name>.<sprache>.md`, z. B. `eisenmangel.de.md`. Alle Sprachfassungen eines Inhalts tragen dieselbe `id`.
- `sprache`: `de` oder `en`, muss zum Dateinamen passen. Entspricht `content_language` im API-Vertrag.
- `version`: Ganzzahl ab 1, bei jeder inhaltlichen Änderung erhöhen. Der Vertrag gibt sie in `ai_disclosure.version` und `notice.version` weiter.
- `status`: `entwurf` | `testfreigabe` | `geprueft`.
  - `geprueft`: der Code lädt den Eintrag immer. Verlangt `herausgeber`, `quelle`, `reviewer`, `review_datum`.
  - `testfreigabe`: formal vollständig, **fachlich nicht geprüft**. Wird nur bei `APP_ENV=development` geladen und in der Antwort als Testinhalt gekennzeichnet ([Testinhalt, nicht fachlich geprüft](../docs/decisions/README.md)). `reviewer` und `review_datum` bleiben leer.
  - `entwurf`: wird nie geladen.
- Siehe [fachliche Prüfung (R1–R6)](../docs/decisions/README.md).

## CP1-Muster
- `rules/cp1_patterns.json`: Muster für Notfall, Krise und Injection, die `features/input_guard` vor dem Modell prüft. Teamentwurf aus dem Team-Router v0.5 (Version im Feld `version`), **nicht medizinisch geprüft**.
- `rules/cp2_patterns.json`: Wortmuster für das Sicherheitsnetz nach dem Routing (`features/safety_net`), Team-Router v0.5.
- Änderungen an beiden nur mit Quelle und neuer Version.

## Übersetzungen
- Nicht zur Laufzeit übersetzen. Eine Übersetzung ist ein eigener Eintrag mit eigener Datei, eigener Prüfung und gleicher `id`.
- Fehlt die Fassung in der gewünschten Sprache, wird die deutsche angezeigt und die Oberfläche weist darauf hin (keine Laufzeitübersetzung freigegebener Texte).

## Tests
- `python scripts/check_structure.py` prüft Kopfdaten, Dateinamen und Status. `testfreigabe` erscheint als Warnung, nicht als Fehler.

## Fallen
- KI darf Entwürfe schreiben, aber nie `status: geprueft` setzen. Das tut nur der benannte Reviewer.
- Auch bei `testfreigabe` gilt: nichts erfinden. Fehlt ein Text, steht dort ein ausdrücklicher Platzhalter.
- `version` erhöhen, wenn sich der Wortlaut ändert – sonst zeigt der Nachweis in der Antwort auf die falsche Fassung.
