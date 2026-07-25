import os
import uvicorn
import json
from pathlib import Path
from typing import Optional
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from pydantic import BaseModel, field_validator, ValidationError

from kerykeion import AstrologicalSubjectFactory
from kerykeion.charts.chart_drawer import ChartDrawer
from kerykeion import ChartDataFactory

app = FastAPI(title="Astrology API")

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


@app.post("/chart")
async def generate_chart(data: BirthData):
    try:
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
            houses_system_identifier=data.houses_system,
        )

        chart_data = ChartDataFactory.create_natal_chart_data(subject)

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

            if not svg_path.exists():
                raise Exception("SVG file was not created")
        except Exception as svg_err:
            print(f"SVG save failed: {svg_err}")
            svg_full_path = None

        return {
            "name": subject.name,
            "date": f"{data.year}-{data.month:02d}-{data.day:02d} {data.hour:02d}:{data.minute:02d}",
            "location": {"lat": data.lat, "lng": data.lng, "tz": data.tz_str},
            "houses_system": getattr(subject, "houses_system_name", data.houses_system),
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
            "svg_path": f"/charts_output/{filename}.svg",
        }

    except Exception as e:
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
