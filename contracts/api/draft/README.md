# Vertragsentwürfe (Status: Vorschlag)

Dieser Ordner enthält **handgepflegte Vertragsentwürfe**. Sie sind Diskussionsgrundlage, kein geltender
Vertrag. Die verbindliche Schnittstellenbeschreibung ist und bleibt `contracts/api/openapi.json`, erzeugt aus
`apps/api` (siehe [AGENTS.md](../../AGENTS.md) des Moduls `contracts/`).

| Datei | Task | Stand | Status |
| --- | --- | --- | --- |
| `chat-v1.openapi.yaml` | F003, T-U028-03 | 14.10.2026 | Vorschlag, unbestätigt |

Ablauf: Team bestätigt den Entwurf → F007 baut genau diesen Endpunkt in Pydantic nach → FastAPI erzeugt
`contracts/api/openapi.json` → der Entwurf wird hier als „umgesetzt in F007" markiert und entfällt, sobald
das generierte Schema vollständig ist. Weicht die Umsetzung ab, wird der Entwurf im selben PR angepasst,
nicht stillschweigend überholt.

## Was der Entwurf festlegt

Ein Endpunkt: `POST /api/v1/chat/messages`. Eine Nutzernachricht hinein, genau eine vollständige Antwort
heraus. Enthalten sind Nachricht, Chat-ID, Request-ID, Sprache, Antwortobjekt, Quellenangaben, einheitliches
Fehlerformat mit abgeschlossener Fehlercode-Liste, maximale Eingabelänge und die maschinenlesbare
KI-Kennzeichnung.

## Begründungen zu den Festlegungen

**Maximale Eingabelänge 2000 Zeichen.** Gezählt werden Unicode-Codepoints nach NFC-Normalisierung und nach
Entfernen von führendem und folgendem Leerraum. 2000 reicht für eine ausführlich geschilderte Frage und
bleibt für das lokale Modell ([D03](../../../docs/decisions/D03-Modell.md)) unkritisch. Die Prüfung läuft
serverseitig; das Eingabefeld im Frontend darf zusätzlich begrenzen, ersetzt die Serverprüfung aber nicht.
Zwei getrennte Fehlerfälle: `message_empty` (leer oder nur Leerraum) und `message_too_long`.

**Keine Identität im Request.** `chat_id` bezeichnet den Chat, nicht den Nutzer. Wer fragt, steht
ausschließlich in der serverseitigen Sitzung ([D05](../../../docs/decisions/D05-Identitaet-Einwilligung.md),
harte Regel 2). Felder wie `user_id` oder `patient_id` sind im Schema ausdrücklich verboten
(`additionalProperties: false`), damit ein Client sie nicht einschmuggeln kann.

**Request-ID.** Optionaler Header `X-Request-Id`; fehlt er, erzeugt der Server eine. Sie steht im
Antwortheader und im Rumpf jeder Antwort und jedes Fehlers. Weil Logs weder Nachrichteninhalte noch
Gesundheitswerte enthalten (harte Regel 10), ist sie die einzige Brücke zwischen einer Nutzermeldung und
dem Logeintrag.

**`chat_id` ist Pflichtfeld mit erlaubtem `null`.** Ein vergessenes Feld soll nicht still einen neuen Chat
anlegen; der Client muss die Absicht ausdrücken.

**Eine vollständige Antwort, kein Streaming.** Passt zu F007 (feste Antwort) und zur Design-Vorlage
(Tippindikator, danach eine Blase) und hält Fehlerformat, KI-Kennzeichnung und Tests einfach. Streaming
wäre eine eigene Entscheidung mit eigenem Vertrag.

**`client_message_id` für Idempotenz.** Wird dieselbe ID erneut gesendet, liefert der Server die bereits
erzeugte Antwort zurück statt das Modell zweimal zu rufen. Deckt „Wiederholen ohne Doppelversand" aus
[apps/web/AGENTS.md](../../../apps/web/AGENTS.md) ab.

**KI-Kennzeichnung (T-U028-03).** Drei Felder statt eines:

- `origin` (`model` | `fixed_text`) macht feste Systemtexte maschinell unterscheidbar. Das war die
  Abnahmebedingung des Tasks.
- `ai_generated` ist Pflichtfeld und genau dann `true`, wenn `origin` den Wert `model` hat. Bei
  `fixed_text` ist der Wortlaut fachlich freigegeben und stammt nicht vom Modell, deshalb `false`.
- `ai_disclosure` verweist versioniert auf den freigegebenen Transparenzhinweis, damit nachweisbar ist,
  welcher Wortlaut angezeigt wurde (AI Act Art. 50, [D09](../../../docs/decisions/D09-Datenschutz-EU.md)).

Wichtig: Die **dauerhafte** Kennzeichnung in der Oberfläche hängt an keinem dieser Felder. Sie ist immer
sichtbar (U028, T-U028-02). `ai_generated: false` heißt „dieser Satz stammt nicht vom Modell", nicht
„hier spricht ein Mensch".

**`notice` statt Dringlichkeit.** Der Notfallhinweis ist ein fester, für alle gleicher Text mit Verweis auf
seinen Eintrag in `knowledge/`. Es gibt bewusst keine Stufe, keinen Score und keinen Zeitrahmen
([D08](../../../docs/decisions/D08-Zweckbestimmung.md), harte Regel 8). Ein fehlender `notice` ist keine
Entwarnung; das gehört in den UI-Text, nicht in ein Feld.

**Quellen.** `sources` spiegelt die Kopfdaten aus `knowledge/`: `knowledge_id` ← `id`, `title` ← `titel`,
`url` ← `quelle`, `review_date` ← `review_datum`. Nur Einträge mit `status: geprueft`
([D04](../../../docs/decisions/D04-Fachinhalte.md)). Eine leere Liste ist erlaubt (fester Text) und bedeutet
nicht, dass keine Quelle nötig wäre.

**Ungültige Modellausgabe ist kein HTTP-Fehler.** Harte Regel 5 verlangt einen kontrollierten Fallback:
`201` mit `origin: fixed_text`. `model_unavailable` gilt nur, wenn das Modell gar nicht erreichbar ist.

**Was absichtlich fehlt.** Im Antwortobjekt sind `assessment`, `severity`, `urgency`, `triage_level`,
`risk_score`, `diagnosis`, `suspected_condition`, `reference_range`, `recommended_action` und `confidence`
verboten und im Schema als solche dokumentiert (D08, harte Regel 7). Für spätere Tasks reserviert, hier
nicht spezifiziert: Darstellung eigener Werte und rein rechnerischer Auswertungen (U010, U013), Anhänge
(U032), Endpunkte für Verlauf und Einwilligung.

## Beispiele

In `examples/`. Die Texte sind synthetische Platzhalter im Sinne der Design-Vorlage v1.5, **nicht fachlich
freigegeben**; die Quellenangaben und `knowledge_id`-Werte sind erfunden und zeigen nur das Format. Der
echte Wortlaut kommt aus D04-Tasks.

| Datei | Fall |
| --- | --- |
| `chat-request.json` | erste Nachricht in einem neuen Chat |
| `chat-response-general.json` | allgemeine Information, `origin: model`, mit Quelle |
| `chat-response-emergency.json` | fester Notfallhinweis, `origin: fixed_text`, `ai_generated: false` |
| `chat-error-message-empty.json` | leerer Text |
| `chat-error-message-too-long.json` | überlange Eingabe |

## Offene Punkte für das Team

1. **Maximale Eingabelänge 2000 Zeichen bestätigen** oder begründet ändern.
2. **`publisher` in `knowledge/`.** Das Quellenobjekt führt die herausgebende Stelle; die Kopfdaten in
   [knowledge/TEMPLATE.md](../../../knowledge/TEMPLATE.md) haben dafür kein Feld. Entweder `publisher`
   dort ergänzen oder das Feld aus dem Vertrag streichen. Entscheidung gehört zu D04.
3. **Versionsfeld in `knowledge/`.** `ai_disclosure.version` und `notice.version` setzen eine Version des
   Wortlauts voraus. Die Kopfdaten kennen nur `review_datum`. Entweder ein `version`-Feld ergänzen oder im
   Vertrag auf `review_date` umstellen.
4. **`language` im Prototyp.** U017 (Deutsch/Englisch) ist optionaler Umfang
   ([D07](../../../docs/decisions/D07-Optionaler-Umfang.md)). Bleibt das Feld im Vertrag, ohne dass es
   zunächst wirkt, oder fällt es weg?
5. **`ai_generated` bei festem Text.** Alternative Lesart: immer `true`, weil der Hinweis aus einem
   KI-System kommt. Dann bräuchte die Unterscheidung allein `origin`. Formulierung oben ist der Vorschlag,
   die Entscheidung ist eine Transparenzfrage für D09.
6. **Streaming** für eine spätere Version: ja oder nein.
7. **Idempotenz-Verhalten** bei erneuter `client_message_id`: dieselbe Antwort mit `201` (Vorschlag) oder
   `200`.
8. **`rate_limited`** ist vorgesehen, aber keine Grenze festgelegt. Gehört in einen eigenen Task.
