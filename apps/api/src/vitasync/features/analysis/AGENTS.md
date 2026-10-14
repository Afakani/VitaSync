# Modul: Datenauswertung

Zweck: Rein rechnerische Auswertungen eigener Daten (Mittelwert, Differenz, Anzahl, Zeitraumvergleich) mit Beleg, welche Werte verwendet wurden.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: `health_data` (öffentlich), `core/`.
- Darf nicht: LLM für Berechnungen; Werte bewerten (normal, auffällig, gut, schlecht); Referenzbereiche verwenden; Ursachen oder Zusammenhänge behaupten ([D08](../../../../../../docs/decisions/D08-Zweckbestimmung.md)).

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- Stories: U006, U029 (Kennzahl)

## Tests
- `apps/api/tests/features/analysis/` mit nachvollziehbar erwarteten Zahlen.

## Fallen
- Jede Aussage nennt Zeitraum, Einheit und Anzahl der verwendeten Werte.
- Datenlücken sichtbar machen, nicht auffüllen.
