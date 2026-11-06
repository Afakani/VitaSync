# Modul: Website (apps/web)

Zweck: Chat-Oberfläche: Eingabe, Verlauf, Lade-/Fehlerzustände, Einwilligung, KI-Kennzeichnung.
Zuständig: <GitHub-Handle eintragen>

## Grenzen
- Darf nutzen: eigene Komponenten, generierter API-Client aus `contracts/api/`.
- Darf nicht: Datenbank, LLM oder FHIR direkt ansprechen; Rechte nur im Frontend prüfen; API-Typen von Hand nachbauen.

## Verträge
- Nutzt `contracts/api/` über den generierten Client in `src/shared/api/`.

## Tests
- Komponententests neben der Datei (`*.test.tsx`), Ende-zu-Ende in `apps/web/e2e/`.
- Noch kein Build- oder Testbefehl. Keinen erfinden.

## Aufbau
- `src/features/<name>/`: ein Ordner pro Fachbereich (chat, consent, health-data). Feature-Ordner importieren sich nicht gegenseitig intern.
- `src/shared/components/`: wiederverwendbare UI ohne Fachlogik.
- `src/shared/api/`: generierter Client. Nicht von Hand bearbeiten.

## Design
- Verbindliche Vorlage: `design/vitasync-ui-v1.5.html` (Änderungen in `design/README.md`). Verbindlich sind **Layout, Farben, Abstände, Rundungen und UI-Rahmentexte** (Schaltflächen, Beschriftungen, Menüpunkte, Platzhalter, Fehlermeldungen der Oberfläche).
- **Nicht verbindlich sind die fachlichen Texte der Vorlage.** Gesundheits-, Notfall-, Zuständigkeits- und Datenschutztexte stehen dort nur als Platzhalter für die Darstellung. Im Produkt kommen sie zur Laufzeit aus `knowledge/` (Gesundheit, Notfall, Zuständigkeiten) bzw. `docs/compliance/` (Datenschutz) und werden nie aus der Vorlage abgeschrieben ([R1–R6](../../docs/decisions/README.md)).
- Design nicht eigenmächtig ändern. Abweichung nur mit Task und Freigabe; dann neue Version der Vorlage anlegen (v1.6 …), alte bleibt.
- Keine externen CDNs, Fonts oder Skripte (DSGVO). Alles lokal ausliefern.

## Fallen
- Modellantworten nie ungefiltert per `innerHTML` einsetzen. Als Text oder bereinigtes Markdown rendern (XSS).
- Keine Ampelfarben, Dringlichkeitslabels oder Diagnose-Titel in der UI (R1–R6).
- Zustände immer vollständig: laden, Fehler, leer, Timeout, Wiederholen ohne Doppelversand.
- Barrierefreiheit: Fokus, Tastaturbedienung, Kontrast.
