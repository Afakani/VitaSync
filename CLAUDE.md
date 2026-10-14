@AGENTS.md

# Claude-spezifisch

`AGENTS.md` gilt vollständig. Hier steht nur, was zusätzlich für Claude gilt.

- Lokale `CLAUDE.md` in Unterordnern werden geladen, sobald du dort Dateien liest. Nicht alle vorab öffnen.
- Ändert der Task mehr als zwei Dateien: erst einen kurzen Plan zeigen (Plan Mode), dann umsetzen.
- Subagenten nur, wenn der Auftrag es ausdrücklich erlaubt. Nie zwei Agenten auf dieselben Dateien.
- Vor absehbarem Kontext- oder Limitende `planning/handoffs/<TASK-ID>.md` aktualisieren.
- Bei Wiederaufnahme zuerst Übergabe, `git status` und Diff vergleichen; erledigte Schritte nicht wiederholen.
- Fehlt eine Entscheidung oder fachliche Regel: konkret fragen. Im nicht interaktiven Lauf die Frage in die Übergabe schreiben und nur unabhängige Teile fortsetzen.
- Keine Emojis. Abschlussbericht wie in `AGENTS.md`, kurz.
