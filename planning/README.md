# Planung

| Datei / Ordner | Zweck |
| --- | --- |
| `VitaSync_Coding_Backlog.xlsx` | Plan: Stories, Tasks, Briefings, DoD. **Nicht** für Status verwenden. |
| `work-orders/` | Ausformulierte Aufträge für Claude/Codex, wenn das Issue nicht reicht. |
| `handoffs/` | Übergaben bei Unterbrechung, eine Datei pro Task-ID. |

Status und Zuweisung laufen über GitHub Issues (siehe [docs/Arbeitsablauf.md](../docs/Arbeitsablauf.md)). Die Excel-Spalten „Status“, „Verantwortlich“, „Bearbeiter“ nicht parallel pflegen.

## Auftrag an Claude/Codex (Kopiervorlage)

```
Bearbeite genau Task <TASK-ID>. Auftrag: <Issue-Link oder planning/work-orders/<TASK-ID>.md>.
Lies vorher die AGENTS.md der betroffenen Ordner und die betroffene Entscheidung in docs/decisions/.
Fehlt eine Entscheidung oder fachliche Regel: frag nach, erfinde nichts.
Branch task/<TASK-ID>-<kurzname>. Ende: PR nach Vorlage, Status "Im Review".
```
