"""Rauchtest fuer den Lebenszeichen-Endpunkt.

Prueft Verhalten, nicht Implementierung: Der Endpunkt antwortet, meldet die
aktive Umgebung und gibt keine unerwarteten Felder heraus.
"""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz_meldet_ok(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_env"] == "test"


def test_healthz_gibt_nur_erwartete_felder(client: TestClient) -> None:
    body = client.get("/healthz").json()

    assert set(body) == {"status", "version", "app_env"}


def test_openapi_schema_ist_abrufbar(client: TestClient) -> None:
    """F003 exportiert daraus `contracts/api/openapi.json`."""
    schema = client.get("/openapi.json")

    assert schema.status_code == 200
    assert "/healthz" in schema.json()["paths"]
