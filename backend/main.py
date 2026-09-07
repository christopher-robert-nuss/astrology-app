"""
Astrology Backend – FastAPI + Kerykeion

Computes natal charts offline using Swiss Ephemeris data that is
downloaded on demand into the user's data directory.
"""

import os
import re
import shutil
import sys
import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, List, Optional

import swisseph as swe
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError, field_validator

from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_ASPECTS

# ---------------------------------------------------------------------------
# Application & constants
# ---------------------------------------------------------------------------

app = FastAPI(title="Astrology API")
_ephe_lock = threading.Lock()

ZODIAC_TYPES = ("Tropical", "Sidereal")

HOUSE_SYSTEM_OPTIONS = {
    "A": "equal",
    "B": "Alcabitius",
    "C": "Campanus",
    "D": "Porphyry",
    "F": "Carter Poli-Equatorial",
    "H": "Horizontal",
    "I": "Sunshine",
    "i": "Sunshine Alternative",
    "K": "Koch",
    "L": "Pullen SD",
    "M": "Morinus",
    "N": "Whole Sign",
    "O": "Porphyry",
    "P": "Placidus",
    "Q": "Pullen SR",
    "R": "Regiomontanus",
    "S": "Sripati",
    "T": "Polich-Page",
    "U": "Krusinski-Pisa",
    "V": "Vehlow",
    "W": "Whole Sign",
    "X": "Axial Rotation",
    "Y": "APC",
}


def _aspect_name(aspect: dict[str, Any]) -> str:
    """Extract the aspect name from a DEFAULT_ACTIVE_ASPECTS entry."""
    return str(aspect.get("name", "")).strip()


SUPPORTED_ASPECTS = tuple(
    _aspect_name(aspect) for aspect in DEFAULT_ACTIVE_ASPECTS if _aspect_name(aspect)
)
DEFAULT_ASPECTS_ENABLED = {name: False for name in SUPPORTED_ASPECTS}


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def _get_app_data_root() -> Path:
    """
    Return the platform-specific root directory for app user data.

    Override with the ASTROLOGY_APP_DATA_ROOT environment variable.
    """
    configured = os.getenv("ASTROLOGY_APP_DATA_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()

    if sys.platform == "win32":
        base_dir = Path(os.getenv("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        base_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base_dir / "simple-astrology-app"


def _get_preferences_path() -> Path:
    """
    Return the path to the preferences JSON file.

    Override with the ASTROLOGY_APP_PREFERENCES_PATH environment variable.
    """
    configured_path = os.getenv("ASTROLOGY_APP_PREFERENCES_PATH")
    if configured_path:
        return Path(configured_path).expanduser().resolve()
    return _get_app_data_root() / "preferences.json"


def _get_ephemeris_dir() -> Path:
    """
    Return the persistent directory for Swiss Ephemeris .se1 files.

    Override with the ASTROLOGY_APP_EPHE_DIR environment variable.
    """
    configured = os.getenv("ASTROLOGY_APP_EPHE_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return _get_app_data_root() / "ephe"


def _get_data_dir() -> Path:
    """
    Return the directory used for chart SVG output.

    Override with the ASTROLOGY_APP_DATA_DIR environment variable.
    Defaults to ../frontend/public relative to this file.
    """
    configured_path = os.getenv("ASTROLOGY_APP_DATA_DIR")
    if configured_path:
        return Path(configured_path).expanduser().resolve()
    return (Path(__file__).resolve().parent / "../frontend/public").resolve()


# ---------------------------------------------------------------------------
# Swiss Ephemeris data management
# ---------------------------------------------------------------------------
# The full ephemeris set is no longer bundled with the app.
# Required .se1 files are downloaded on first use for a given 600-year block
# and stored permanently under the user data directory:
#   <app-data-root>/ephe/
# Kerykeion is pointed at this directory via swe.set_ephe_path().
# ---------------------------------------------------------------------------


def _year_to_ephe_prefix(year: int) -> str:
    """
    Map a year to the Swiss Ephemeris 600-year block prefix.

    Supported practical range: roughly 5400 BC – 5399 AD.
    Examples:
        1990 → "18"
        1750 → "12"
        -300 → "m06"
    """
    if year < -5400 or year > 5399:
        raise ValueError(
            f"Year {year} is outside the supported Swiss Ephemeris range "
            "(approx. 5400 BC – 5399 AD)"
        )

    if year >= 0:
        block_start = (year // 600) * 600
        return f"{block_start // 100:02d}"

    abs_year = abs(year)
    block_start = ((abs_year - 1) // 600) * 600 + 600
    return f"m{block_start // 100:02d}"


def _required_ephe_files(year: int, include_asteroids: bool = False) -> List[str]:
    """Return the list of .se1 filenames needed for a birth year."""
    prefix = _year_to_ephe_prefix(year)
    files = [
        f"sepl_{prefix}.se1",
        f"semo_{prefix}.se1",
    ]
    if include_asteroids:
        files.append(f"seas_{prefix}.se1")
    return files


def _get_bundled_ephe_dir() -> Optional[Path]:
    """Return the repository's bundled ephemeris directory if present."""
    candidate = (Path(__file__).resolve().parent / "../ephe").resolve()
    return candidate if candidate.exists() else None


def _ensure_ephe_file_available(filename: str, dest_dir: Path) -> bool:
    """Make sure a required ephemeris file exists locally, using bundled data first."""
    dest = dest_dir / filename
    if dest.exists() and dest.stat().st_size > 10_000:
        return True

    bundled_dir = _get_bundled_ephe_dir()
    if bundled_dir is not None:
        bundled_file = bundled_dir / filename
        if bundled_file.exists() and bundled_file.stat().st_size > 10_000:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bundled_file, dest)
            print(f"[Ephemeris] Copied {filename} from bundled data")
            return True

    return False


def _download_ephe_file(filename: str, dest_dir: Path) -> None:
    """
    Download a single ephemeris file if it does not already exist.

    Uses the public GitHub mirror of the Swiss Ephemeris data files.
    """
    dest = dest_dir / filename
    if dest.exists() and dest.stat().st_size > 10_000:
        return

    url = f"https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/{filename}"
    print(f"[Ephemeris] Downloading {filename} …")

    dest_dir.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "simple-astrology-app/0.0.1"},
    )
    last_error = None

    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
            if len(data) < 10_000:
                raise RuntimeError(
                    f"Downloaded {filename} is too small ({len(data)} bytes)"
                )
            tmp.write_bytes(data)
            tmp.replace(dest)
            print(f"[Ephemeris] Saved {filename} ({len(data):,} bytes)")
            return
        except urllib.error.HTTPError as error:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(
                f"Ephemeris server returned HTTP {error.code} for {url}"
            ) from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            tmp.unlink(missing_ok=True)
            if attempt < 3:
                print(f"[Ephemeris] Download attempt {attempt} failed; retrying …")
                time.sleep(attempt)

    raise RuntimeError(
        f"Failed to download {filename} from {url} after 3 attempts: {last_error}"
    ) from last_error


def ensure_ephemeris_for_year(year: int, include_asteroids: bool = False) -> Path:
    """
    Ensure the required Swiss Ephemeris files for `year` exist locally,
    then point pyswisseph at that directory.

    Returns the ephemeris directory that was used.
    """
    with _ephe_lock:
        ephe_dir = _get_ephemeris_dir()
        required = _required_ephe_files(year, include_asteroids=include_asteroids)

        for fname in required:
            if not _ensure_ephe_file_available(fname, ephe_dir):
                _download_ephe_file(fname, ephe_dir)

        swe.set_ephe_path(str(ephe_dir))
        print(f"[Ephemeris] Using path: {ephe_dir}")
        return ephe_dir


# ---------------------------------------------------------------------------
# Directory setup & static file serving
# ---------------------------------------------------------------------------

DATA_DIR = _get_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)

STATIC_CHART_DIR = DATA_DIR / "charts_output"
STATIC_CHART_DIR.mkdir(parents=True, exist_ok=True)

print(f"[Backend] Using data dir: {DATA_DIR}")
print(f"[Backend] Charts dir: {STATIC_CHART_DIR}")
print(f"[Backend] Preferences: {_get_preferences_path()}")
print(f"[Backend] Ephemeris dir: {_get_ephemeris_dir()}")

app.mount(
    "/charts_output",
    StaticFiles(directory=STATIC_CHART_DIR),
    name="charts_output",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class BirthData(BaseModel):
    """Birth data supplied by the frontend form."""

    name: str
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    tz_str: str
    city: Optional[str] = None
    nation: Optional[str] = None
    zodiac_type: str = "Tropical"
    houses_system: str = "P"

    @field_validator("year", "month", "day", "hour", "minute", "lat", "lng")
    @classmethod
    def validate_numbers(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} is required")
        return v


class Preferences(BaseModel):
    """User preferences for zodiac type, house system and aspects."""

    zodiac_type: str = "Tropical"
    houses_system: str = "P"
    aspects_enabled: dict[str, bool] = Field(
        default_factory=lambda: dict(DEFAULT_ASPECTS_ENABLED)
    )

    @field_validator("zodiac_type")
    @classmethod
    def validate_zodiac_type(cls, value: str) -> str:
        if value not in ZODIAC_TYPES:
            raise ValueError(f"zodiac_type must be one of: {', '.join(ZODIAC_TYPES)}")
        return value

    @field_validator("houses_system")
    @classmethod
    def validate_house_system(cls, value: str) -> str:
        if value not in HOUSE_SYSTEM_OPTIONS:
            raise ValueError(
                f"houses_system must be one of: {', '.join(sorted(HOUSE_SYSTEM_OPTIONS.keys()))}"
            )
        return value

    @field_validator("aspects_enabled", mode="before")
    @classmethod
    def validate_aspects_enabled(cls, value: Any) -> dict[str, bool]:
        return _normalize_aspects_enabled(value)


class ChartRequest(BaseModel):
    """Request body for the /chart endpoint."""

    data: BirthData
    data2: Optional[Preferences] = None


# ---------------------------------------------------------------------------
# Preference helpers
# ---------------------------------------------------------------------------


def _normalize_aspects_enabled(value: Any) -> dict[str, bool]:
    """Normalise the aspects_enabled field to a full map of supported aspects."""
    if isinstance(value, bool):
        return {name: value for name in SUPPORTED_ASPECTS}

    if value is None:
        return dict(DEFAULT_ASPECTS_ENABLED)

    if not isinstance(value, dict):
        raise ValueError("aspects_enabled must be a boolean or an object map")

    unknown = [key for key in value if key not in SUPPORTED_ASPECTS]
    if unknown:
        raise ValueError(f"Unsupported aspects: {', '.join(sorted(unknown))}")

    normalized = dict(DEFAULT_ASPECTS_ENABLED)
    for key, enabled in value.items():
        if not isinstance(enabled, bool):
            raise ValueError(f"Aspect '{key}' must be true or false")
        normalized[key] = enabled

    return normalized


def _save_preferences(preferences: Preferences) -> None:
    """Write preferences to disk atomically."""
    path = _get_preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = preferences.model_dump()
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)


def _load_preferences() -> Preferences:
    """
    Load preferences from disk.

    Creates and returns defaults if the file is missing or invalid.
    """
    path = _get_preferences_path()

    if not path.exists():
        defaults = Preferences()
        _save_preferences(defaults)
        return defaults

    try:
        raw_data = json.loads(path.read_text(encoding="utf-8"))
        return Preferences.model_validate(raw_data)
    except (json.JSONDecodeError, ValidationError, OSError) as error:
        print(f"[Backend] Preferences file invalid, resetting to defaults: {error}")
        defaults = Preferences()
        _save_preferences(defaults)
        return defaults


def _get_active_aspects(preferences: Preferences) -> list[dict[str, Any]]:
    """Return the subset of DEFAULT_ACTIVE_ASPECTS that the user has enabled."""
    active_names = {
        name for name, is_enabled in preferences.aspects_enabled.items() if is_enabled
    }
    return [
        aspect
        for aspect in DEFAULT_ACTIVE_ASPECTS
        if _aspect_name(aspect) in active_names
    ]


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------


def _strip_aspect_matrix_from_svg(svg_markup: str) -> str:
    """
    Remove the aspect grid and aspect list groups from a rendered SVG
    while keeping the rest of the chart layout intact.
    """
    patterns = [
        r"<g\s+kr:node='Aspect_Grid'.*?</g>",
        r"<g\s+kr:node='Aspect_List'.*?</g>",
    ]

    cleaned = svg_markup
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL)
    return cleaned


# ---------------------------------------------------------------------------
# API routes – Preferences
# ---------------------------------------------------------------------------


@app.get("/preferences")
async def get_preferences():
    """Return the current user preferences."""
    return _load_preferences().model_dump()


@app.put("/preferences")
async def update_preferences(preferences: Preferences):
    """Update and persist user preferences."""
    _save_preferences(preferences)
    return preferences.model_dump()


@app.get("/preferences/options")
async def get_preferences_options():
    """Return the available zodiac types, house systems and aspects."""
    return {
        "zodiac_types": list(ZODIAC_TYPES),
        "house_systems": [
            {"code": code, "label": label}
            for code, label in HOUSE_SYSTEM_OPTIONS.items()
        ],
        "aspects": [
            {
                "key": _aspect_name(aspect),
                "label": _aspect_name(aspect).replace("_", " ").title(),
                "default_orb": aspect.get("orb"),
            }
            for aspect in DEFAULT_ACTIVE_ASPECTS
            if _aspect_name(aspect)
        ],
    }


# ---------------------------------------------------------------------------
# API routes – Chart generation
# ---------------------------------------------------------------------------


@app.post("/chart")
async def generate_chart(payload: ChartRequest):
    """
    Generate a natal chart for the supplied birth data.

    Downloads any missing Swiss Ephemeris files for the birth year,
    computes planetary and house positions, and renders an SVG chart.
    """
    try:
        data = payload.data
        data2 = payload.data2 or _load_preferences()

        if data.year is None:
            raise ValueError("year is required to select ephemeris files")

        try:
            ensure_ephemeris_for_year(data.year)
        except Exception as ephe_err:
            raise HTTPException(
                status_code=400,
                detail=f"Ephemeris data unavailable: {ephe_err}",
            ) from ephe_err

        subject = AstrologicalSubjectFactory.from_birth_data(
            name=data.name,
            year=data.year,
            month=data.month,
            day=data.day,
            hour=data.hour,
            minute=data.minute,
            lat=data.lat,
            lng=data.lng,
            tz_str=data.tz_str or "UTC",
            city=data.city,
            nation=data.nation,
            online=False,
            zodiac_type=data2.zodiac_type,
            houses_system_identifier=data2.houses_system,
        )

        print(
            f"[Backend] Generating chart for: {subject.name} "
            f"({data.year}-{data.month}-{data.day} {data.hour}:{data.minute})"
        )

        aspect_list = _get_active_aspects(data2)
        print(f"[Backend] Active aspects: {aspect_list}")

        chart_data = ChartDataFactory.create_natal_chart_data(
            subject, active_aspects=aspect_list
        )
        print(f"[Backend] Chart data generated successfully for {subject.name}")

        # Planets
        standard_planets = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
            "uranus",
            "neptune",
            "pluto",
        ]
        planets_data = {}
        for p_name in standard_planets:
            if hasattr(subject, p_name):
                p = getattr(subject, p_name)
                planets_data[p_name] = {
                    "name": getattr(p, "name", p_name.capitalize()),
                    "sign": getattr(p, "sign", None),
                    "sign_num": getattr(p, "sign_num", None),
                    "position": getattr(p, "position", None),
                    "abs_pos": getattr(p, "abs_pos", None),
                    "house": getattr(p, "house", None),
                    "retrograde": getattr(p, "retrograde", None),
                }

        # Houses
        houses_data = {}
        house_map = {
            1: "first_house",
            2: "second_house",
            3: "third_house",
            4: "fourth_house",
            5: "fifth_house",
            6: "sixth_house",
            7: "seventh_house",
            8: "eighth_house",
            9: "ninth_house",
            10: "tenth_house",
            11: "eleventh_house",
            12: "twelfth_house",
        }
        for i, attr in house_map.items():
            if hasattr(subject, attr):
                h = getattr(subject, attr)
                houses_data[f"house_{i}"] = {
                    "house": i,
                    "sign": getattr(h, "sign", None),
                    "sign_num": getattr(h, "sign_num", None),
                    "position": getattr(h, "position", None),
                    "abs_pos": getattr(h, "abs_pos", None),
                }

        chart_drawer = ChartDrawer(chart_data=chart_data)
        filename = f"{data.name.replace(' ', '-')}-chart"
        svg_full_path = f"/charts_output/{filename}.svg"

        try:
            STATIC_CHART_DIR.mkdir(parents=True, exist_ok=True)
            svg_path = STATIC_CHART_DIR / f"{filename}.svg"

            if svg_path.exists():
                svg_path.unlink()

            chart_drawer.save_svg(output_path=str(STATIC_CHART_DIR), filename=filename)

            if not aspect_list and svg_path.exists():
                svg_markup = svg_path.read_text(encoding="utf-8")
                svg_path.write_text(
                    _strip_aspect_matrix_from_svg(svg_markup),
                    encoding="utf-8",
                )

            if not svg_path.exists():
                raise Exception("SVG file was not created")
        except Exception as svg_err:
            print(f"SVG save failed: {svg_err}")
            svg_full_path = None

        return {
            "name": subject.name,
            "date": f"{data.year}-{data.month:02d}-{data.day:02d} {data.hour:02d}:{data.minute:02d}",
            "location": {"lat": data.lat, "lng": data.lng, "tz": data.tz_str},
            "zodiac_type": data2.zodiac_type,
            "houses_system": getattr(
                subject, "houses_system_name", data2.houses_system
            ),
            "planets": planets_data,
            "houses": houses_data,
            "ascendant": (
                getattr(subject.first_house, "sign", None)
                if hasattr(subject, "first_house")
                else None
            ),
            "mc": (
                getattr(subject.tenth_house, "sign", None)
                if hasattr(subject, "tenth_house")
                else None
            ),
            "aspects": getattr(chart_data, "aspects", []),
            "preferences": data2.model_dump(),
            "svg_path": f"/charts_output/{filename}.svg",
        }

    except Exception as e:
        print(f"[Backend] Error generating chart: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# API routes – Ephemeris management
# ---------------------------------------------------------------------------


@app.get("/ephemeris/status")
async def ephemeris_status():
    """Return the current ephemeris directory and the list of installed files."""
    ephe_dir = _get_ephemeris_dir()
    files = sorted(f.name for f in ephe_dir.glob("*.se1")) if ephe_dir.exists() else []
    return {
        "ephe_dir": str(ephe_dir),
        "exists": ephe_dir.exists(),
        "files": files,
        "note": "Files are downloaded on demand when a chart is generated.",
    }


@app.post("/ephemeris/ensure")
async def ephemeris_ensure(year: int, include_asteroids: bool = False):
    """
    Ensure the required ephemeris files for a given year are present.

    Useful for pre-downloading or testing.
    """
    try:
        path = ensure_ephemeris_for_year(year, include_asteroids=include_asteroids)
        files = sorted(f.name for f in path.glob("*.se1"))
        return {
            "ok": True,
            "year": year,
            "ephe_dir": str(path),
            "files": files,
            "required": _required_ephe_files(year, include_asteroids),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# ---------------------------------------------------------------------------
# API routes – Debug
# ---------------------------------------------------------------------------


@app.get("/debug/charts")
async def debug_charts():
    """List SVG files currently present in the charts output directory."""
    files = [f.name for f in STATIC_CHART_DIR.glob("*.svg")]
    return {
        "static_dir": str(STATIC_CHART_DIR),
        "files": files,
        "exists": STATIC_CHART_DIR.exists(),
    }


@app.get("/debug/ephe/{year}")
async def debug_ephe(year: int):
    """Ensure ephemeris data for a year and return the resulting file list."""
    path = ensure_ephemeris_for_year(year)
    files = list(path.glob("*.se1"))
    return {
        "ephe_dir": str(path),
        "files": [f.name for f in files],
        "required_for_year": _required_ephe_files(year),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="127.0.0.1", port=port)
