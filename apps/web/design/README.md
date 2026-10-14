# Design-Vorlage

`vitasync-ui-v1.5.html` ist die verbindliche Design-Vorlage für `apps/web`. Kein Produktcode: Antworten sind feste Demo-Texte.

Öffnen: Datei im Browser öffnen (der Ordner `vendor/` muss daneben liegen). Es werden keine externen Server angefragt.

## Änderungen gegenüber v1.4

| Bereich | v1.4 | v1.5 | Grund |
| --- | --- | --- | --- |
| Notfallantwort | „Dringlichkeitsstufe: Notfall“, „Verdacht auf akutes Koronarsyndrom“, Handlungsanweisungen | fester allgemeiner Notfallhinweis, 112 und 116117, „kann deine Situation nicht beurteilen“ | D08, AI Act Anhang III 5 d |
| Zusammenfassung / PDF | „Einschätzung: Sofort 112“ | nur Angaben des Nutzers und angezeigte Werte | D08, U014 |
| Chatverlauf | Ampelpunkte, Titel wie „Spannungskopfschmerz“ | keine Punkte, Titel in Nutzerworten | D08 |
| Kacheln | Medikamente/Dosierung, Laborwerte verstehen | Beschwerden festhalten, allgemeine Frage, eigene Werte ansehen, Zuständigkeiten | D08, U018 gestrichen |
| Profil | „Patient #8942“, Dauermedikation | „Testkonto“, nur Alter, Vorerkrankungen, Allergien als Selbstauskunft | D08, U019 |
| Einstellungen | „Herz-Warnhinweis aktiv“, „Lokale Sitzung“ | Datenschutzhinweis, Export, Löschen, Einwilligung widerrufen | D08, D09, U024, U033 |
| Einwilligung | fehlte | Dialog vor erster Nutzung, Ablehnen sperrt Eingabe, Widerruf verwirft laufende Antworten | U027, F016 |
| KI-Kennzeichnung | nur „AI“-Kürzel | dauerhaft im Header und unter der Eingabe, `data-ai-generated` an jeder Antwort | U028, T-U028-03, AI Act Art. 50 |
| Externe Ressourcen | Tailwind-CDN, unpkg | lokal unter `vendor/` | D09 (DSGVO) |
| Upload | pdf, Bilder, doc, docx, txt, ohne Limit | pdf, png, jpg, max. 10 MB | U032 |
| Sprache | Englisch zuerst | Deutsch zuerst | AGENTS.md |
| Barrierefreiheit | Profilkarte als `div` | `button`, `aria-label` an Icon-Buttons | Web-AGENTS.md |

## Tailwind neu bauen

`vendor/tailwind.css` ist aus `tailwind.config.js` (Tailwind 3.4.17) gebaut. Bei neuen Klassen neu bauen:

```
npx tailwindcss@3.4.17 -c tailwind.config.js -i <input.css mit @tailwind base/components/utilities> -o vendor/tailwind.css --minify
```

Icons: Phosphor Icons (MIT-Lizenz, `vendor/phosphor/LICENSE`).

## Offen

- Text des Notfallhinweises und Stichwortliste: fachliche Freigabe (D04).
- Datenschutzhinweis-Text: Abstimmung mit Betreuung (F016).
