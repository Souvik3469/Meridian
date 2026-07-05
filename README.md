# ELD Trip Planner

A full-stack app for truck drivers: enter a trip's current/pickup/dropoff
locations and how many hours you've already worked this cycle, and get back
a route map with rest/fuel stops plus auto-filled FMCSA daily log sheets.

Built for a take-home full-stack assessment. See [ARCHITECTURE.md](ARCHITECTURE.md)
for how it works, in plain English and in HLD/LLD technical detail.

- **Live app**: TBD
- **Loom walkthrough**: TBD

## Tech stack

- **Backend**: Django + Django REST Framework
- **Frontend**: React (Vite)
- **Routing / geocoding**: [OpenRouteService](https://openrouteservice.org/)
- **Map rendering**: Leaflet

## Assumptions

Per the assignment brief:

- Property-carrying driver, 70-hour/8-day cycle, no adverse driving conditions
- Fuel stop at least once every 1,000 miles
- 1 hour each for pickup and dropoff

## Local setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENROUTESERVICE_API_KEY
python manage.py migrate
python manage.py runserver 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # points at the backend URL
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` by default (see
`frontend/.env.example`).

## Project structure

```
backend/    Django project (config/) + trips app (API, HOS engine)
frontend/   React app (Vite)
ARCHITECTURE.md   System design: plain-English + HLD/LLD
```
