from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kerykeion import AstrologicalSubjectFactory
from kerykeion.charts.chart_drawer import ChartDrawer  # For SVG if needed
from kerykeion import ChartDataFactory
from datetime import datetime
import json

app = FastAPI(title="Astrology API")

# CORS for Vue dev server (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BirthData(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    lat: float
    lng: float
    tz_str: str  # e.g., "Europe/Rome", "America/New_York"
    houses_system: str = "P"  # P = Placidus (default)


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
            tz_str=data.tz_str,
            online=False,
            houses_system_identifier=data.houses_system,
        )

        # Generate full chart data (includes aspects, etc.)
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

        # Houses (all 12)
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
            "aspects": (
                chart_data.aspects if hasattr(chart_data, "aspects") else []
            ),  # Main addition
            # Add more from chart_data as needed (e.g. chart_data.dignities, etc.)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/debug/{name}")
async def debug_subject(name: str):
    # Example birth data for debugging
    subject = AstrologicalSubjectFactory.from_birth_data(
        name=name,
        year=1990,
        month=7,
        day=15,
        hour=10,
        minute=30,
        lat=41.9,
        lng=12.5,
        tz_str="Europe/Rome",
        online=False,
    )
    attrs = [attr for attr in dir(subject) if not attr.startswith("_")]
    return {"available_attributes": attrs}
