import os
import uvicorn
import json
import re

from pathlib import Path
from typing import Any, Optional
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field, ValidationError, field_validator

from kerykeion import AstrologicalSubjectFactory
from kerykeion.charts.chart_drawer import ChartDrawer
from kerykeion import ChartDataFactory
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_ASPECTS

app = FastAPI(title="Astrology API")

ZODIAC_TYPES = ("Tropical", "Sidereal")
HOUSE_SYSTEM_OPTIONS = {
    "A": "Equal",
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
    return str(aspect.get("name", "")).strip()


SUPPORTED_ASPECTS = tuple(
    _aspect_name(aspect) for aspect in DEFAULT_ACTIVE_ASPECTS if _aspect_name(aspect)
)
DEFAULT_ASPECTS_ENABLED = {name: False for name in SUPPORTED_ASPECTS}


def _normalize_aspects_enabled(value: Any) -> dict[str, bool]:
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


def _get_preferences_path() -> Path:
    configured_path = os.getenv("ASTROLOGY_APP_PREFERENCES_PATH")
    if configured_path:
        return Path(configured_path).expanduser().resolve()

    if sys.platform == "win32":
        base_dir = Path(os.getenv("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        base_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base_dir / "simple-astro-chart" / "preferences.json"


# ====================== DIRECTORY SETUP ======================
print("[Backend] Forcing DEVELOPMENT mode")
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "../frontend/public"

DATA_DIR.mkdir(parents=True, exist_ok=True)

STATIC_CHART_DIR = DATA_DIR / "charts_output"
STATIC_CHART_DIR.mkdir(parents=True, exist_ok=True)

print(f"[Backend] Using data dir: {DATA_DIR}")
print(f"[Backend] Charts dir: {STATIC_CHART_DIR}")

# Serve SVG charts
app.mount(
    "/charts_output", StaticFiles(directory=STATIC_CHART_DIR), name="charts_output"
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="127.0.0.1", port=port)


# CORS for Vue dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BirthData(BaseModel):
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
    data: BirthData
    data2: Optional[Preferences] = None


def _save_preferences(preferences: Preferences) -> None:
    path = _get_preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = preferences.model_dump()
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)


def _load_preferences() -> Preferences:
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
    active_names = {
        name for name, is_enabled in preferences.aspects_enabled.items() if is_enabled
    }
    return [
        aspect
        for aspect in DEFAULT_ACTIVE_ASPECTS
        if _aspect_name(aspect) in active_names
    ]


def _strip_aspect_matrix_from_svg(svg_markup: str) -> str:
    # Keep the full chart layout and metadata tables, but remove only aspect sections.
    patterns = [
        r"<g\s+kr:node='Aspect_Grid'.*?</g>",
        r"<g\s+kr:node='Aspect_List'.*?</g>",
    ]

    cleaned = svg_markup
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL)

    return cleaned


@app.get("/preferences")
async def get_preferences():
    return _load_preferences().model_dump()


@app.put("/preferences")
async def update_preferences(preferences: Preferences):
    _save_preferences(preferences)
    return preferences.model_dump()


@app.get("/preferences/options")
async def get_preferences_options():
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


@app.post("/chart")
async def generate_chart(payload: ChartRequest):
    try:
        data = payload.data
        data2 = payload.data2 or _load_preferences()

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
            f"[Backend] Generating chart for: {subject.name} ({data.year}-{data.month}-{data.day} {data.hour}:{data.minute})"
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

            # Always render the full chart so other right-side panels are preserved.
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


# @app.get("/debug/{name}")
# async def debug_subject(name: str):
#     subject = AstrologicalSubjectFactory.from_birth_data(
#         name=name,
#         year=1990,
#         month=7,
#         day=15,
#         hour=10,
#         minute=30,
#         lat=41.9,
#         lng=12.5,
#         tz_str="Europe/Rome",
#         online=False,
#     )
#     attrs = [attr for attr in dir(subject) if not attr.startswith("_")]
#     return {"available_attributes": attrs}


@app.get("/debug/charts")
async def debug_charts():
    files = [f.name for f in STATIC_CHART_DIR.glob("*.svg")]
    return {
        "static_dir": str(STATIC_CHART_DIR),
        "files": files,
        "exists": STATIC_CHART_DIR.exists(),
    }
