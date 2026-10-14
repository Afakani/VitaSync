# Modul: Einwilligung

Zweck: Einwilligungen **verwalten** – pro Nutzer und Zweck erteilen, anzeigen, widerrufen; Löschanfragen.

Zuständig: <GitHub-Handle eintragen>

Abgrenzung zu [`security`](../../security/AGENTS.md): Dieses Modul **verwaltet** den Zustand (erteilen,
widerrufen, löschen). Ob eine Anfrage erlaubt ist, entscheidet beim Zugriff ausschließlich die lesende
Prüfung in `security`; sie wird hier nicht nachgebaut.

## Grenzen
- Darf nutzen: `core/`, DB-Port.
- Darf nicht: Chat-Widerruf, Quellen-Widerruf und Löschung zu einem Ablauf vermischen; eine eigene Consent-Prüfung für Datenzugriffe einführen.

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- Stories: U023, U024, U027, U033 (Auskunft/Export)

## Tests
- `apps/api/tests/features/consent/`. Verhalten testen, nicht Implementierung spiegeln.

## Fallen
- Widerruf während laufender Anfrage: Antwort darf danach nicht mehr ausgeliefert werden (T-U027-04).
