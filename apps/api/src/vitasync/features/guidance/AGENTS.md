# Modul: Allgemeine Information und Notfallhinweis

Zweck: Wählt zur erkannten Anfrage freigegebene allgemeine Inhalte aus `knowledge/` (Gesundheitsinformation, Lifestyle, Vorsorge, Zuständigkeiten) und löst bei Warnzeichen-Stichworten den festen Notfallhinweis aus.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: Loader für `knowledge/`, `core/`.
- Darf nicht: Inhalte im Code festschreiben; Einträge mit Status `entwurf` verwenden; Antworten an Werte, Profil oder Vorerkrankungen der Person anpassen; Dringlichkeitsstufen bilden; Diagnosen, Ursachen oder Medikamente nennen ([D08](../../../../../../docs/decisions/D08-Zweckbestimmung.md)).

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- Stories: U001 (Notfallhinweis, Zuständigkeiten), U008, U009, U029, U030

## Tests
- `apps/api/tests/features/guidance/`. Verhalten testen, nicht Implementierung spiegeln.
- Grenzfälle in `evals/answers/`: keine Antwort enthält Bewertung, Diagnose oder Einstufung.

## Fallen
- Notfallhinweis ist ein fester Text, für alle gleich. Keine Variante „wahrscheinlich nicht dringend“.
- Verneintes Stichwort („keine Atemnot“) löst keinen Hinweis aus.
- Kein Treffer ist keine Entwarnung.
- Kein passender geprüfter Eintrag → ehrlich sagen und allgemein auf Hausarzt oder 116117 verweisen.
