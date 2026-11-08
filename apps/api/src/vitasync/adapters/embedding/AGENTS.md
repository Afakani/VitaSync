# Modul: Embedding-Adapter

Zweck: Macht aus Texten Vektoren für den SLM-Erkenner (`features/recognition/slm.py`). Implementiert `EmbedderPort` aus `core/ports.py`.
Zuständig: Atakan Cubukcu

## Grenzen
- Darf nutzen: `core/`, Standardbibliothek (HTTP über `urllib`).
- Darf nicht: Flags oder Routen bestimmen; Texte oder Vektoren loggen; den API-Schlüssel in Fehlermeldungen oder Logs schreiben; echte Nutzertexte an externe Dienste schicken.

## Verträge
- `OllamaEmbedder(model, base_url)`: lokal über Ollama `/api/embed`. Standard (`EMBED_BACKEND=ollama`, `EMBED_MODEL=qwen3-embedding:8b`).
- `ApiEmbedder(model, api_base, api_key)`: OpenAI-kompatibles `/embeddings`, nur für Tests mit synthetischen Daten und nur auf ausdrücklichen Wunsch (`EMBED_BACKEND=api`).
- `FakeEmbedder` für Tests. Alle Vektoren werden auf Länge 1 normalisiert; Stapel zu 32 Texten, Wiederholung bei 429/5xx.

## Tests
- Über `tests/features/recognition/test_slm.py` und `tests/features/chat/test_intake.py` (Fake).

## Fallen
- Tolgas Gewichte (`apps/api/models/slm_lr_qwen3-embedding-8b.json`) wurden mit Vektoren von KI:connect trainiert. Die lokale Ollama-Fassung ist quantisiert; die Vektoren weichen leicht ab. Vor dem Einsatz gegen den API-Stand messen oder neu trainieren.
- Ollama und die API nennen dasselbe Modell verschieden (`qwen3-embedding:8b` bzw. `qwen-qwen3-embedding-8b`).
- Unter Windows nie `localhost` als Ollama-Adresse: "localhost" wird zuerst als IPv6 `::1` aufgelöst, Ollama hört nur auf IPv4, jeder Aufruf wartet ~2,1 s. Immer `http://127.0.0.1:11434` (gemessen 08.11.2026: 2.123 ms gegenüber 82 ms je Embedding).
