# Server

Regeln und Aufbau: [AGENTS.md](AGENTS.md). Stack: [D01](../../docs/decisions/D01-Stack.md).

Stand F002: leere, startbare Anwendung mit dem Lebenszeichen-Endpunkt `/healthz`. Noch keine Fachlogik.

## Voraussetzungen

- Python 3.12
- Docker (Pflicht, es gibt keinen Weg ohne; siehe D01)

## Einrichten

Alle Befehle vom Wurzelverzeichnis des Repositorys aus.

```bash
# 1. Konfiguration anlegen und POSTGRES_PASSWORD setzen
cp .env.example .env

# 2. Datenbank starten
docker compose --env-file .env -f infra/docker-compose.yml up -d db

# 3. Virtuelle Umgebung und Abhängigkeiten
cd apps/api
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.lock -e ".[dev]"   # Windows
# .venv/bin/python -m pip install -r requirements.lock -e ".[dev]"         # Linux, macOS
```

`requirements.lock` hält die aufgelösten Versionen fest, `pyproject.toml` die direkten. Beides zusammen installieren, damit alle denselben Stand haben.

## Starten

```bash
cd apps/api
.venv/Scripts/python.exe -m uvicorn vitasync.api.app:app --reload --host 127.0.0.1 --port 8000
```

Prüfen: `curl http://127.0.0.1:8000/healthz` liefert `{"status":"ok",...}`. API-Schema: `http://127.0.0.1:8000/docs`.

## Tests

```bash
cd apps/api
.venv/Scripts/python.exe -m pytest
```

## Datenbank stoppen

```bash
docker compose --env-file .env -f infra/docker-compose.yml down
```

Daten bleiben im Volume `vitasync-db-data`. Mit `down -v` wird es gelöscht.

## Fehlerbehebung: Port belegt

Startet die Datenbank nicht oder bricht Compose mit einem Bind-Fehler ab, ist der Port auf dem Host schon belegt. Häufigste Ursache ist eine lokal installierte PostgreSQL auf `5432`. Deshalb ist die Vorgabe in `.env.example` bereits `5433`.

Belegung prüfen (Windows, PowerShell oder cmd):

```
netstat -ano | findstr :5432
```

Die letzte Spalte ist die PID. Dazu den Prozess finden:

```
tasklist /FI "PID eq <PID>"
```

Ist der Port belegt, in `.env` einen freien Port setzen, **beide** Stellen angleichen und neu starten:

```
POSTGRES_PORT=5434
DATABASE_URL=postgresql://vitasync:<passwort>@127.0.0.1:5434/vitasync
```

```bash
docker compose --env-file .env -f infra/docker-compose.yml up -d db
docker compose --env-file .env -f infra/docker-compose.yml port db 5432
```

Der letzte Befehl muss `127.0.0.1:<dein Port>` zeigen. Steht dort `0.0.0.0`, fehlt das Loopback-Präfix in `infra/docker-compose.yml`.

Die lokale PostgreSQL-Installation nicht beenden, um den Port freizumachen. Ein anderer Port im Container-Setup ist der harmlosere Weg.

## Hinweise

- `--env-file .env` ist nötig, weil Compose seine Env-Datei sonst neben `infra/docker-compose.yml` sucht.
- Der Datenbankport ist nur auf `127.0.0.1` veröffentlicht, nicht im Netz.
- Die LLM-Laufzeit (Ollama) läuft nativ auf dem Host und ist für diesen Stand nicht erforderlich.
