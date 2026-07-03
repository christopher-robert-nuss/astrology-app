from fileinput import filename

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kerykeion import AstrologicalSubjectFactory
from kerykeion.charts.chart_drawer import ChartDrawer  # For SVG if needed
from kerykeion import ChartDataFactory
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from typing import List, Optional
from pydantic import BaseModel, field_validator, ValidationError

app = FastAPI(title="Astrology API")

# Database setup - simple SQLite for standalone offline use
DB_PATH = Path("birth_charts.db")
DB_PATH.parent.mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            hour INTEGER,
            minute INTEGER,
            lat REAL,
            lng REAL,
            tz_str TEXT,
            city TEXT,
            nation TEXT,
            zodiac_type TEXT DEFAULT 'Tropical',
            houses_system TEXT DEFAULT 'P',
            chart_data TEXT,  -- JSON string of full chart
            svg_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()

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
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    tz_str: str  # e.g., "Europe/Rome", "America/New_York"
    city: Optional[str] = None  # Optional city name
    nation: Optional[str] = None  # Optional nation code (ISO 3166-1 alpha-2)
    zodiac_type: str = "Tropical"
    houses_system: str = "P"  # P = Placidus (default)

    @field_validator("year", "month", "day", "hour", "minute", "lat", "lng")
    @classmethod
    def validate_numbers(cls, v, info):
        if v is None:
            raise ValueError(f"{info.field_name} is required")
        return v


class PersonResponse(BaseModel):
    id: int
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    lat: float
    lng: float
    tz_str: str
    city: Optional[str] = None
    nation: Optional[str] = None
    zodiac_type: str
    houses_system: str
    chart_data: Optional[dict] = None
    svg_path: Optional[str] = None
    created_at: str


# Database helper functions
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.post("/persons")
async def save_person(data: BirthData):
    """Save birth data (and optionally chart) for later recall"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO persons 
            (name, year, month, day, hour, minute, lat, lng, tz_str, city, nation, zodiac_type, houses_system)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data.name,
                data.year,
                data.month,
                data.day,
                data.hour,
                data.minute,
                data.lat,
                data.lng,
                data.tz_str,
                data.city,
                data.nation,
                data.zodiac_type,
                data.houses_system,
            ),
        )
        person_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {"id": person_id, "message": "Person saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/persons", response_model=List[PersonResponse])
async def list_persons():
    """List all saved persons"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persons ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    persons = []
    for row in rows:
        person = dict(row)
        if person["chart_data"]:
            person["chart_data"] = json.loads(person["chart_data"])
        persons.append(person)
    return persons


@app.get("/persons/{person_id}")
async def get_person(person_id: int):
    """Load a specific saved person (with chart if available)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Person not found")

    person = dict(row)
    if person["chart_data"]:
        person["chart_data"] = json.loads(person["chart_data"])
    return person


@app.delete("/persons/{person_id}")
async def delete_person(person_id: int):
    """Delete a saved person"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM persons WHERE id = ?", (person_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Person deleted successfully"}


@app.post("/chart")
async def generate_chart(data: BirthData):
    try:
        # Step 1: Create astrological subject from birth data
        subject = AstrologicalSubjectFactory.from_birth_data(
            name=data.name,
            year=data.year,
            month=data.month,
            day=data.day,
            hour=data.hour,
            minute=data.minute,
            lat=data.lat,
            lng=data.lng,
            tz_str=data.tz_str or "UTC",  # fallback
            city=data.city,
            nation=data.nation,
            online=False,
            houses_system_identifier=data.houses_system,
        )

        # Step 2: Generate full chart data (includes aspects, etc.)
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

        # Step 3: Create visualization normally with your true Brisbane data
        chart_drawer = ChartDrawer(chart_data=chart_data)

        # Step 4: Save the original SVG file
        filename = f"{data.name.replace(' ', '-')}-chart"
        svg_full_path = f"/charts_output/{filename}.svg"

        try:
            output_dir = Path("../frontend/public/charts_output")
            output_dir.mkdir(exist_ok=True)
            svg_path = output_dir / f"{filename}.svg"

            # Force overwrite if exists (most reliable)
            if svg_path.exists():
                svg_path.unlink()  # Delete old one first

            chart_drawer.save_svg(output_path=output_dir, filename=filename)

        except Exception as svg_err:
            print(f"SVG save failed: {svg_err}")  # Log it
            svg_full_path = None  # or fallback

        # Optionally save full chart to DB (for recall with data)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE persons 
                SET chart_data = ?, svg_path = ?
                WHERE name = ? AND year = ? AND month = ? AND day = ? 
                ORDER BY id DESC LIMIT 1
            """,
                (
                    json.dumps(
                        {
                            "planets": planets_data,
                            "houses": houses_data,
                            "aspects": (
                                chart_data.aspects
                                if hasattr(chart_data, "aspects")
                                else []
                            ),
                            # Add more as needed
                        }
                    ),
                    svg_full_path,
                    data.name,
                    data.year,
                    data.month,
                    data.day,
                ),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass  # Non-critical if DB update fails

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
            "aspects": (chart_data.aspects if hasattr(chart_data, "aspects") else []),
            "svg_path": f"/charts_output/{filename}.svg",
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
