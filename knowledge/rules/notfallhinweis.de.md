---
id: rule-notfallhinweis
titel: Allgemeiner Notfallhinweis
status: testfreigabe
sprache: de
version: 1
herausgeber:
quelle:
reviewer:
review_datum:
---

# Allgemeiner Notfallhinweis

**Testinhalt, nicht fachlich geprüft** ([D10](../../docs/decisions/D10-Testlauf.md)). Der Wortlaut unten
stammt wörtlich aus der Design-Vorlage `apps/web/design/vitasync-ui-v1.5.html` (deutsche Fassung,
Zeilen 827–829). Er ist damit belegt, aber nicht fachlich freigegeben.

## Wann gilt dieser Eintrag

**Platzhalter – die Liste der Warnzeichen-Stichworte fehlt und wird hier nicht erfunden.** Welche Wörter
den Hinweis auslösen, legt der Research-Task zu U001 fest; die Freigabe läuft über
[D04](../../docs/decisions/D04-Fachinhalte.md). Solange diese Liste fehlt, darf `features/guidance` den
Hinweis nicht automatisch auslösen.

## Inhalt

Der Text wird unverändert und für alle Nutzer gleich ausgegeben:

> Du hast Beschwerden genannt, bei denen allgemein empfohlen wird, sofort den Notruf 112 zu wählen, zum
> Beispiel starker Druck oder Schmerz in der Brust, Atemnot oder Lähmungserscheinungen.
>
> VitaSync ist eine KI und kann deine Situation nicht beurteilen.
>
> Wenn es kein Notfall ist: Der ärztliche Bereitschaftsdienst ist unter 116117 erreichbar.

## Anlaufstelle

112 (Notruf), 116117 (ärztlicher Bereitschaftsdienst).

## Grenzen

- Keine Einstufung der Dringlichkeit, kein Zeitfenster, keine Aussage über die Lage der fragenden Person
  ([D08](../../docs/decisions/D08-Zweckbestimmung.md)).
- Kein Treffer in der Stichwortliste ist **keine** Entwarnung, und es wird nie behauptet, alle Notfälle zu
  erkennen (harte Regel 8).
- Keine Variante des Textes, keine Abschwächung, keine Personalisierung.
