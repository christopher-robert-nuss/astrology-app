from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import backend.main as backend_main
from backend.main import app


@pytest.fixture(autouse=True)
def restore_kerykeion_ephemeris_context():
    """Keep Kerykeion's ephemeris_context pristine between tests."""
    original = backend_main._kerykeion_ephemeris_context
    yield
    backend_main._kerykeion_subject_factory.ephemeris_context = original


@pytest.fixture
def client(tmp_path, monkeypatch):
    preferences_path = tmp_path / "preferences.json"
    ephe_dir = tmp_path / "ephe"
    monkeypatch.setenv("ASTROLOGY_APP_PREFERENCES_PATH", str(preferences_path))
    monkeypatch.setenv("ASTROLOGY_APP_EPHE_DIR", str(ephe_dir))
    monkeypatch.setenv("ASTROLOGY_APP_DATA_DIR", str(tmp_path / "frontend-public"))
    with TestClient(app) as test_client:
        yield test_client


def test_empty_appdata_does_not_resolve_ephe_relative_to_cwd(monkeypatch, tmp_path):
    monkeypatch.delenv("ASTROLOGY_APP_EPHE_DIR", raising=False)
    monkeypatch.delenv("ASTROLOGY_APP_DATA_ROOT", raising=False)
    monkeypatch.setattr(backend_main.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", "")
    monkeypatch.setattr(backend_main.Path, "home", staticmethod(lambda: tmp_path))

    ephe_dir = backend_main._get_ephemeris_dir()

    assert ephe_dir == tmp_path / "AppData" / "Roaming" / "simple-astrology-app" / "ephe"
    assert Path.cwd() not in ephe_dir.parents
    assert ephe_dir != Path.cwd() / "simple-astrology-app" / "ephe"


def test_ensure_ephemeris_points_kerykeion_at_app_ephe_dir(tmp_path, monkeypatch):
    ephe_dir = tmp_path / "ephe"
    monkeypatch.setenv("ASTROLOGY_APP_EPHE_DIR", str(ephe_dir))
    monkeypatch.setattr(
        backend_main,
        "_ensure_ephe_file_available",
        lambda filename, dest_dir: True,
    )

    result = backend_main.ensure_ephemeris_for_year(1972)

    assert result == ephe_dir.resolve()
    patched = backend_main._kerykeion_subject_factory.ephemeris_context
    assert getattr(patched, "_astrology_app_patched", False) is True
    expected_path = backend_main._swisseph_search_path(ephe_dir)
    assert patched._astrology_app_ephe_dir == expected_path
    assert backend_main._swisseph_path_str(ephe_dir) in patched._astrology_app_ephe_dir.split(
        ";" if backend_main.sys.platform == "win32" else ":"
    )


def test_swisseph_path_str_uses_forward_slashes(tmp_path):
    path = backend_main._swisseph_path_str(tmp_path / "ephe")
    assert "\\" not in path
    assert path.endswith("ephe")


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


def test_timezone_endpoint_resolves_iana_zone_from_coordinates(client):
    london = client.get("/timezone", params={"lat": 51.5074, "lng": -0.1278})
    assert london.status_code == 200
    assert london.json()["tz_str"] == "Europe/London"

    village = client.get("/timezone", params={"lat": 48.05, "lng": 11.55})
    assert village.status_code == 200
    assert village.json()["tz_str"] == "Europe/Berlin"


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
            "tz_str": "",
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
    assert data["location"]["tz"] == "Europe/London"
    assert data["location"]["city"] if "city" in data["location"] else True
    assert data["svg_path"].startswith("/charts_output/")
    assert data["print_svg_path"].startswith("/charts_output/")
    assert data["print_svg_path"].endswith("-print.svg")
    assert "planets" in data
    assert "houses" in data
    assert isinstance(data["aspects"], list)
    if data["aspects"]:
        assert "p1" in data["aspects"][0]
        assert "aspect" in data["aspects"][0]


def test_editorial_svg_palette_uses_readable_structure_colors():
    sample = """
    :root {
      --kerykeion-color-base-100: #0f172a;
      --kerykeion-color-primary: #38bdf8;
      --kerykeion-color-primary-content: #000000;
      --kerykeion-modern-stroke: #384a6b;
      --kerykeion-modern-indicator: #4e607d;
      --kerykeion-chart-color-houses-radix-line: var(--kerykeion-color-base-content);
    }
    <rect fill="#ffffff"/>
    <circle stroke="#6f5a3b"/>
    """

    rewritten = backend_main._apply_editorial_svg_palette(sample)

    assert "--kerykeion-color-base-100: #222625" in rewritten
    assert "--kerykeion-color-primary: #c9a467" in rewritten
    assert "--kerykeion-modern-stroke: #c9a467" in rewritten
    assert "--kerykeion-modern-indicator: #b08a4a" in rewritten
    assert "--kerykeion-chart-color-houses-radix-line: #b08a4a" in rewritten
    assert "--kerykeion-color-primary-content: #c9a467" not in rewritten
    assert 'fill="#222625"' in rewritten
    assert "#6f5a3b" not in rewritten
    assert "#38bdf8" not in rewritten


def test_ephemeris_ensure_exposes_download_error(client, monkeypatch):
    def fail_download(*args, **kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(backend_main, "ensure_ephemeris_for_year", fail_download)

    response = client.post("/ephemeris/ensure?year=1972")

    assert response.status_code == 400
    assert response.json()["detail"] == "network unavailable"
