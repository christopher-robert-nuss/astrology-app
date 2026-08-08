import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    preferences_path = tmp_path / "preferences.json"
    ephe_dir = tmp_path / "ephe"
    monkeypatch.setenv("ASTROLOGY_APP_PREFERENCES_PATH", str(preferences_path))
    monkeypatch.setenv("ASTROLOGY_APP_EPHE_DIR", str(ephe_dir))
    monkeypatch.setenv("ASTROLOGY_APP_DATA_DIR", str(tmp_path / "frontend-public"))
    with TestClient(app) as test_client:
        yield test_client


def test_preferences_endpoint_returns_defaults(client):
    response = client.get("/preferences")

    assert response.status_code == 200
    data = response.json()
    assert data["zodiac_type"] == "Tropical"
    assert data["houses_system"] == "P"


def test_preferences_options_endpoint_lists_supported_values(client):
    response = client.get("/preferences/options")

    assert response.status_code == 200
    data = response.json()
    assert "Tropical" in data["zodiac_types"]
    assert "Sidereal" in data["zodiac_types"]
    assert data["house_systems"]
    assert data["aspects"]


def test_ephemeris_status_endpoint_is_available(client):
    response = client.get("/ephemeris/status")

    assert response.status_code == 200
    data = response.json()
    assert "ephe_dir" in data
    assert "files" in data
    assert isinstance(data["files"], list)


def test_chart_endpoint_returns_chart_metadata(client):
    payload = {
        "data": {
            "name": "Ada Lovelace",
            "year": 1815,
            "month": 12,
            "day": 10,
            "hour": 0,
            "minute": 0,
            "lat": 51.5074,
            "lng": -0.1278,
            "tz_str": "UTC",
            "city": "London",
            "nation": "UK",
            "zodiac_type": "Tropical",
            "houses_system": "P",
        },
        "data2": {
            "zodiac_type": "Tropical",
            "houses_system": "P",
            "aspects_enabled": {},
        },
    }

    response = client.post("/chart", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ada Lovelace"
    assert data["location"]["city"] if "city" in data["location"] else True
    assert data["svg_path"].startswith("/charts_output/")
    assert "planets" in data
    assert "houses" in data
