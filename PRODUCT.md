# Product Perspective

A product-owner read on this app: who it's for, the user journey, and an honest
accounting of what it solves today, what's on the roadmap, and what it will
never fix.

## Who's actually opening this app

A property-carrying truck driver (or their dispatcher) who just got assigned a
load: pick up at A, deliver to B, truck currently at C. Before committing to
the run they need to know two things — **can I legally make this trip, and
where will I be forced to stop** — and they need a filled-out daily log to
actually drive with.

## The user journey, as built

1. Driver checks their ELD device for "hours used in my current 70hr/8-day
   cycle"
2. Opens the app, types current/pickup/dropoff + that cycle number, hits
   "Plan trip"
3. Gets back: a map with the route and every rest/fuel stop marked, a
   total-trip-time figure, a loud warning if a 34-hour restart is forced, and
   one pre-drawn FMCSA log sheet per day
4. Uses that to decide if the load is even doable in the promised window, and
   to know in advance where they'll need to park for the night or fuel up

That's a complete, coherent loop for the one job this app does — **pre-trip
feasibility + a draft log**. It is not, and was never scoped to be, a live
ELD replacement.

## Problems the driver faces today (before a tool like this)

- Manually computing HOS math (11-hr/14-hr/70-hr/8-day limits, when the
  30-min break lands, whether a 34-hr restart is coming) is slow and
  error-prone by hand
- No easy way to visualize *where* the mandatory stops will fall along an
  actual route before leaving
- Drawing the paper log grid by hand is tedious and a common source of
  transcription mistakes
- Dispatchers often don't find out a load needs a 34-hour restart until the
  driver is already stuck mid-route

## Problems this app solves now

- Automates the HOS math correctly and consistently (verified against real
  regulations and real routing data)
- Shows rest/fuel stops on an actual map, not just a number
- Auto-drafts the daily log grid instead of hand-drawing it
- Surfaces the 34-hour-restart / total-trip-time reality *before* the driver
  commits, instead of it being buried in a later day's log entry
- **Exports/prints the log** as an actual document via the browser's print
  dialog (dedicated print stylesheet, "Save as PDF" works) — glovebox copy or
  handout for a roadside inspector.
- **Real trip start-time input** — an optional field lets the driver say when
  they're actually leaving; the log correctly shows off-duty time from
  midnight up to that point instead of assuming the trip starts at midnight.
- **Location autocomplete** on all three location fields — suggests real
  places as the driver types, reducing ambiguous or misspelled geocoding
  before it ever reaches the routing step.
- **Multi-stop routes** — the trip is now an ordered list of stops (each
  tagged pickup or dropoff), not a hardcoded single pickup + single dropoff,
  matching how real dispatch chains work.

## Problems it could solve later (real roadmap, not done yet)

- **Editable/recomputable plans** — "I got delayed 2 hours at pickup, replan
  the rest" instead of starting over.
- **Saved trip history / driver accounts** — currently fully stateless by
  design (see [ARCHITECTURE.md](ARCHITECTURE.md)).

## Problems it will never fix

- **It cannot replace a certified ELD device.** FMCSA requires actual duty
  status to come from certified hardware reading real engine/vehicle data,
  tamper-evident. This tool works off self-reported, idealized inputs — it can
  simulate a compliant plan, but it can never be the legal record of what a
  driver actually did. That's a hardware/regulatory category difference no
  amount of feature work closes.
- **It cannot account for reality diverging from the plan** — traffic,
  weather, breakdowns, a dispatcher changing the load mid-route. The moment
  the truck leaves, the plan is a snapshot, not a live truth.
- **It cannot verify the input is honest.** "Cycle hours used" is trusted at
  face value; nothing here cross-checks it against the driver's real ELD
  history. Garbage in, garbage out — structurally, not a bug.
- **It cannot enforce compliance.** It's advisory. Nothing stops a driver from
  ignoring its suggested stops; only the real ELD + FMCSA audits do that.

That distinction — *planning tool* vs *live compliance system* — is worth
keeping in mind when testing: bugs in the HOS math or the UI are fair game to
flag; "it doesn't track me live" isn't a bug, it's a different product.
