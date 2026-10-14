---
id: D04
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D04 – Fachliche Inhalte, Quellen und Freigabe

**Status: Empfohlen, nicht bestätigt.** Diese Entscheidung ist das größte Projektrisiko: Sie blockiert elf Tasks, und ohne fachliche Prüfung darf keine Gesundheitsfunktion als fertig gelten.

## Empfehlung

1. **Fachlichen Reviewer benennen.** Eine Person mit medizinischer Qualifikation (Betreuung, Kooperationspartner, Medizinstudierende unter Aufsicht). Ohne Namen bleibt D04 offen.
2. **Kleiner Demo-Umfang**, je Thema vollständig statt vieles halb:
   - Eisenmangel allgemein: was es ist, eisenreiche Lebensmittel, Hausarzt als Ansprechpartner (keine Ableitung aus Werten)
   - Zwei weitere allgemeine Themen aus dem Wissenspaket (U009)
   - Warnzeichen-Stichworte mit festem Notfallhinweis 112 / 116117 und allgemeine Zuständigkeiten (U001)
   - Fachfremde Frage → freundliche Abweisung (U004)
3. **Quellen nur aus anerkannten deutschen Stellen**, z. B. gesund.bund.de (Bundesgesundheitsministerium), gesundheitsinformation.de (IQWiG), DGE für Ernährung, 116117.de für Versorgungswege. Jede Regel nennt ihre Quelle.
4. **Format:** Jeder Inhalt ist eine Datei in `knowledge/` mit Kopfdaten (Quelle, Status, Reviewer, Datum). Der Code lädt nur `status: geprueft`. Der Strukturcheck erzwingt die Kopfdaten. Ausnahme im Testlauf siehe [D10](D10-Testlauf.md).
5. **Ablauf:** Research-Task schreibt Entwurf → Reviewer prüft und setzt `geprueft` → erst dann Code-Task, der den Inhalt nutzt.

## Rahmen

- Alle Inhalte sind allgemein und für alle Nutzer gleich. Grenze zum Medizinprodukt: [D08](D08-Zweckbestimmung.md).
- KI-Kennzeichnung gegenüber Nutzern (U028) beibehalten.

## Betroffen

`knowledge/`, `features/guidance/`, `features/recognition/`, `evals/`, alle Tasks mit Entscheidung D04.

Durch D08 sinkt der Prüfaufwand deutlich: Der Reviewer prüft allgemeine Texte und eine Stichwortliste, keine individuellen Entscheidungsregeln.
