"""Pure-Python simulator for FMCSA Hours-of-Service duty schedules.

No I/O, no Django imports — takes route legs (distance + duration) and the
driver's cycle hours already used, and produces a time-ordered list of duty
status entries. Kept dependency-free so it can be unit-tested with synthetic
distances instead of a real routing API.

Assumptions (per the assignment brief): property-carrying driver, 70hr/8-day
cycle, no adverse driving conditions, a fuel stop every 1,000 miles, and 1
hour each for pickup and dropoff.
"""

from dataclasses import dataclass
from enum import Enum

# Federal HOS limits for a property-carrying driver on a 70hr/8-day cycle.
MAX_DRIVING_HOURS = 11.0
MAX_DUTY_WINDOW_HOURS = 14.0
BREAK_REQUIRED_AFTER_HOURS = 8.0
BREAK_DURATION_HOURS = 0.5
DAILY_RESET_HOURS = 10.0
MAX_CYCLE_HOURS = 70.0
RESTART_DURATION_HOURS = 34.0

# Assignment-specific assumptions (not federal law, but given in the brief).
FUEL_INTERVAL_MILES = 1000.0
FUEL_STOP_HOURS = 0.5
PICKUP_DROPOFF_HOURS = 1.0

_EPSILON = 1e-6


class DutyStatus(str, Enum):
    OFF_DUTY = "off_duty"
    SLEEPER_BERTH = "sleeper_berth"
    DRIVING = "driving"
    ON_DUTY_NOT_DRIVING = "on_duty_not_driving"


@dataclass
class LogEntry:
    status: DutyStatus
    start_hour: float
    end_hour: float
    label: str
    distance_marker_miles: float = 0.0

    @property
    def duration(self) -> float:
        return self.end_hour - self.start_hour


@dataclass
class RouteLeg:
    distance_miles: float
    duration_hours: float
    label: str


class HOSEngine:
    """Walks through a trip's activities, inserting mandatory rests as HOS
    limits are hit, and records a flat timeline of duty status entries."""

    def __init__(self, current_cycle_used_hours: float, trip_start_hour: float = 0.0):
        self.clock = 0.0
        self.duty_window_start = None
        self.driving_hours_today = 0.0
        self.hours_since_break = 0.0
        self.cycle_hours_used = current_cycle_used_hours
        self.miles_since_fuel = 0.0
        self.distance_traveled_miles = 0.0
        self.entries: list[LogEntry] = []

        if trip_start_hour > _EPSILON:
            self._append(DutyStatus.OFF_DUTY, trip_start_hour, "Before trip start")

    def drive(self, distance_miles: float, duration_hours: float, label: str) -> None:
        if duration_hours <= _EPSILON or distance_miles <= _EPSILON:
            return

        avg_speed_mph = distance_miles / duration_hours
        remaining_hours = duration_hours

        while remaining_hours > _EPSILON:
            if self.duty_window_start is None:
                self.duty_window_start = self.clock

            window_left = MAX_DUTY_WINDOW_HOURS - (self.clock - self.duty_window_start)
            driving_left = MAX_DRIVING_HOURS - self.driving_hours_today
            break_left = BREAK_REQUIRED_AFTER_HOURS - self.hours_since_break
            cycle_left = MAX_CYCLE_HOURS - self.cycle_hours_used
            fuel_left = (
                (FUEL_INTERVAL_MILES - self.miles_since_fuel) / avg_speed_mph
                if avg_speed_mph > _EPSILON
                else float("inf")
            )

            chunk = min(remaining_hours, window_left, driving_left, break_left, cycle_left, fuel_left)

            if chunk <= _EPSILON:
                # Priority: mandatory break, then daily reset, then cycle
                # restart, then fuel — regulatory rests take precedence over
                # the assignment's operational fuel-stop assumption.
                if break_left <= _EPSILON:
                    self._take_break()
                elif window_left <= _EPSILON or driving_left <= _EPSILON:
                    self._take_daily_reset()
                elif cycle_left <= _EPSILON:
                    self._take_restart()
                else:
                    self._take_fuel_stop()
                continue

            distance_delta = chunk * avg_speed_mph
            self.miles_since_fuel += distance_delta
            self.distance_traveled_miles += distance_delta
            self._append(DutyStatus.DRIVING, chunk, label)
            remaining_hours -= chunk

    def on_duty(self, duration_hours: float, label: str) -> None:
        remaining = duration_hours
        while remaining > _EPSILON:
            if self.duty_window_start is None:
                self.duty_window_start = self.clock

            window_left = MAX_DUTY_WINDOW_HOURS - (self.clock - self.duty_window_start)
            cycle_left = MAX_CYCLE_HOURS - self.cycle_hours_used
            chunk = min(remaining, window_left, cycle_left)

            if chunk <= _EPSILON:
                if window_left <= _EPSILON:
                    self._take_daily_reset()
                else:
                    self._take_restart()
                continue

            self._append(DutyStatus.ON_DUTY_NOT_DRIVING, chunk, label)
            remaining -= chunk

    def _take_break(self) -> None:
        self._append(DutyStatus.ON_DUTY_NOT_DRIVING, BREAK_DURATION_HOURS, "30-minute break")

    def _take_daily_reset(self) -> None:
        self._append(DutyStatus.OFF_DUTY, DAILY_RESET_HOURS, "10-hour rest period")

    def _take_restart(self) -> None:
        self._append(DutyStatus.OFF_DUTY, RESTART_DURATION_HOURS, "34-hour restart")

    def _take_fuel_stop(self) -> None:
        self._append(DutyStatus.ON_DUTY_NOT_DRIVING, FUEL_STOP_HOURS, "Fuel stop")
        self.miles_since_fuel = 0.0

    def _append(self, status: DutyStatus, duration: float, label: str) -> None:
        if duration <= _EPSILON:
            return

        entry = LogEntry(status, self.clock, self.clock + duration, label, self.distance_traveled_miles)
        self.entries.append(entry)
        self.clock += duration

        if status == DutyStatus.DRIVING:
            self.driving_hours_today += duration
            self.hours_since_break += duration
            self.cycle_hours_used += duration
        elif status == DutyStatus.ON_DUTY_NOT_DRIVING:
            self.cycle_hours_used += duration
            if duration >= BREAK_DURATION_HOURS:
                self.hours_since_break = 0.0
        else:  # OFF_DUTY or SLEEPER_BERTH
            if duration >= BREAK_DURATION_HOURS:
                self.hours_since_break = 0.0
            if duration >= DAILY_RESET_HOURS:
                self.driving_hours_today = 0.0
                self.duty_window_start = None
            if duration >= RESTART_DURATION_HOURS:
                self.cycle_hours_used = 0.0


def build_duty_schedule(
    current_cycle_used_hours: float,
    legs: list[RouteLeg],
    stop_labels: list[str],
    trip_start_hour: float = 0.0,
    on_duty_hours: list[float] | None = None,
) -> list[LogEntry]:
    """Simulates the full trip: drive to each stop in order, with on-duty time
    at each one (pickup, dropoff, or any additional stop in between).

    `on_duty_hours` lets a caller extend a stop past the standard 1-hour
    pickup/dropoff assumption — e.g. a driver reporting they were delayed 2
    hours at a stop — so the rest of the schedule can be recomputed around
    that real delay instead of the plan just being wrong from that point on.
    Defaults to 1 hour per stop when omitted.
    """
    if len(legs) != len(stop_labels):
        raise ValueError("legs and stop_labels must be the same length")

    if on_duty_hours is None:
        on_duty_hours = [PICKUP_DROPOFF_HOURS] * len(legs)
    elif len(on_duty_hours) != len(legs):
        raise ValueError("on_duty_hours must be the same length as legs")

    engine = HOSEngine(current_cycle_used_hours, trip_start_hour)
    for leg, stop_label, stop_hours in zip(legs, stop_labels, on_duty_hours):
        engine.drive(leg.distance_miles, leg.duration_hours, leg.label)
        engine.on_duty(stop_hours, stop_label)
    return engine.entries


@dataclass
class DayEntry:
    status: DutyStatus
    start_hour: float
    end_hour: float
    label: str

    @property
    def duration(self) -> float:
        return self.end_hour - self.start_hour


@dataclass
class DaySchedule:
    day_number: int
    entries: list[DayEntry]
    totals: dict[str, float]


def split_into_days(entries: list[LogEntry]) -> list[DaySchedule]:
    """Splits a flat timeline into per-24-hour-day log sheets, cutting any
    entry that spans midnight into one segment per day."""
    days_by_index: dict[int, list[DayEntry]] = {}

    for entry in entries:
        cursor = entry.start_hour
        while cursor < entry.end_hour - _EPSILON:
            day_index = int(cursor // 24)
            day_boundary = (day_index + 1) * 24
            segment_end = min(entry.end_hour, day_boundary)

            days_by_index.setdefault(day_index, []).append(
                DayEntry(
                    status=entry.status,
                    start_hour=cursor - day_index * 24,
                    end_hour=segment_end - day_index * 24,
                    label=entry.label,
                )
            )
            cursor = segment_end

    schedules = []
    for day_index in sorted(days_by_index):
        day_entries = days_by_index[day_index]
        totals = {status.value: 0.0 for status in DutyStatus}
        for day_entry in day_entries:
            totals[day_entry.status.value] += day_entry.duration
        schedules.append(DaySchedule(day_number=day_index + 1, entries=day_entries, totals=totals))

    return schedules
