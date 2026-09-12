"""
Astrology Backend – FastAPI + Kerykeion

Computes natal charts offline using Swiss Ephemeris data that is
downloaded on demand into the user's data directory.
"""

import os
import re
import ssl
import shutil
import sys
import json
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

import certifi
import swisseph as swe
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError, field_validator

from kerykeion import AstrologicalSubjectFactory, ChartDataFactory
from kerykeion.astrological_subject_factory import ephemeris_context as _kerykeion_ephemeris_context
from kerykeion.charts.chart_drawer import ChartDrawer
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_ASPECTS
from timezonefinder import TimezoneFinder
import kerykeion.astrological_subject_factory as _kerykeion_subject_factory

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


def _env_path(name: str) -> Optional[Path]:
    """Return an expanded path from an environment variable, or None if unset/blank."""
    configured = os.getenv(name)
    if not configured or not configured.strip():
        return None
    return Path(configured).expanduser().resolve()


def _get_app_data_root() -> Path:
    """
    Return the platform-specific root directory for app user data.

    Override with the ASTROLOGY_APP_DATA_ROOT environment variable.
    """
    configured = _env_path("ASTROLOGY_APP_DATA_ROOT")
    if configured is not None:
        return configured

    if sys.platform == "win32":
        # Prefer APPDATA, but ignore empty values so we never fall back to cwd
        # under a non-writable install directory (common for packaged Windows apps).
        appdata = os.getenv("APPDATA")
        base_dir = Path(appdata) if appdata and appdata.strip() else Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        xdg = os.getenv("XDG_CONFIG_HOME")
        base_dir = Path(xdg) if xdg and xdg.strip() else Path.home() / ".config"

    return base_dir / "simple-astrology-app"


def _get_preferences_path() -> Path:
    """
    Return the path to the preferences JSON file.

    Override with the ASTROLOGY_APP_PREFERENCES_PATH environment variable.
    """
    configured_path = _env_path("ASTROLOGY_APP_PREFERENCES_PATH")
    if configured_path is not None:
        return configured_path
    return _get_app_data_root() / "preferences.json"


def _get_ephemeris_dir() -> Path:
    """
    Return the persistent directory for Swiss Ephemeris .se1 files.

    Override with the ASTROLOGY_APP_EPHE_DIR environment variable.
    """
    configured = _env_path("ASTROLOGY_APP_EPHE_DIR")
    if configured is not None:
        return configured
    return _get_app_data_root() / "ephe"


def _get_data_dir() -> Path:
    """
    Return the directory used for chart SVG output.

    Override with the ASTROLOGY_APP_DATA_DIR environment variable.
    Defaults to ../frontend/public relative to this file.
    """
    configured_path = _env_path("ASTROLOGY_APP_DATA_DIR")
    if configured_path is not None:
        return configured_path
    return (Path(__file__).resolve().parent / "../frontend/public").resolve()


def _swisseph_path_str(ephe_dir: Path) -> str:
    """Format an ephemeris directory for pyswisseph (forward slashes work on Windows)."""
    return str(ephe_dir.resolve()).replace("\\", "/")


def _swisseph_search_path(ephe_dir: Path) -> str:
    """
    Build the Swiss Ephemeris search path.

    Prefer the app's persistent download directory, and append Kerykeion's
    bundled sweph/ when present so support files like sefstars.txt remain
    available without re-downloading them.
    """
    paths = [_swisseph_path_str(ephe_dir)]
    try:
        import kerykeion
    except ImportError:
        kerykeion = None
    if kerykeion is not None:
        kery_sweph = Path(kerykeion.__file__).resolve().parent / "sweph"
        if kery_sweph.is_dir():
            kery_path = _swisseph_path_str(kery_sweph)
            if kery_path not in paths:
                paths.append(kery_path)

    separator = ";" if sys.platform == "win32" else ":"
    return separator.join(paths)


def _certifi_ca_path() -> str:
    """Return a CA bundle path that works in source runs and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            bundled = Path(meipass) / "certifi" / "cacert.pem"
            if bundled.is_file():
                return str(bundled)
    return certifi.where()


def _point_kerykeion_at_ephe_dir(ephe_dir: Path) -> None:
    """
    Make Kerykeion use our persistent ephemeris directory.

    AstrologicalSubjectFactory hardcodes Path(__file__)/sweph, which only ships
    a few support files and is unreliable in frozen Windows builds. Redirect its
    ephemeris_context to the directory we download into.
    """
    path_str = _swisseph_search_path(ephe_dir)
    existing = _kerykeion_subject_factory.ephemeris_context
    if getattr(existing, "_astrology_app_patched", False):
        existing._astrology_app_ephe_dir = path_str
        return

    original = _kerykeion_ephemeris_context

    @contextmanager
    def _patched_ephemeris_context(ephe_path: str, *args, **kwargs):
        del ephe_path  # ignore Kerykeion's bundled sweph path
        with original(_patched_ephemeris_context._astrology_app_ephe_dir, *args, **kwargs) as iflag:
            yield iflag

    _patched_ephemeris_context._astrology_app_patched = True
    _patched_ephemeris_context._astrology_app_ephe_dir = path_str
    _kerykeion_subject_factory.ephemeris_context = _patched_ephemeris_context


# ---------------------------------------------------------------------------
# Swiss Ephemeris data management
# ---------------------------------------------------------------------------
# The full ephemeris set is no longer bundled with the app.
# Required .se1 files are downloaded on first use for a given 600-year block
# and stored permanently under the user data directory:
#   <app-data-root>/ephe/
# Kerykeion is redirected to this directory (it otherwise hardcodes its own
# incomplete sweph/ package path).
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


def _required_ephe_files(year: int, include_asteroids: bool = True) -> List[str]:
    """Return the list of .se1 filenames needed for a birth year.

    Asteroid files are included by default because Kerykeion's default active
    points include Chiron, which reads seas_*.se1.
    """
    prefix = _year_to_ephe_prefix(year)
    files = [
        f"sepl_{prefix}.se1",
        f"semo_{prefix}.se1",
    ]
    if include_asteroids:
        files.append(f"seas_{prefix}.se1")
    return files


def _get_bundled_ephe_dir() -> Optional[Path]:
    """Return a local bundled ephemeris directory if present (dev tree or next to the exe)."""
    candidates = [
        (Path(__file__).resolve().parent / "../ephe").resolve(),
    ]
    if getattr(sys, "frozen", False):
        candidates.insert(0, Path(sys.executable).resolve().parent / "ephe")
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "ephe")

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _local_ephe_source_dirs() -> List[Path]:
    """Directories that may already contain ephemeris files (dev tree or Kerykeion)."""
    sources: List[Path] = []
    bundled_dir = _get_bundled_ephe_dir()
    if bundled_dir is not None:
        sources.append(bundled_dir)

    try:
        import kerykeion
    except ImportError:
        return sources

    kery_sweph = Path(kerykeion.__file__).resolve().parent / "sweph"
    if kery_sweph.is_dir() and kery_sweph not in sources:
        sources.append(kery_sweph)
    return sources


def _ensure_ephe_file_available(filename: str, dest_dir: Path) -> bool:
    """Make sure a required ephemeris file exists locally, using bundled data first."""
    dest = dest_dir / filename
    if dest.exists() and dest.stat().st_size > 10_000:
        return True

    for source_dir in _local_ephe_source_dirs():
        source_file = source_dir / filename
        if source_file.exists() and source_file.stat().st_size > 10_000:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest)
            print(f"[Ephemeris] Copied {filename} from {source_dir}")
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
    ssl_context = ssl.create_default_context(cafile=_certifi_ca_path())

    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(
                request,
                timeout=30,
                context=ssl_context,
            ) as response:
                data = response.read()
            if len(data) < 10_000:
                raise RuntimeError(
                    f"Downloaded {filename} is too small ({len(data)} bytes)"
                )
            tmp.write_bytes(data)
            os.replace(tmp, dest)
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


def ensure_ephemeris_for_year(year: int, include_asteroids: bool = True) -> Path:
    """
    Ensure the required Swiss Ephemeris files for `year` exist locally,
    then point pyswisseph and Kerykeion at that directory.

    Returns the ephemeris directory that was used.
    """
    with _ephe_lock:
        ephe_dir = _get_ephemeris_dir()
        ephe_dir.mkdir(parents=True, exist_ok=True)
        required = _required_ephe_files(year, include_asteroids=include_asteroids)

        for fname in required:
            if not _ensure_ephe_file_available(fname, ephe_dir):
                _download_ephe_file(fname, ephe_dir)

        path_str = _swisseph_search_path(ephe_dir)
        swe.set_ephe_path(path_str)
        _point_kerykeion_at_ephe_dir(ephe_dir)
        print(f"[Ephemeris] Using path: {path_str}")
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


_timezone_finder: Optional[TimezoneFinder] = None
_IANA_TIMEZONES = available_timezones()


def _get_timezone_finder() -> TimezoneFinder:
    global _timezone_finder
    if _timezone_finder is None:
        _timezone_finder = TimezoneFinder()
    return _timezone_finder


def _timezone_from_coordinates(lat: float, lng: float) -> str:
    found = _get_timezone_finder().timezone_at(lat=lat, lng=lng)
    return found or "UTC"


def _is_valid_iana_timezone(name: str) -> bool:
    if name == "UTC":
        return True
    if name not in _IANA_TIMEZONES:
        return False
    try:
        ZoneInfo(name)
        return True
    except ZoneInfoNotFoundError:
        return False


def resolve_timezone(lat: float, lng: float, tz_str: Optional[str] = None) -> str:
    """Prefer an explicit IANA zone; otherwise derive it from coordinates."""
    requested = (tz_str or "").strip()
    if requested and requested.lower() != "auto":
        if not _is_valid_iana_timezone(requested):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unknown timezone '{requested}'. "
                    "Use an IANA name such as Europe/Berlin, or leave it blank to "
                    "resolve from latitude and longitude."
                ),
            )
        return requested
    return _timezone_from_coordinates(lat, lng)


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
    tz_str: Optional[str] = None
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


# Editorial chart tokens. Rings and glyphs must keep ≥3:1 (UI) / ≥4.5:1 (text)
# against paper (#222625). Do not use #6f5a3b for structure — it fails both.
_EDITORIAL_CHART_CSS_VARS = {
    "--kerykeion-color-black": "#17191a",
    "--kerykeion-color-white": "#f4eee4",
    "--kerykeion-color-neutral-content": "#bdb4a7",
    "--kerykeion-color-base-content": "#f4eee4",
    "--kerykeion-color-primary": "#c9a467",
    "--kerykeion-color-secondary": "#bdb4a7",
    "--kerykeion-color-accent": "#9aa390",
    "--kerykeion-color-neutral": "#5c625e",
    "--kerykeion-color-base-100": "#222625",
    "--kerykeion-color-base-200": "#17191a",
    "--kerykeion-color-base-300": "#2b302d",
    "--kerykeion-color-info": "#9aa390",
    "--kerykeion-color-info-content": "#17191a",
    "--kerykeion-color-success": "#9aa390",
    "--kerykeion-color-warning": "#e0be7b",
    "--kerykeion-color-error": "#d08968",
    "--kerykeion-modern-planet-ring": "#17191a",
    "--kerykeion-modern-planet-ring-outer": "#17191a",
    "--kerykeion-modern-house-ring": "#2b302d",
    "--kerykeion-modern-stroke": "#c9a467",
    "--kerykeion-modern-retrograde": "#d08968",
    "--kerykeion-modern-indicator": "#b08a4a",
    "--kerykeion-chart-color-paper-0": "#f4eee4",
    "--kerykeion-chart-color-paper-1": "#222625",
    "--kerykeion-chart-color-zodiac-radix-ring-0": "#c9a467",
    "--kerykeion-chart-color-zodiac-radix-ring-1": "#e0be7b",
    "--kerykeion-chart-color-zodiac-radix-ring-2": "#b08a4a",
    "--kerykeion-chart-color-houses-radix-line": "#b08a4a",
}

_EDITORIAL_CHART_CSS_VARS.update(
    {
        f"--kerykeion-modern-zodiac-bg-{index}": (
            "#17191a" if index % 2 == 0 else "#2b302d"
        )
        for index in range(12)
    }
)
_EDITORIAL_CHART_CSS_VARS.update(
    {
        f"--kerykeion-chart-color-zodiac-bg-{index}": (
            "#17191a" if index % 2 == 0 else "#2b302d"
        )
        for index in range(12)
    }
)

_EDITORIAL_CHART_HEX_FALLBACK = {
    "#ffffff": "#222625",
    "#FFFFFF": "#222625",
    "#000000": "#f4eee4",
    "#000000ff": "#f4eee4",
    "#0f172a": "#222625",
    "#1d1b22": "#222625",
    "#302b2b": "#17191a",
    "#6f5a3b": "#b08a4a",
    "#8f7650": "#e0be7b",
    "#4f5f99": "#c9a467",
    "#7f8fc6": "#e0be7b",
    "#9eabd8": "#b08a4a",
    "#8d9cd2": "#b08a4a",
    "#dbe2ff": "#17191a",
    "#7c8ac1": "#c9a467",
    "#49547e": "#f4eee4",
    "#38bdf8": "#c9a467",
    "#818cf8": "#bdb4a7",
    "#f471b5": "#9aa390",
    "#fb7085": "#d08968",
    "#2dd4bf": "#9aa390",
    "#f4bf50": "#e0be7b",
}


def _apply_editorial_svg_palette(svg_markup: str) -> str:
    """Retint a Kerykeion SVG to the app's dark editorial palette."""
    rewritten = svg_markup
    for name, value in _EDITORIAL_CHART_CSS_VARS.items():
        rewritten = re.sub(
            rf"({re.escape(name)})(?![\w-])(\s*:\s*)[^;]+",
            rf"\g<1>\g<2>{value}",
            rewritten,
            flags=re.IGNORECASE,
        )
    hex_fallback = {key.lower(): value for key, value in _EDITORIAL_CHART_HEX_FALLBACK.items()}
    return re.sub(
        r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?",
        lambda match: hex_fallback.get(match.group(0).lower(), match.group(0)),
        rewritten,
    )


def _serialize_aspects(chart_data: Any) -> list[dict[str, Any]]:
    """Turn Kerykeion aspect models into JSON-safe rows for the UI."""
    raw = getattr(chart_data, "aspects", None)
    if raw is None:
        aspects = []
    elif hasattr(raw, "aspects"):
        aspects = raw.aspects or []
    else:
        aspects = raw or []
    rows: list[dict[str, Any]] = []
    for aspect in aspects:
        if hasattr(aspect, "model_dump"):
            data = aspect.model_dump()
        elif isinstance(aspect, dict):
            data = aspect
        else:
            continue
        rows.append(
            {
                "p1": data.get("p1_name"),
                "p2": data.get("p2_name"),
                "aspect": data.get("aspect"),
                "orbit": data.get("orbit"),
                "movement": data.get("aspect_movement"),
            }
        )
    return rows


def _write_chart_svg(
    chart_data: Any,
    output_dir: Path,
    filename: str,
    *,
    theme: str,
    editorial: bool,
    strip_matrix: bool,
) -> Optional[Path]:
    """Render a natal SVG, optionally retinted for the on-screen palette."""
    drawer = ChartDrawer(chart_data=chart_data, theme=theme)
    svg_path = output_dir / f"{filename}.svg"
    if svg_path.exists():
        svg_path.unlink()
    drawer.save_svg(output_path=str(output_dir), filename=filename)
    if not svg_path.exists():
        return None
    markup = svg_path.read_text(encoding="utf-8")
    if strip_matrix:
        markup = _strip_aspect_matrix_from_svg(markup)
    if editorial:
        markup = _apply_editorial_svg_palette(markup)
    svg_path.write_text(markup, encoding="utf-8")
    return svg_path


# ---------------------------------------------------------------------------
# API routes – Preferences
# ---------------------------------------------------------------------------


@app.get("/timezone")
async def get_timezone(lat: float, lng: float):
    """Return the IANA timezone for a latitude/longitude pair."""
    if lat < -90 or lat > 90 or lng < -180 or lng > 180:
        raise HTTPException(status_code=400, detail="Latitude or longitude is out of range.")
    tz_str = _timezone_from_coordinates(lat, lng)
    return {
        "tz_str": tz_str,
        "source": "coordinates" if tz_str != "UTC" else "fallback",
        "lat": lat,
        "lng": lng,
    }


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

        tz_str = resolve_timezone(data.lat, data.lng, data.tz_str)

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
            tz_str=tz_str,
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

        filename = f"{data.name.replace(' ', '-')}-chart"
        print_filename = f"{filename}-print"
        svg_full_path = f"/charts_output/{filename}.svg"
        print_svg_path: Optional[str] = f"/charts_output/{print_filename}.svg"
        strip_matrix = not aspect_list

        try:
            STATIC_CHART_DIR.mkdir(parents=True, exist_ok=True)
            screen_path = _write_chart_svg(
                chart_data,
                STATIC_CHART_DIR,
                filename,
                theme="dark-high-contrast",
                editorial=True,
                strip_matrix=strip_matrix,
            )
            print_path = _write_chart_svg(
                chart_data,
                STATIC_CHART_DIR,
                print_filename,
                theme="classic",
                editorial=False,
                strip_matrix=strip_matrix,
            )
            if screen_path is None:
                raise Exception("SVG file was not created")
            if print_path is None:
                print_svg_path = None
        except Exception as svg_err:
            print(f"SVG save failed: {svg_err}")
            svg_full_path = None
            print_svg_path = None

        return {
            "name": subject.name,
            "date": f"{data.year}-{data.month:02d}-{data.day:02d} {data.hour:02d}:{data.minute:02d}",
            "location": {
                "lat": data.lat,
                "lng": data.lng,
                "tz": tz_str,
                "city": data.city,
                "nation": data.nation,
            },
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
            "aspects": _serialize_aspects(chart_data),
            "preferences": data2.model_dump(),
            "svg_path": svg_full_path,
            "print_svg_path": print_svg_path,
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
async def ephemeris_ensure(year: int, include_asteroids: bool = True):
    """
    Ensure the required ephemeris files for a given year are present.

    Asteroid files are included by default (needed for Chiron). Useful for
    pre-downloading or testing.
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
