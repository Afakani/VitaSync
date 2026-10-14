# Planung

| Datei / Ordner | Zweck |
| --- | --- |
| `VitaSync_Coding_Backlog.xlsx` | Plan **und Statusquelle**: Stories, Tasks, Briefings, DoD. |
| `work-orders/` | Ausformulierte Aufträge für Claude/Codex, wenn das Issue nicht reicht. |
| `handoffs/` | Übergaben bei Unterbrechung, eine Datei pro Task-ID. |

## Statusquelle

Der Status eines Tasks steht in der Spalte **Status** im Blatt **Tasks**. Es gibt keine zweite Quelle.

- Wer umsetzt, setzt die eigene Zeile im selben PR auf **„Im Review“**.
- Nach der Freigabe durch die reviewende Person folgt im selben PR ein **letzter Commit** mit Status
  **„Erledigt“** und der PR-Nummer in der Spalte „Änderung“. Danach wird gemergt.
- Ein eigener PR nur für eine Statusänderung ist nicht vorgesehen.
- GitHub Issues sind optional. Werden sie genutzt, sind sie Diskussionsort, nicht Statusquelle.

Ablauf und Rollen: [docs/Arbeitsablauf.md](../docs/Arbeitsablauf.md).

## Auftrag an Claude/Codex (Kopiervorlage)

```
Bearbeite genau Task <TASK-ID>. Auftrag: <Issue-Link oder planning/work-orders/<TASK-ID>.md>.
Lies vorher die AGENTS.md der betroffenen Ordner und die betroffene Entscheidung in docs/decisions/.
Fehlt eine Entscheidung oder fachliche Regel: frag nach, erfinde nichts.
Branch task/<TASK-ID>-<kurzname>. Ende: PR nach Vorlage, Status "Im Review".
```
