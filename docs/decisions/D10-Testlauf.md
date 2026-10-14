---
id: D10
status: bestaetigt
bestaetigt_von: Atakan
bestaetigt_am: 2026-10-14
---

# D10 – Testlauf: eine Person, alle Rollen

**Status: Bestätigt am 14.10.2026 durch Atakan.** Befristet, siehe „Ende der Befristung“.

## Problem

[D04](D04-Fachinhalte.md) verlangt einen benannten fachlichen Reviewer, und harte Regel 6 lässt im Code nur
Inhalte mit `status: geprueft` zu. Beides ist richtig – aber solange kein Reviewer benannt ist, gibt es
keinen einzigen verwendbaren Eintrag in `knowledge/`. Damit lässt sich kein Ablauf von Ende zu Ende
ausprobieren: Der Chat hätte nichts zu antworten. Gleichzeitig arbeitet im Testlauf **eine Person in allen
Rollen** (Umsetzung, Review, Merge), sodass auch der Vier-Augen-Teil des Arbeitsablaufs nicht wörtlich
erfüllbar ist.

## Beschluss

### Dritter Status in `knowledge/`

Das Statusfeld kennt drei Werte statt zwei:

| Status | Bedeutung | Darf der Code laden |
| --- | --- | --- |
| `entwurf` | in Arbeit, inhaltlich unfertig | nein |
| `testfreigabe` | formal vollständig, **fachlich nicht geprüft** | nur bei `APP_ENV=development` |
| `geprueft` | von der benannten fachlichen Person freigegeben | ja, immer |

Regeln dazu:

1. `testfreigabe` wird **nur bei `APP_ENV=development`** geladen. In jeder anderen Umgebung verhält sich
   der Eintrag wie nicht vorhanden – es gibt keinen Schalter, der das aufhebt.
2. Jede Antwort, die einen Eintrag mit `testfreigabe` verwendet, ist in der Oberfläche und im API-Vertrag
   als **„Testinhalt, nicht fachlich geprüft“** gekennzeichnet. Im Vertrag dafür: `review_status` an
   `notice` und an jeder Quelle, `contains_test_content` an der Antwort
   (`contracts/api/draft/chat-v1.openapi.yaml`).
3. `geprueft` erfordert unverändert `reviewer`, `review_datum` und `quelle`. Eine KI setzt diesen Status
   nie.
4. `testfreigabe` lässt `reviewer` und `review_datum` leer. Der Strukturcheck erlaubt den Status, listet
   ihn aber als Warnung auf, damit er sichtbar bleibt.
5. Alles andere bleibt: Nichts erfinden. Ein Eintrag mit `testfreigabe` darf nur Inhalte enthalten, die
   aus einer belegbaren Quelle stammen (z. B. wörtlich aus der Design-Vorlage). Fehlt der Text, steht dort
   ein ausdrücklicher Platzhalter und kein ausgedachter Inhalt.

Harte Regel 6 und D04 bleiben im Wortlaut bestehen und verweisen nur auf diese Ausnahme.

### Rollen im Testlauf

Eine Person übernimmt Umsetzung, Review und Merge. Das Review ist dann die **eigene Durchsicht des Diffs
vor dem Merge** – nicht das Überspringen des Reviews. Branch und PR bleiben Pflicht, weil der PR der Ort
ist, an dem der Diff am Stück lesbar ist. Branch-Schutz wird erst eingerichtet, wenn CI existiert (F004);
vorher würde er nur den einzigen Weg blockieren, ohne etwas zu prüfen.

Ablauf siehe `docs/Arbeitsablauf.md`, Abschnitt „Testlauf“.

## Ende der Befristung

D10 ist eine Übergangsregel. Sobald eine fachliche Reviewerin oder ein fachlicher Reviewer nach D04
benannt ist:

1. Alle Einträge mit `testfreigabe` werden fachlich geprüft und auf `geprueft` oder `entwurf` gesetzt.
2. Der Status `testfreigabe` entfällt aus `knowledge/TEMPLATE.md` und aus dem Strukturcheck.
3. Die Kennzeichnungsfelder im Vertrag bleiben, verlieren aber ihren Anwendungsfall.
4. D10 bekommt `status: ersetzt` mit Verweis auf D04.

Solange D10 gilt, ist **keine Demo außerhalb der Entwicklungsumgebung** zulässig, in der Testinhalte
ausgeliefert werden.

## Alternativen

- **Warten, bis ein Reviewer benannt ist.** Sauber, blockiert aber jeden Ablauf von Ende zu Ende auf
  unbestimmte Zeit.
- **Inhalte vorläufig als `geprueft` markieren.** Verstößt gegen D04 und gegen harte Regel 6 und macht den
  Unterschied zwischen geprüft und ungeprüft unsichtbar. Abgelehnt.
- **Inhalte im Code festschreiben.** Verstößt gegen harte Regel 6 und gegen `features/guidance`. Abgelehnt.

## Offene Punkte

- Fachliche Person nach D04 benennen – das beendet diese Entscheidung.
- Prüfen, ob `APP_ENV` in der Konfiguration ausreicht oder ob der Loader einen eigenen Schalter braucht
  (gehört zur Umsetzung in `features/guidance`, nicht hierher).

## Betroffen

`knowledge/`, `scripts/check_structure.py`, `contracts/api/draft/`, `features/guidance/`,
`docs/Arbeitsablauf.md`, harte Regel 6 in `AGENTS.md`, [D04](D04-Fachinhalte.md).
