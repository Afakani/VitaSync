"""Gemeinsame Fixtures fuer die API-Tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from vitasync.api.app import create_app
from vitasync.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Feste Testeinstellungen, unabhaengig von der Prozessumgebung."""
    return Settings(app_env="test", log_level="INFO", database_url="")


@pytest.fixture
def client(settings: Settings) -> TestClient:
    """TestClient gegen eine frisch gebaute Anwendung."""
    return TestClient(create_app(settings))
