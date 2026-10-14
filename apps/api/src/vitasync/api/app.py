"""Aufbau der FastAPI-Anwendung.

Enthaelt bewusst nur den Lebenszeichen-Endpunkt. Fachliche Routen entstehen
in den jeweiligen Task-IDs, der Chat-Vertrag z. B. mit F003.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI
from pydantic import BaseModel

from vitasync.core.config import Settings, load_settings


def _app_version() -> str:
    """Gibt die installierte Paketversion zurueck, sonst `unknown`."""
    try:
        return version("vitasync")
    except PackageNotFoundError:
        return "unknown"


class LivenessResponse(BaseModel):
    """Antwort des Lebenszeichen-Endpunkts.

    Attribute:
        status: Immer `ok`, wenn der Prozess Anfragen annimmt.
        version: Installierte Version des Pakets `vitasync`.
        app_env: Aktive Umgebung aus der Konfiguration.

    Bewusst ohne Gesundheitsdaten, Nutzerbezug und Infrastrukturdetails.
    """

    status: str
    version: str
    app_env: str


def create_app(settings: Settings | None = None) -> FastAPI:
    """Erzeugt die FastAPI-Anwendung.

    Args:
        settings: Einstellungen. Ohne Angabe werden sie aus der Umgebung
            gelesen. Tests koennen eigene Werte uebergeben.

    Returns:
        Fertig verdrahtete `FastAPI`-Instanz.
    """
    active = load_settings() if settings is None else settings
    app = FastAPI(
        title="VitaSync API",
        version=_app_version(),
        summary=(
            "Allgemeine Gesundheitsinformationen. Kein Medizinprodukt: "
            "keine Diagnose, keine Bewertung eigener Werte, keine "
            "Dringlichkeitseinstufung (D08)."
        ),
    )

    # Name bewusst /healthz: Lebenszeichen des Prozesses, nicht zu
    # verwechseln mit den Gesundheitsdaten in features/health_data.
    @app.get("/healthz", response_model=LivenessResponse, tags=["betrieb"])
    def healthz() -> LivenessResponse:
        """Meldet, dass der Prozess Anfragen annimmt."""
        return LivenessResponse(
            status="ok",
            version=app.version,
            app_env=active.app_env,
        )

    return app


#: Einstiegspunkt fuer `uvicorn vitasync.api.app:app`.
app = create_app()
