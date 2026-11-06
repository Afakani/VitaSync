@AGENTS.md

# Claude-spezifisch

`AGENTS.md` gilt vollständig. Hier steht nur, was zusätzlich für Claude gilt.

- Lokale `CLAUDE.md` in Unterordnern werden geladen, sobald du dort Dateien liest. Nicht alle vorab öffnen.
- Ändert die Arbeit mehr als zwei Dateien: erst einen kurzen Plan zeigen (Plan Mode), dann umsetzen.
- Subagenten nur, wenn der Auftrag es ausdrücklich erlaubt. Nie zwei Agenten auf dieselben Dateien.
- Jira und Confluence (Atlassian-MCP) nur lesen. Nichts anlegen, ändern, kommentieren oder verschieben ohne ausdrückliche Freigabe für die konkrete Aktion.
- Benchmark- und Modellläufe nur auf Ansage und nie parallel zu anderen GPU-Läufen; Zeitmessungen gelten nur bei freier GPU.
- Vor absehbarem Kontext- oder Limitende `planning/handoffs/<Jira-Key oder Kurzname>.md` aktualisieren.
- Bei Wiederaufnahme zuerst Übergabe, `git status` und Diff vergleichen; erledigte Schritte nicht wiederholen.
- Fehlt eine Entscheidung oder fachliche Regel: konkret fragen. Im nicht interaktiven Lauf die Frage in die Übergabe schreiben und nur unabhängige Teile fortsetzen.
- Keine Emojis. Abschlussbericht wie in `AGENTS.md`, kurz.
