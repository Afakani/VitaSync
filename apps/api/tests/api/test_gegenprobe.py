"""Gegenprobe F004: muss scheitern. Wird nach dem Lauf geloescht."""
from fastapi.testclient import TestClient


def test_gegenprobe_schlaegt_absichtlich_fehl(client: TestClient) -> None:
    assert client.get('/healthz').json()['status'] == 'absichtlich-falsch'
