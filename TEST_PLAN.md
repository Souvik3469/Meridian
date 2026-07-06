# Manual Test Plan

Run these yourself at **http://localhost:5173** with the backend running at
**http://localhost:8000** (see [README.md](README.md) for setup). Automated
tests (26, all passing — run `python manage.py test trips` in `backend/`)
already cover the HOS engine's logic in isolation with synthetic inputs —
this plan is about verifying the **real, live, end-to-end** behavior: real
geocoding, real routes, real rendering.

A note on exact numbers: OpenRouteService returns real-world distances/
durations, which can shift slightly as road data updates. Where an exact
number is given below, it's from a verified run — use it as a strong
reference, not a brittle assertion. Where it says "check the rule," verify
the *relationship* holds against whatever real numbers come back, not a
specific number.

---

## Tier 1 — Basic / happy path

### TC-1: Short trip, no rest required
**Inputs:** current = `Denver, CO`, pickup = `Boulder, CO`, dropoff = `Fort Collins, CO`, cycle used = `0`

**Expected:**
- HTTP 200, exactly **1 day** of logs, no 34-hour-restart warning banner
- Map shows 3 markers only: current, pickup, dropoff (no rest/fuel pins)
- Log sheet: two `driving` blocks (to pickup, to dropoff) and two `on_duty_not_driving`
  blocks (1 hr each, for pickup/dropoff), no `off_duty` block, no break

**Why:** total driving is short (~1–2 hrs), nowhere near the 8-hour break
threshold, 11-hour driving cap, or 14-hour duty window. This is the engine's
simplest path — no rule fires. Confirms the happy path renders cleanly with
nothing extra.

### TC-2: Round-trip-shaped inputs
**Inputs:** current = `Colorado Springs, CO`, pickup = `Denver, CO`, dropoff = `Colorado Springs, CO`

**Expected:** valid plan, dropoff marker sits very close to (or on top of) the
current-location marker on the map.

**Why:** the engine treats each leg independently by distance/duration, not by
geometry — a route that "returns to start" is not a special case. Confirms
there's no hidden assumption that dropoff ≠ current.

---

## Tier 2 — Single-rule triggers

### TC-3: 30-minute break rule (verified reference case)
**Inputs:** current = `Denver, CO`, pickup = `Colorado Springs, CO`, dropoff = `Albuquerque, NM`, cycle used = `10`

**Expected (from a verified run):**
```
0.0h  – 1.9h   driving              En route to pickup
1.9h  – 2.9h   on_duty_not_driving  Pickup
2.9h  – 10.9h  driving              En route to dropoff   (exactly 8.0h)
10.9h – 11.4h  on_duty_not_driving  30-minute break
11.4h – 12.3h  driving              En route to dropoff
12.3h – 13.3h  on_duty_not_driving  Dropoff
```
Distance ≈ 445 mi, total driving ≈ 10.8 hrs, "Total trip time" stat ≈ 13.3
hrs, 1 day of logs, 1 rest marker on the map (no fuel stop — under 1,000 mi),
no restart warning.

**Why:** the 1-hour pickup activity resets the "time since last break" clock
(any non-driving activity ≥ 30 min does). Driving then accumulates fresh from
0, and the break fires at **exactly 8.0 hours of cumulative driving** — the
federal 30-minute-break-after-8-hours rule. This case exercises that reset
logic precisely.

### TC-4: 34-hour restart via cycle hours (fully controllable)
**Inputs:** current = `Denver, CO`, pickup = `Colorado Springs, CO`, dropoff = `Albuquerque, NM`, cycle used = `69`

**Expected:** a `34-hour restart` entry (exactly 34.0 hrs, status `off_duty`)
appears almost immediately. The amber **"34-hour restart required"** warning
banner appears above the stat tiles. Trip spans **2 days** of logs (compare
to TC-3, same route, cycle used = 10).

**Why:** with 69 of 70 cycle-hours already used, only 1 hour of on-duty time
is available before the 70-hour/8-day cap is hit. This is the only test case
where you fully control *which* rule fires just by varying one input — good
for isolating this rule from route distance. Also the primary check for the
`summary.requires_34_hour_restart` flag and its UI banner.

### TC-5: 11-hour driving limit / 10-hour reset
**Inputs:** current = `Los Angeles, CA`, pickup = `Phoenix, AZ`, dropoff = `Denver, CO`, cycle used = `0`

**Expected:** at least one `10-hour rest period` entry (exactly 10.0 hrs,
`off_duty`) appears once cumulative driving in a duty window approaches
11 hours. Trip spans **2+ days**.

**Why:** LA→Phoenix→Denver is long enough (~1,200+ mi total) that the 11-hour
daily driving cap binds before the trip finishes, independent of the 8-hour
break (which will also fire earlier and separately). Confirms the two limits
don't get confused with each other — you should see **both** a break entry
and a 10-hour reset entry, in that order.

### TC-6: Fuel stop every 1,000 miles
**Inputs:** current = `Los Angeles, CA`, pickup = `Denver, CO`, dropoff = `Chicago, IL`, cycle used = `0`

**Expected:** at least one `Fuel stop` entry (0.5 hrs, `on_duty_not_driving`),
and a corresponding **orange fuel marker** on the map positioned along the
route polyline, not at pickup/dropoff.

**Why:** total distance is ~2,000 mi, comfortably past the 1,000-mile fuel
assumption at least once. Also validates the distance-interpolation math
(`point_at_distance`) that places the fuel marker on the actual road geometry
rather than a straight line between waypoints.

---

## Tier 3 — Advanced / multi-rule

### TC-7: Long-haul torture test
**Inputs:** current = `Seattle, WA`, pickup = `Miami, FL`, dropoff = `New York, NY`, cycle used = `0`

**Expected:** multiple days of logs (likely 5+), multiple `10-hour rest
period` entries, multiple `30-minute break` entries, multiple `Fuel stop`
entries, and likely at least one `34-hour restart` once cumulative on-duty
hours cross 70 within an 8-day span.

**Why:** this is long enough to exercise every rule in the engine at least
once, and to prove they compose correctly in sequence rather than only being
tested in isolation. Check in particular: no single `driving` entry exceeds
11.0 hrs, no on-duty stretch exceeds 14.0 hrs, and days are contiguous with no
gaps or overlaps.

### TC-8: High starting cycle + long trip (stacked constraints)
**Inputs:** same as TC-7 but cycle used = `50`

**Expected:** the 34-hour restart should fire *earlier* in the timeline than
in TC-7, since less cycle headroom is available before the 70-hour cap.

**Why:** confirms `current_cycle_used_hours` is actually seeded into the
simulation's running total, not just accepted and ignored.

---

## Tier 4 — Edge cases & validation

### TC-9: Cycle hours at the upper boundary
**Inputs:** cycle used = `70` (any valid route)

**Expected:** HTTP 200 (70 is inclusive/valid per the serializer). A 34-hour
restart should fire essentially immediately, before any meaningful driving.

### TC-10: Cycle hours over the boundary
**Inputs:** cycle used = `71`

**Expected:** HTTP 400, form/API rejects it — cycle hours can't exceed the
70-hour cycle limit.

### TC-11: Negative cycle hours
**Inputs:** cycle used = `-5`

**Expected:** HTTP 400 — the browser's number input may block this via
`min="0"`, but also try it directly against the API (see the `curl` command
below) to confirm the backend rejects it independently of the frontend.

### TC-12: Nonexistent location
**Inputs:** pickup = `Zzzznotarealplace123`

**Expected:** a clean red error alert — "Couldn't plan this trip. No location
found for 'Zzzznotarealplace123'" — not a crash, not a blank screen, not a raw
stack trace.

**Why:** this is exactly the bug that was caught and fixed earlier in
development (a missing API key used to leak a raw Django debug page here).
This test re-confirms that fix holds for a different failure cause
(unresolvable location vs. missing credentials).

### TC-13: Empty required field
**Action:** leave "Pickup location" blank and click "Plan trip"

**Expected:** the browser blocks submission natively (HTML5 `required`
validation) — no network request should fire at all.

### TC-14: All three locations identical
**Inputs:** current = pickup = dropoff = `Denver, CO`

**Expected:** valid plan with ~0 driving distance/time. Log sheet should show
just two `on_duty_not_driving` blocks (pickup + dropoff, 1 hr each) totaling
2 hours, no `driving` entries, no rest/fuel stops. All 3 map markers overlap
at the same point.

**Why:** confirms the engine's early-return guard (`distance_miles <=
epsilon`) actually skips driving simulation instead of dividing by zero or
looping forever computing an average speed from 0 miles / 0 hours.

### TC-15: Trip spanning exactly midnight
**Action:** inspect any multi-day result (e.g. TC-5 or TC-7) closely at the
day boundary.

**Expected:** an entry that would cross midnight is **split into two**
entries — one ending at hour 24 of day *N*, the next starting at hour 0 of
day *N+1* — with the same status and label, not one gap and not one entry
rendered outside the 0–24 axis.

---

## Tier 5 — UI/UX checks (the part the assignment explicitly grades)

| Check | How to test | Expected |
|---|---|---|
| Loading state | Throttle network in DevTools, submit | Button reads "Planning…" and is disabled until the response returns |
| Error doesn't nuke the form | Trigger TC-12, then look at the form | Your typed inputs are still there — only the result area shows the error |
| Responsive layout | Resize the browser to ~400px wide | Form fields, stat tiles, and log-sheet totals collapse to a single column (not clipped/overlapping) |
| Dark mode | Toggle OS/browser dark mode, reload | Colors flip to the dark palette; text stays legible; map tiles/markers still visible |
| Color isn't the only signal | Look at the error/warning alerts and log sheet rows | Each colored element also has a text label or icon next to it (never color-only meaning) |
| Legend consistency | Compare map legend dots to log-sheet row dots | Categories (rest/fuel on map; duty statuses on log sheet) use one fixed color per category everywhere it appears |
| Multi-day readability | Run TC-7 | Each day gets its own clearly separated card; you can tell which card is which day at a glance |
| Log sheet stays legible on mobile | Resize to ~375px wide | Hour labels/text stay full-size and the chart scrolls horizontally, instead of shrinking to illegible |

## Tier 6 — Export & external navigation (added after initial build)

### TC-16: Print / Save as PDF
**Action:** run TC-3, click "Print / Save as PDF", open the print preview (or
save as PDF)

**Expected:** only the log sheets print, one day per landscape page, with a
one-line trip-context header (`Denver, CO → Colorado Springs, CO →
Albuquerque, NM`). The form, header, stat tiles, map, and buttons are all
excluded — a roadside inspector cares about the daily logs, not the app UI.

**Why:** verified earlier via an actual generated PDF (not just a screenshot)
— this caught two real bugs (map/stat-tiles not actually hidden, a day's
sheet splitting across two pages) that a visual screenshot alone missed.

### TC-17: Open in Google Maps
**Action:** run any successful trip, click "Open in Google Maps" above the map

**Expected:** opens Google Maps (new tab) with driving directions from the
current location, through the pickup as a waypoint, to the dropoff — using
the same three real locations you entered, not the synthetic rest/fuel
markers.

**Why:** confirms the app hands off to real turn-by-turn navigation using
accurate, already-geocoded coordinates, and doesn't route through arbitrary
interpolated points that aren't real stopping locations.

---

## Testing at the API level directly (optional, for backend-only checks)

```bash
curl -s -X POST http://localhost:8000/api/trips/plan/ \
  -H "Content-Type: application/json" \
  -d '{
    "current_location": "Denver, CO",
    "pickup_location": "Colorado Springs, CO",
    "dropoff_location": "Albuquerque, NM",
    "current_cycle_used_hours": 10
  }' | python3 -m json.tool
```

Swap in any test case's inputs. Useful for TC-11 (negative cycle hours)
specifically, since it bypasses the browser's own input validation and hits
the serializer directly.

---

## Does this match what the assignment asked for?

Yes — mapping directly to the brief:

| Assignment requirement | Where it's covered |
|---|---|
| Inputs: current, pickup, dropoff, current cycle used (hrs) | Exactly the 4 form fields — TC-1 through TC-15 all exercise these |
| Output: map with route + stops/rests, using a free map API | Leaflet + OpenStreetMap tiles (free) + OpenRouteService routing (free tier) — TC-1, TC-6 |
| Output: daily log sheets drawn out, multiple sheets for longer trips | `LogSheet`/`LogSheetList` — TC-5, TC-7, TC-15 specifically test the multi-sheet and midnight-split behavior |
| Assumption: 70hr/8-day cycle, property-carrying driver | TC-4, TC-8, TC-9, TC-10 directly target this limit |
| Assumption: fuel every 1,000 miles | TC-6 |
| Assumption: 1 hr each for pickup/dropoff | Baked into every test case's on-duty blocks |
| "We will test the hosted version for accuracy" | Tiers 2–4 are precisely an accuracy audit of the HOS rule engine against the real regulations |
| "UI and UX must be good... can compensate for some inaccuracies" | Tier 5 — this is graded independently of correctness, so don't skip it even if Tiers 1–4 all pass |

Tier 6 (print export, Google Maps link) goes beyond the assignment's literal
input/output spec — they came out of a product-usability discussion, not the
brief itself. See [PRODUCT.md](PRODUCT.md) for that reasoning.

The one thing this plan **can't** validate for you: whether the *hosted*
version (once deployed to Render/Vercel) behaves identically to localhost —
environment differences (CORS origins, allowed hosts, cold starts) are worth
re-running at least TC-1 and TC-12 against once it's live.
