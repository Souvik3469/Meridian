# Meridian

An ELD trip planner for truck drivers: enter a trip's current/pickup/dropoff
locations and how many hours you've already worked this cycle, and get back
a route map with rest/fuel stops plus auto-filled FMCSA daily log sheets.

See [ARCHITECTURE.md](ARCHITECTURE.md) for how it works, in plain English and
in HLD/LLD technical detail, [PRODUCT.md](PRODUCT.md) for the product-owner
read on who it's for and what it does (and doesn't) solve, and
[TEST_PLAN.md](TEST_PLAN.md) for a manual test plan covering basic through
edge-case scenarios.

- **Live app**: https://meridian-route.vercel.app/

## Origin

Meridian started as a take-home assessment. The brief was the ELD trip planner: given a trip and a
driver's used cycle hours, produce a compliant route and filled log sheets.

I kept building after the assessment closed, because the interesting part — the Hours-of-Service
rule engine — was more of a constraint-scheduling problem than the brief needed it to be. What came
after the original scope: the engine rewritten as a pure, dependency-free simulator with its own
unit tests; multi-stop trips; trip replanning; location autocomplete; the log-sheet export; request
throttling; and the documentation set in this repository.

The simplifications that remain against the real federal rules — no sleeper-berth split provision,
no adverse-driving exception, a relative rather than calendar-anchored clock — are listed as
assumptions at the top of `backend/trips/hos/engine.py`.

## Tech stack

- **Backend**: Django + Django REST Framework
- **Frontend**: React (Vite)
- **Routing / geocoding**: [OpenRouteService](https://openrouteservice.org/)
- **Map rendering**: Leaflet

## Assumptions

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
PRODUCT.md        Product-owner perspective: user journey, scope, limits
TEST_PLAN.md      Manual test plan: basic -> advanced -> edge cases
```
