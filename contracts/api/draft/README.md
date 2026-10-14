# Vertragsentwürfe

Dieser Ordner enthält **handgepflegte Vertragsentwürfe**. Die verbindliche Schnittstellenbeschreibung ist
und bleibt `contracts/api/openapi.json`, erzeugt aus `apps/api` (siehe [AGENTS.md](../../AGENTS.md) des
Moduls `contracts/`).

| Datei | Task | Stand | Status |
| --- | --- | --- | --- |
| `chat-v1.openapi.yaml` | F003, T-U028-03 | 14.10.2026 | bestätigt vorbehaltlich Review |

„Bestätigt vorbehaltlich Review" heißt: Das Team hat die inhaltlichen Fragen am 14.10.2026 entschieden
(Atakan, siehe „Entschiedene Punkte"). Der PR-Review steht noch aus. Erst danach gilt der Vertrag als
abgenommen.

Ablauf: F007 baut genau diesen Endpunkt in Pydantic nach → FastAPI erzeugt `contracts/api/openapi.json`
→ der Entwurf wird hier als „umgesetzt in F007" markiert und entfällt, sobald das generierte Schema
vollständig ist. Weicht die Umsetzung ab, wird der Entwurf im selben PR angepasst, nicht stillschweigend
überholt.

## Was der Entwurf festlegt

Ein Endpunkt: `POST /api/v1/chat/messages`. Eine Nutzernachricht hinein, genau eine vollständige Antwort
heraus. Enthalten sind Nachricht, Chat-ID, Request-ID, Sprache, Antwortobjekt, Quellenangaben, einheitliches
Fehlerformat mit abgeschlossener Fehlercode-Liste, maximale Eingabelänge und die maschinenlesbare
KI-Kennzeichnung.

## Begründungen zu den Festlegungen

**Maximale Eingabelänge 2000 Zeichen** (bestätigt). Gezählt werden Unicode-Codepoints nach NFC-Normalisierung und nach
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
(Tippindikator, danach eine Blase) und hält Fehlerformat, KI-Kennzeichnung und Tests einfach. Für v1
entschieden; Neubewertung nach der Latenzmessung zu [D03](../../../docs/decisions/D03-Modell.md). Streaming
wäre dann eine eigene Entscheidung mit eigenem Vertrag.

**`client_message_id` für Idempotenz.** Wird dieselbe ID erneut gesendet, liefert der Server **dieselbe
Antwort erneut, einschließlich Status `201`**, statt das Modell zweimal zu rufen. Bewusst kein `200`: für
den Client ist die Wiederholung nicht von der ersten Antwort zu unterscheiden, er braucht keine Sonderlogik.
Deckt „Wiederholen ohne Doppelversand" aus [apps/web/AGENTS.md](../../../apps/web/AGENTS.md) ab.

**Sprache: `language` im Request, `content_language` am Inhalt.** Der Nutzer wählt die Sprache in der
Oberfläche (U017), der Client schickt sie bei jeder Anfrage mit; der Server erkennt nichts automatisch und
leitet die Sprache auch nicht aus dem Nachrichtentext ab. Davon getrennt tragen `notice` und jeder Eintrag
in `sources` ein eigenes `content_language`: die Sprache, in der der **freigegebene** Text wirklich
vorliegt. Weicht sie von `language` ab, weist die Oberfläche darauf hin („Nur auf Deutsch verfügbar").
Übersetzt wird nicht – eine maschinelle Übersetzung wäre nicht mehr der fachlich freigegebene Wortlaut
([D04](../../../docs/decisions/D04-Fachinhalte.md)). Beispiel dafür:
`examples/chat-response-general-en.json`.

**KI-Kennzeichnung (T-U028-03).** Drei Felder statt eines:

- `origin` (`model` | `fixed_text`) macht feste Systemtexte maschinell unterscheidbar. Das war die
  Abnahmebedingung des Tasks.
- `ai_generated` ist Pflichtfeld und genau dann `true`, wenn `origin` den Wert `model` hat. Bei
  `fixed_text` ist der Wortlaut fachlich freigegeben und stammt nicht vom Modell, deshalb `false`
  (entschieden). Die Herkunft steht in `origin`.
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
`publisher` ← `herausgeber`, `url` ← `quelle`, `review_date` ← `review_datum`. Nur Einträge mit
`status: geprueft` ([D04](../../../docs/decisions/D04-Fachinhalte.md)). Eine leere Liste ist erlaubt
(fester Text) und bedeutet nicht, dass keine Quelle nötig wäre.

**Versionen sind Ganzzahlen.** `ai_disclosure.version` und `notice.version` verweisen auf das Kopfdatum
`version` in `knowledge/`. Eine Ganzzahl genügt: Für den Nachweis zählt, welcher Wortlaut angezeigt wurde,
nicht wie groß die Änderung war.

**Kopfdaten in `knowledge/` (erledigt mit DOC-001).** `herausgeber`, `version` und `sprache` sind seit
DOC-001 Pflichtkopfdaten; `sprache` ist die Quelle für `content_language`. F007 kann die Felder also
befüllen.

**Testinhalte kennzeichnen (D10).** Solange kein fachlicher Reviewer benannt ist, dürfen Einträge mit
`status: testfreigabe` verwendet werden – nur bei `APP_ENV=development` und nur gekennzeichnet
([D10](../../../docs/decisions/D10-Testlauf.md)). Der Vertrag bildet das mit drei Stellen ab:

- `review_status` (`geprueft` | `testfreigabe`) an `notice` und an jeder Quelle – sagt, woher der einzelne
  Text kommt. `entwurf` erscheint nie, weil solche Einträge nicht geladen werden.
- `contains_test_content` an der Antwort – `true`, sobald mindestens ein verwendeter Eintrag
  `testfreigabe` ist. Damit zeigt die Oberfläche **einmal** „Testinhalt, nicht fachlich geprüft“, statt
  jede Quelle einzeln prüfen zu müssen. Außerhalb von `APP_ENV=development` immer `false`.
- `publisher`, `url` und `review_date` sind nullable geworden: Ein Testinhalt hat weder Herausgeber noch
  Freigabedatum. Bei `review_status: geprueft` sind alle drei gesetzt.

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
| `chat-request.json` | erste Nachricht in einem neuen Chat, `language: de` |
| `chat-request-en.json` | Oberfläche auf Englisch, `language: en` |
| `chat-response-general.json` | allgemeine Information, `origin: model`, mit Quelle |
| `chat-response-general-en.json` | Antwort auf Englisch, Quelle nur auf Deutsch (`content_language: de`) |
| `chat-response-emergency.json` | fester Notfallhinweis, `origin: fixed_text`, `ai_generated: false` |
| `chat-error-message-empty.json` | leerer Text |
| `chat-error-message-too-long.json` | überlange Eingabe |

## Entschiedene Punkte (Atakan, 14.10.2026)

| # | Frage | Entscheidung | Folge im Vertrag |
| --- | --- | --- | --- |
| 1 | Maximale Eingabelänge | 2000 Zeichen, bestätigt | `maxLength: 2000` unverändert |
| 2 | `publisher` | bleibt im Vertrag; `knowledge/` bekommt das Kopfdatum `herausgeber` | `Source.publisher` bleibt Pflichtfeld, Herkunft dokumentiert |
| 3 | Versionen | `knowledge/` bekommt `version` als Ganzzahl | `ai_disclosure.version` und `notice.version` sind `integer`, `minimum: 1` |
| 4 | Sprache | `language` bleibt, Enum `["de", "en"]`, Auswahl in der UI, keine automatische Erkennung | neues `content_language` an `notice` und `sources`, englisches Beispielpaar |
| 5 | `ai_generated` bei festem Text | `false`; `origin` kennzeichnet die Herkunft | unverändert, Begründung ergänzt |
| 6 | Streaming | kein Streaming in v1, Neubewertung nach Latenzmessung D03 | Hinweis in der Endpunktbeschreibung |
| 7 | Wiederholte `client_message_id` | identische Antwort einschließlich Status `201` | Beschreibung von `client_message_id` präzisiert |
| 8 | `rate_limited` | Fehlercode bleibt, keine Grenze festgelegt | unverändert, Grenze in eigenem Task |

Die Punkte 2 und 3 sind mit **DOC-001** in `knowledge/` umgesetzt.

## Nachtrag DOC-001 (14.10.2026)

- Neue Felder für den Testlauf: `review_status`, `contains_test_content`; `publisher`, `url` und
  `review_date` nullable (siehe oben).
- `knowledge_id` in den Beispielen zeigt jetzt auf die tatsächlich angelegten Entwürfe
  (`topic-eisenmangel`, `rule-notfallhinweis`).
- **`notice-ki-hinweis` bleibt eine erfundene Platzhalter-ID.** Der Transparenzhinweis aus T-U028-01
  existiert noch nicht in `knowledge/`; sobald er angelegt ist, wird die ID in den Beispielen angeglichen.

## Noch offen

- PR-Review dieses Vertrags.
- Grenze für `rate_limited` (eigener Task).
- Fachliche Freigabe aller Inhalte, auf die der Vertrag verweist (D04). Bis dahin tragen alle Beispiele
  `review_status: testfreigabe`.
- `ai_disclosure` verweist noch auf keinen existierenden Eintrag (T-U028-01).
