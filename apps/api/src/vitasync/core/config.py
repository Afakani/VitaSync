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

    Enthaelt bewusst keine Gesundheitsdaten und keine Geheimnisse im Klartext
    als Vorgabewert.
    """

    app_env: str = Field(default=DEFAULT_APP_ENV, min_length=1)
    log_level: str = Field(default="INFO", min_length=1)
    database_url: str = Field(default="")


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
    )
