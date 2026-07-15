# Architecture

## In plain terms

The app has two workers:

- **The face (React frontend)** — a form where the driver enters where they are,
  where they're picking up, where they're dropping off, and how many hours
  they've already worked this week. It later shows a map and the filled-out
  paper logs.
- **The brain (Django backend)** — takes those 4 answers, asks a map service
  for the actual route and its distance/duration, then runs a rules simulator
  that thinks like a compliance officer: "drive for a while, then legally must
  take a break, then drive more, then must stop for the night, then start a
  new day" — until the whole trip is scheduled out hour by hour. It hands back
  the route plus a day-by-day breakdown of what the driver was doing.

The frontend does no legal-rules thinking of its own — it only draws whatever
the backend already computed: the route on a map, and duty-status blocks onto
the log sheet grid, one sheet per day.

## High-Level Design

Client-server, stateless REST API. One core endpoint drives the whole flow.

```mermaid
flowchart LR
  subgraph Client["Browser — React SPA"]
    Form[Trip Form]
    MapView[Map View · Leaflet]
    Logs[Log Sheet Renderer · SVG]
  end

  subgraph Server["Django REST API"]
    API["POST /api/trips/plan/"]
    Geo[Geocoding Client]
    Route[Routing Client]
    Engine["HOS Rule Engine<br/>pure Python, no I/O"]
  end

  ORS[(OpenRouteService)]

  Form -->|trip inputs| API
  API --> Geo --> ORS
  API --> Route --> ORS
  API --> Engine
  API -->|route + daily logs JSON| MapView
  API -->|route + daily logs JSON| Logs
```

### Request flow

```mermaid
sequenceDiagram
  participant U as User
  participant F as React Frontend
  participant B as Django API
  participant O as OpenRouteService

  U->>F: Submit trip form
  F->>B: POST /api/trips/plan/
  B->>O: Geocode current / pickup / dropoff
  O-->>B: Coordinates
  B->>O: Directions (waypoints)
  O-->>B: Distance, duration, route geometry
  B->>B: HOS engine simulates duty schedule
  B-->>F: { route, days: [...] }
  F->>F: Render map + one log sheet per day
```

### Key design decisions

- **Stateless backend.** No DB writes in the core flow — a trip plan doesn't
  need to persist between requests, so there's no Trip model, no migrations
  beyond Django's defaults, and no extra moving parts to deploy or go stale.
- **HOS engine is pure Python.** No network calls, no Django imports beyond
  plain data classes. This makes it trivial to unit-test with fake
  distances/durations instead of hitting a real routing API in tests.
- **Single external dependency (OpenRouteService)** for both geocoding and
  routing, to keep API-key/quota management to one provider.
- **Domain assumptions** (from the assignment brief): property-carrying
  driver, 70hrs/8-day cycle, no adverse driving conditions, fuel stop every
  1,000 miles, 1 hour each for pickup and dropoff.

## Low-Level Design

### Backend modules (`backend/trips/`)

| Module | Responsibility |
|---|---|
| `services/geocoding.py` | Wraps ORS geocode search and autocomplete — location text → `(lat, lng)` / place suggestions |
| `services/routing.py` | Wraps ORS directions API — waypoints → distance, duration, route geometry |
| `hos/engine.py` | The rule simulator (see below) |
| `serializers.py` | Validates the 4 request inputs |
| `views.py` | Orchestrates: validate → geocode → route → run engine → shape response |

### HOS engine (`hos/engine.py`)

Pure, deterministic, no I/O — walks through the trip's required activities in
order (optional off-duty block from midnight to the trip's start time → drive
to pickup → 1hr on-duty at pickup → drive to dropoff → 1hr on-duty at
dropoff, with fuel stops spliced in every 1,000 miles) and tracks state as it
goes:

- hours driven in the current duty day (11-hour limit)
- time remaining in the current 14-hour on-duty window
- time since the last 30-minute break (required after 8 cumulative driving
  hours)
- cycle hours used so far (70-hour/8-day limit, seeded from
  `current_cycle_used_hours`)
- miles since the last fuel stop (1,000-mile interval)

Whenever a limit would be exceeded, the engine inserts the mandatory rest
(30-min break, 10-hour off-duty, or 34-hour restart) before continuing. It
emits a flat, time-ordered list of `(status, start, end, label)` entries,
which are then split at midnight boundaries into one log sheet per calendar
day.

### API contract

```
POST /api/trips/plan/

Request:
{
  "current_location": "Denver, CO",
  "pickup_location": "Colorado Springs, CO",
  "dropoff_location": "Albuquerque, NM",
  "current_cycle_used_hours": 12,
  "trip_start_time": "06:30"
}

Response:
{
  "route": {
    "distance_miles": 420.5,
    "duration_hours": 7.2,
    "geometry": [[lat, lng], ...],
    "stops": [
      { "type": "pickup", "label": "Colorado Springs, CO", "lat": ..., "lng": ... },
      { "type": "fuel", "label": "Fuel stop (mile 1000)", "lat": ..., "lng": ... },
      { "type": "dropoff", "label": "Albuquerque, NM", "lat": ..., "lng": ... }
    ]
  },
  "days": [
    {
      "day_number": 1,
      "entries": [
        { "status": "on_duty", "start_hour": 6.0, "end_hour": 7.0, "label": "Pickup" },
        { "status": "driving", "start_hour": 7.0, "end_hour": 11.5, "label": "En route" },
        ...
      ],
      "totals": { "driving": 8.5, "on_duty": 2.0, "off_duty": 10.0, "sleeper_berth": 0 }
    }
  ],
  "summary": {
    "total_trip_hours": 13.3,
    "requires_34_hour_restart": false
  }
}
```

```
GET /api/locations/autocomplete/?q=Denv

Response:
{
  "results": [
    { "label": "Denver, CO, USA", "lat": 39.74, "lng": -104.99 },
    ...
  ]
}
```

Queries under 3 characters skip the ORS call and return `results: []`
immediately; ORS failures soft-fail to `results: []` with a 200 rather than
surfacing an error, since suggestions are a typing affordance, not the core
planning flow.

### Frontend modules (`frontend/src/`)

| Module | Responsibility |
|---|---|
| `api/tripService.js` | Fetch wrapper for `POST /api/trips/plan/` |
| `api/locationService.js` | Fetch wrapper for `GET /api/locations/autocomplete/` |
| `components/TripForm.jsx` | The trip inputs + submit |
| `components/LocationAutocomplete.jsx` | Debounced place-suggestion dropdown, used by the 3 location fields |
| `components/StatTiles.jsx` | Distance / driving time / total trip time / day-count summary tiles |
| `components/MapView.jsx` | Leaflet map — polyline route + stop markers + "Open in Google Maps" link |
| `components/LogSheet.jsx` | SVG renderer drawing the duty-status step-line onto the FMCSA grid for one day |
| `components/LogSheetList.jsx` | Renders one `LogSheet` per day + the print-only trip-context line |
| `utils/googleMapsLink.js` | Builds a Google Maps directions URL from the trip's real (non-interpolated) stops |
| `App.jsx` | Form → loading → results orchestration, print stylesheet triggers |

## Deployment topology

- **Frontend** — static Vite build deployed to Vercel
- **Backend** — Django (Gunicorn) deployed to Render, env-configured secret
  key, allowed hosts, CORS origins, and the OpenRouteService API key
