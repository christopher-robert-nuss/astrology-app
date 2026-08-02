# Simple Astrology App

A full-stack astrology application for generating and viewing natal chart visualizations. The project combines a FastAPI backend for astrology calculations with a Vue 3 + Vite frontend, and also supports a desktop experience via Electron.

## Overview

This app lets users enter birth details and generate a chart with:

- planetary positions and house placements
- zodiac and house system selection
- aspect calculations
- generated SVG chart output
- a polished UI for exploring the results

## Features

- Birth data input for name, date, time, location, and timezone
- Multiple astrology preferences, including zodiac and house systems
- Dynamic chart generation powered by Kerykeion
- SVG chart rendering and static chart output
- Modern frontend experience with PrimeVue and Tailwind CSS
- Desktop packaging support with Electron

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- Kerykeion
- Uvicorn

### Frontend

- Vue 3
- Vite
- PrimeVue
- Tailwind CSS
- Pinia
- Electron

## Project Structure

```text
backend/         # FastAPI astrology API and chart generation logic
frontend/        # Vue 3 frontend and Electron app shell
docs/            # Project documentation
ephe/            # Ephemeris data used by the astrology engine
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 22.x or newer
- npm

### 1. Clone the repository

```bash
git clone https://github.com/christopher-robert-nuss/astrology-app.git
cd astrology-app
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_backend.py
```

The backend runs by default on http://127.0.0.1:8080.

### 3. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend development server will be available at http://localhost:5173.

### 4. Run the desktop app

From the frontend directory:

```bash
npm run electron:dev
```

## Development Notes

- The API exposes endpoints such as /preferences, /preferences/options, and /chart.
- Generated charts are written to the backend chart output directory and served as SVG files.
- The frontend communicates with the backend during chart generation and preference updates.

## Contributing

Contributions are welcome. If you would like to improve the app, please open an issue or submit a pull request with your changes.

## Acknowledgements

- Built with Kerykeion for astrology calculations
- UI powered by Vue 3, PrimeVue, and Tailwind CSS
