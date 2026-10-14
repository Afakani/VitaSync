---
id: D03
status: empfohlen
bestaetigt_von:
bestaetigt_am:
---

# D03 – Lokales Modell, Hardware und Laufzeitgrenzen

**Status: Empfohlen, nicht bestätigt.** Stand der Recherche: 14.10.2026. Vor Bestätigung Modell-Tags in Ollama und Lizenz erneut prüfen.

## Zielhardware (Referenzrechner)

- GPU mit 12 GB VRAM, 32 GB Arbeitsspeicher
- Quantisierung Q4, Kontext 8K, KV-Cache F16 (bei Engpass Q8)

## Anforderungen

- Chat auf Deutsch, Anfrageerkennung mit JSON-Ausgabe (Pflicht)
- Dateianalyse, z. B. Laborbefund als PDF (optional, später)
- Bildanalyse, z. B. Foto eines Befunds (optional, später)
- Möglichst **ein** Modell für alles. Zwei Modelle passen nicht gleichzeitig in 12 GB, und Umladen kostet Sekunden pro Anfrage.

## Empfehlung

| Rolle | Modell | Lizenz | Begründung |
| --- | --- | --- | --- |
| **Hauptkandidat** | Gemma 4 12B | Apache 2.0 | Text und Bilder in einem Modell, Q4 passt in 12 GB mit Platz für 8K-Kontext. Seit Gemma 4 freie Lizenz. |
| **Gegenkandidat** | Qwen3-VL 8B Instruct | Apache 2.0 | Kleiner und schneller, stark bei Texterkennung in Dokumenten und Bildern (OCR). |
| Fallback für schwache Rechner | Gemma 4 E4B | Apache 2.0 | Läuft auch auf Laptops ohne starke GPU, deutlich schwächer. |

Nicht empfohlen: Modelle ab 24B (z. B. Gemma 4 26B/31B). Sie passen nicht vollständig in 12 GB; ein Teil wird in den Arbeitsspeicher ausgelagert, und die Antworten werden mehrfach langsamer.

**Entscheidung zwischen Haupt- und Gegenkandidat nur per Messung** mit `evals/` auf dem Referenzrechner:

| Messgröße | Gemma 4 12B | Qwen3-VL 8B |
| --- | --- | --- |
| Trefferquote Anfrageerkennung | | |
| Anteil gültiger JSON-Ausgaben | | |
| Deutsch-Qualität (Bewertung durch 2 Personen) | | |
| Latenz Median / 95 % | | |
| Texterkennung auf 10 synthetischen Befundbildern | | |

## Datei- und Bildanalyse richtig aufteilen

- **Strukturierte Dateien** (FHIR-JSON, CSV) werden vom Code eingelesen, nicht vom Modell.
- **PDFs mit Textebene:** Text per Bibliothek extrahieren, das Modell bekommt nur den Text.
- **Scans und Fotos von Dokumenten:** Das Bildmodell liest die Werte aus. Danach werden Wert, Einheit und Datum dem Nutzer zur **Bestätigung** angezeigt, bevor sie gespeichert oder verwendet werden. Lesefehler sind sonst nicht auffindbar.
- **Nicht im Umfang:** medizinische Bilder bewerten (Hautveränderungen, Röntgen, Wunden). Das wäre eine Diagnose. Solche Bilder werden mit einem Hinweis auf eine ärztliche Anlaufstelle abgelehnt.
- Ein Bild belegt je nach Auflösung mehrere hundert bis über tausend Token. Bei 8K Kontext höchstens ein bis zwei Bilder pro Anfrage; die Bildgröße serverseitig begrenzen.

## Modell später wechseln

Vorgesehen und einfach, solange diese Regeln gelten:
- Modellname kommt nur aus der Konfiguration (`.env`), nie aus dem Code.
- Alle Modellzugriffe laufen über den Port in `core/ports.py`; nur `adapters/llm/` kennt Ollama.
- Ausgaben werden immer gegen `contracts/llm/` validiert, egal welches Modell.
- Wechsel = Modell ziehen, Konfiguration ändern, `evals/` laufen lassen, Ergebnis im PR. Prompts können pro Modell nachjustiert werden; dafür neue Prompt-Version anlegen.
- Wechsel auf eine andere Laufzeit (z. B. llama.cpp, vLLM) = neuer Adapter, Features bleiben unverändert.

## Laufzeit und Grenzen

- **Laufzeit: Ollama.** Erzwingt JSON-Schemas in der Ausgabe und unterstützt Bildeingaben.
- **Adaptervertrag** (`core/ports.py`): Nachrichten, optional Bilder und JSON-Schema → validierte Ausgabe oder definierter Fehler. Ein Fake-Adapter für Tests ist Pflicht. Das Modell bleibt austauschbar.
- **Startwerte, dann messen:** Timeout 30 s (mit Bild 60 s), Ausgabelänge begrenzen, Temperatur 0–0,3 für die Erkennung, keine Werkzeugaufrufe durch das Modell.
- **Aufgaben des Modells:** Anfrage klassifizieren, Angaben extrahieren, Dokumente lesen, freigegebene Inhalte verständlich formulieren. **Nicht:** rechnen, Dringlichkeit festlegen, Rechte prüfen, medizinische Regeln erzeugen, Bilder medizinisch bewerten, Werte oder Beschwerden einer Person bewerten (D08).

## Offene Punkte

- Läuft die Demo auf diesem Referenzrechner oder auf einem anderen?
- Haben die anderen Teammitglieder schwächere Hardware? Dann entwickeln sie mit dem Fake-Adapter oder mit Gemma 4 E4B und testen nur final auf dem Referenzrechner.

## Betroffen

`apps/api/src/vitasync/adapters/llm/`, `contracts/llm/`, `evals/`, `infra/`, Task F001, F008, U022, U032.
