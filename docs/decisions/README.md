# Entscheidungen

Eine Datei pro Entscheidung. Status im Kopf: `offen`, `empfohlen`, `bestaetigt`, `ersetzt`.
Bestätigen = `status: bestaetigt`, `bestaetigt_von`, `bestaetigt_am` ausfüllen, im PR reviewen lassen.

| ID | Thema | Status |
| --- | --- | --- |
| [D01](D01-Stack.md) | Stack und Repository | bestaetigt |
| [D02](D02-FHIR.md) | FHIR-Version, Ressourcen, Messgrößen | empfohlen |
| [D03](D03-Modell.md) | Lokales Modell und Laufzeit | empfohlen |
| [D04](D04-Fachinhalte.md) | Fachinhalte, Quellen, Freigabe | empfohlen |
| [D05](D05-Identitaet-Einwilligung.md) | Identität, Einwilligung, Logs | empfohlen |
| [D06](D06-Speicherung.md) | Speicherung und Löschung | empfohlen |
| [D07](D07-Optionaler-Umfang.md) | Optionaler Umfang | empfohlen |
| [D08](D08-Zweckbestimmung.md) | Zweckbestimmung: kein Medizinprodukt | bestaetigt |
| [D09](D09-Datenschutz-EU.md) | Datenschutz und EU-Recht | empfohlen |
| [D10](D10-Testlauf.md) | Testlauf: eine Person, alle Rollen | bestaetigt |

Neue Entscheidung: `docs/vorlagen/ENTSCHEIDUNG.md` kopieren, nächste freie ID (D11 …).
