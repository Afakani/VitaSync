# Modul: Anfrageerkennung

Zweck: **Kern des Prototyps.** Aus der Nutzernachricht die **Anfrageart** bestimmen – was der Nutzer will – und damit, welche Information er zurückbekommt. Dazu Entitäten (Symptome, Messgrößen, Altersgruppe), Verneinung und Zeitangaben.

Der Katalog der Anfragearten kommt aus den **Anwendungsfällen** (User Stories), nicht aus dem Code. Er liegt als Enum im Ausgabeschema unter `contracts/llm/`; jeder Wert nennt seine Story. Was dort nicht steht, ist keine gültige Anfrageart.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: LLM-Port mit Schema aus `contracts/llm/`, `core/`.
- Darf nicht: Antworten formulieren; Dringlichkeit oder Diagnosen ableiten; Modellausgabe ungeprüft weitergeben; eine Anfrageart vergeben, die nicht im Schema steht; aus erkannten Entitäten eine Aussage über die Person machen.

## Verträge
- Öffentliche Funktionen nur über `__init__.py`.
- Stories: U004, U010, U013

## Tests
- `apps/api/tests/features/recognition/`. Verhalten testen, nicht Implementierung spiegeln.

## Fallen
- Ungültige oder unvollständige Modellausgabe → definierter Fallback (Rückfrage), kein Absturz.
- Verneinungen („kein Fieber“) sind die häufigste Fehlerquelle; in `evals/recognition/` abdecken.
- **Unbekannte Anfrageart nicht raten.** Passt nichts, ist das ein eigenes Ergebnis (Rückfrage oder Abweisung nach U004) – nicht die nächstbeste Anfrageart. Ein fehlender Treffer ist nie eine Entwarnung (harte Regel 8).
- **Erkennen ist nicht bewerten.** Eine erkannte Altersgruppe oder Messgröße ist eine Entität, keine Aussage über die Person. Ob Personenmerkmale die Auswahl beeinflussen dürfen, ist offen – siehe [D08](../../../../../../docs/decisions/D08-Zweckbestimmung.md).
