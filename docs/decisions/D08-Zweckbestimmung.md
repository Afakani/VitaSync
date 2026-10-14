---
id: D08
status: bestaetigt
bestaetigt_von: Atakan (Projektvorgabe)
bestaetigt_am: 2026-10-14
---

# D08 – Zweckbestimmung: kein Medizinprodukt

**Status: Bestätigt als Projektvorgabe.** Formale Einschätzung durch die Betreuung noch einholen und hier verlinken.

## Grundsatz

VitaSync macht **keine Aussage über den Gesundheitszustand einer konkreten Person**. Ob Software ein Medizinprodukt ist, hängt davon ab, was sie tatsächlich tut, nicht von einem Hinweistext. Deshalb wird die Grenze im Funktionsumfang gezogen.

## Erlaubt

- Allgemeine Gesundheits- und Lifestyle-Information aus geprüften Quellen (gleich für alle Nutzer)
- Allgemein erklären, welche Stelle wofür zuständig ist (Hausarzt, Facharztrichtungen, 116117, 112)
- Fester, für alle gleicher Notfallhinweis, wenn ein Warnzeichen-Stichwort genannt wird
- Eigene Daten unverändert anzeigen (Wert, Einheit, Zeitpunkt, Quelle)
- Rein rechnerische Auswertungen (Mittelwert, Differenz, Anzahl) ohne Bewertung
- Dokumentieren: Symptomtagebuch, Profil als Selbstauskunft, PDF-Zusammenfassung eigener Angaben
- Text aus eigenen Dokumenten auslesen, mit Bestätigung durch den Nutzer

## Nicht erlaubt

- Diagnose oder Verdachtsdiagnose, auch nicht „könnte sein“
- Werte als normal, auffällig, gut oder schlecht bewerten; Referenzbereiche neben eigene Werte stellen
- Individuelle Dringlichkeitseinstufung (Triage), z. B. „Sie sollten heute noch zum Arzt“
- Ursachen von Beschwerden einordnen oder Zusammenhänge zwischen Beschwerden herstellen
- Aus Daten einen Mangel oder eine Erkrankung ableiten (z. B. Eisenmangel aus Ferritin)
- Medikamente, Dosierungen, Therapien oder Therapieänderungen empfehlen
- Medizinische Bilder bewerten (Haut, Röntgen, Wunden)
- Vorerkrankungen oder Profilangaben zur Bewertung heranziehen

## Grenzfall Beispiel Eisenmangel

- Erlaubt: Nutzer sagt „Ich habe Eisenmangel“ → allgemeine Information zu eisenreichen Lebensmitteln, Hinweis auf Hausarzt.
- Nicht erlaubt: System sieht niedrige Werte → „Sie haben vermutlich Eisenmangel, essen Sie mehr Fisch“.

## Auswirkungen

- Backlog: U002, U003, U018, U031 gestrichen; U001, U006, U008, U013, U014, U019, U029, U030 umgebaut (Spalte „Zweckprüfung (D08)“).
- Regeln: Root-`AGENTS.md` (harte Regeln), `features/guidance`, `features/analysis`, `knowledge/`, `evals/`.
- Evals: `evals/answers/` prüft, dass keine Antwort Diagnose, Bewertung oder Dringlichkeitseinstufung enthält.

## Nebeneffekt AI Act

KI-Systeme zur Triage von Notfallpatienten gelten nach AI Act als Hochrisiko-KI (Anhang III Nr. 5 d). Weil VitaSync keine Dringlichkeitseinstufung macht, entfällt auch diese Einstufung. Siehe [D09](D09-Datenschutz-EU.md).

## Offene Punkte

- Schriftliche Einschätzung der Betreuung einholen.
