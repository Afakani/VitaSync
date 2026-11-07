"""Einstellungen aus Umgebungsvariablen.

Nutzt nur Standardbibliothek und Pydantic, damit `core` frei von
Infrastruktur bleibt (siehe `core/AGENTS.md`). Konfiguration kommt
ausschliesslich aus der Umgebung, Vorlage ist `.env.example` im Root.
"""
from __future__ import annotations

import os

from pydantic import BaseModel, Field

#: Vorgabe, falls APP_ENV nicht gesetzt ist.
DEFAULT_APP_ENV = "development"


class Settings(BaseModel):
    """Laufzeiteinstellungen der API.

    Attribute:
        app_env: Umgebungsname, z. B. `development`.
        log_level: Logstufe fuer die Anwendung.
        database_url: Verbindung zur PostgreSQL-Datenbank. Leer, solange
            kein Datenbankzugriff implementiert ist.
        llm_base_url: Adresse der lokalen Modell-Laufzeit (Ollama).
        llm_model: Modellname, z. B. `qwen3:8b`. Leer = kein Modellaufruf moeglich.
        llm_timeout_s: maximale Wartezeit je Modellaufruf in Sekunden.
        cp1_patterns: Pfad zur CP1-Musterdatei (Notfall, Krise, Injection).
        router_policy: Schalter fuer offene Teamentscheidungen, Format
            `key=value,key=value` (siehe `core.intent.Policy`). Leer = vorsichtige Vorgaben.

    Enthaelt bewusst keine Gesundheitsdaten und keine Geheimnisse im Klartext
    als Vorgabewert.
    """

    app_env: str = Field(default=DEFAULT_APP_ENV, min_length=1)
    log_level: str = Field(default="INFO", min_length=1)
    database_url: str = Field(default="")
    llm_base_url: str = Field(default="http://localhost:11434", min_length=1)
    llm_model: str = Field(default="")
    llm_timeout_s: float = Field(default=120.0, gt=0)
    cp1_patterns: str = Field(default="knowledge/rules/cp1_patterns.json", min_length=1)
    router_policy: str = Field(default="")


def load_settings(env: dict[str, str] | None = None) -> Settings:
    """Liest die Einstellungen aus der Umgebung.

    Args:
        env: Abbildung von Variablennamen auf Werte. Ohne Angabe wird
            `os.environ` genutzt. Der Parameter existiert, damit Tests ohne
            Veraenderung der Prozessumgebung laufen koennen.

    Returns:
        Geprueftes `Settings`-Objekt.

    Raises:
        pydantic.ValidationError: Wenn ein gesetzter Wert leer oder
            ungueltig ist.
    """
    source = os.environ if env is None else env
    return Settings(
        app_env=source.get("APP_ENV", DEFAULT_APP_ENV),
        log_level=source.get("LOG_LEVEL", "INFO"),
        database_url=source.get("DATABASE_URL", ""),
        llm_base_url=source.get("LLM_BASE_URL", "http://localhost:11434"),
        llm_model=source.get("LLM_MODEL", ""),
        llm_timeout_s=float(source.get("LLM_TIMEOUT_S", "120")),
        cp1_patterns=source.get("CP1_PATTERNS", "knowledge/rules/cp1_patterns.json"),
        router_policy=source.get("ROUTER_POLICY", ""),
    )
