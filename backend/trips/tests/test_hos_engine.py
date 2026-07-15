from django.test import SimpleTestCase

from trips.hos.engine import (
    DutyStatus,
    RouteLeg,
    build_duty_schedule,
    split_into_days,
)


class BuildDutyScheduleTests(SimpleTestCase):
    def test_short_trip_needs_no_rest(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=50, duration_hours=1, label="to pickup"),
                RouteLeg(distance_miles=100, duration_hours=2, label="to dropoff"),
            ],
            stop_labels=["Pickup", "Dropoff"],
        )

        statuses = [e.status for e in entries]
        self.assertEqual(
            statuses,
            [
                DutyStatus.DRIVING,
                DutyStatus.ON_DUTY_NOT_DRIVING,
                DutyStatus.DRIVING,
                DutyStatus.ON_DUTY_NOT_DRIVING,
            ],
        )
        self.assertAlmostEqual(entries[-1].end_hour, 5.0)

    def test_break_inserted_after_eight_hours_driving(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=500, duration_hours=10, label="long haul"),
                RouteLeg(distance_miles=0, duration_hours=0, label="n/a"),
            ],
            stop_labels=["Pickup", "Dropoff"],
        )

        driving_entries = [e for e in entries if e.status == DutyStatus.DRIVING]
        break_entries = [e for e in entries if e.label == "30-minute break"]

        self.assertEqual(len(break_entries), 1)
        self.assertAlmostEqual(break_entries[0].duration, 0.5)
        self.assertAlmostEqual(driving_entries[0].duration, 8.0)
        self.assertAlmostEqual(sum(e.duration for e in driving_entries), 10.0)
        # The break happens strictly between the two driving segments.
        self.assertLessEqual(driving_entries[0].end_hour, break_entries[0].start_hour)
        self.assertLessEqual(break_entries[0].end_hour, driving_entries[1].start_hour)

    def test_ten_hour_reset_inserted_after_eleven_hours_driving(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=650, duration_hours=13, label="very long haul"),
                RouteLeg(distance_miles=0, duration_hours=0, label="n/a"),
            ],
            stop_labels=["Pickup", "Dropoff"],
        )

        reset_entries = [e for e in entries if e.label == "10-hour rest period"]
        driving_entries = [e for e in entries if e.status == DutyStatus.DRIVING]

        self.assertEqual(len(reset_entries), 1)
        self.assertAlmostEqual(reset_entries[0].duration, 10.0)
        self.assertAlmostEqual(sum(e.duration for e in driving_entries), 13.0)
        # No single driving segment exceeds the 11-hour daily limit.
        self.assertTrue(all(e.duration <= 11.0 + 1e-6 for e in driving_entries))

    def test_thirty_four_hour_restart_when_cycle_exhausted(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=68,
            legs=[
                RouteLeg(distance_miles=150, duration_hours=3, label="short haul"),
                RouteLeg(distance_miles=0, duration_hours=0, label="n/a"),
            ],
            stop_labels=["Pickup", "Dropoff"],
        )

        restart_entries = [e for e in entries if e.label == "34-hour restart"]
        self.assertEqual(len(restart_entries), 1)
        self.assertAlmostEqual(restart_entries[0].duration, 34.0)

    def test_trip_start_hour_prepends_off_duty_block(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=50, duration_hours=1, label="to pickup"),
                RouteLeg(distance_miles=100, duration_hours=2, label="to dropoff"),
            ],
            stop_labels=["Pickup", "Dropoff"],
            trip_start_hour=6.5,
        )

        self.assertEqual(entries[0].status, DutyStatus.OFF_DUTY)
        self.assertAlmostEqual(entries[0].start_hour, 0.0)
        self.assertAlmostEqual(entries[0].end_hour, 6.5)
        self.assertEqual(entries[1].status, DutyStatus.DRIVING)
        self.assertAlmostEqual(entries[1].start_hour, 6.5)
        self.assertAlmostEqual(entries[-1].end_hour, 11.5)

    def test_zero_trip_start_hour_matches_default_behavior(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=50, duration_hours=1, label="to pickup"),
                RouteLeg(distance_miles=100, duration_hours=2, label="to dropoff"),
            ],
            stop_labels=["Pickup", "Dropoff"],
            trip_start_hour=0.0,
        )

        self.assertEqual(entries[0].status, DutyStatus.DRIVING)
        self.assertAlmostEqual(entries[0].start_hour, 0.0)

    def test_fuel_stop_inserted_every_thousand_miles(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=1200, duration_hours=20, label="cross-country"),
                RouteLeg(distance_miles=0, duration_hours=0, label="n/a"),
            ],
            stop_labels=["Pickup", "Dropoff"],
        )

        fuel_stops = [e for e in entries if e.label == "Fuel stop"]
        self.assertEqual(len(fuel_stops), 1)

    def test_more_than_two_stops_each_get_an_on_duty_block(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=50, duration_hours=1, label="leg 1"),
                RouteLeg(distance_miles=60, duration_hours=1, label="leg 2"),
                RouteLeg(distance_miles=70, duration_hours=1, label="leg 3"),
                RouteLeg(distance_miles=80, duration_hours=1, label="leg 4"),
            ],
            stop_labels=["Pickup A", "Dropoff A", "Pickup B", "Dropoff B"],
        )

        statuses = [e.status for e in entries]
        self.assertEqual(
            statuses,
            [
                DutyStatus.DRIVING,
                DutyStatus.ON_DUTY_NOT_DRIVING,
                DutyStatus.DRIVING,
                DutyStatus.ON_DUTY_NOT_DRIVING,
                DutyStatus.DRIVING,
                DutyStatus.ON_DUTY_NOT_DRIVING,
                DutyStatus.DRIVING,
                DutyStatus.ON_DUTY_NOT_DRIVING,
            ],
        )
        on_duty_labels = [e.label for e in entries if e.status == DutyStatus.ON_DUTY_NOT_DRIVING]
        self.assertEqual(on_duty_labels, ["Pickup A", "Dropoff A", "Pickup B", "Dropoff B"])
        # 4 driving hours + 4 one-hour stops.
        self.assertAlmostEqual(entries[-1].end_hour, 8.0)

    def test_mismatched_legs_and_labels_raises(self):
        with self.assertRaises(ValueError):
            build_duty_schedule(
                current_cycle_used_hours=0,
                legs=[RouteLeg(distance_miles=50, duration_hours=1, label="leg 1")],
                stop_labels=["Pickup", "Dropoff"],
            )


class SplitIntoDaysTests(SimpleTestCase):
    def test_entry_spanning_midnight_is_split_across_two_days(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=1100, duration_hours=22, label="overnight haul"),
                RouteLeg(distance_miles=0, duration_hours=0, label="n/a"),
            ],
            stop_labels=["Pickup", "Dropoff"],
        )

        days = split_into_days(entries)

        self.assertGreaterEqual(len(days), 2)
        self.assertEqual(days[0].day_number, 1)
        self.assertEqual(days[1].day_number, 2)
        for day in days:
            for entry in day.entries:
                self.assertGreaterEqual(entry.start_hour, 0)
                self.assertLessEqual(entry.end_hour, 24)

    def test_daily_totals_sum_to_day_length(self):
        entries = build_duty_schedule(
            current_cycle_used_hours=0,
            legs=[
                RouteLeg(distance_miles=50, duration_hours=1, label="to pickup"),
                RouteLeg(distance_miles=100, duration_hours=2, label="to dropoff"),
            ],
            stop_labels=["Pickup", "Dropoff"],
        )

        days = split_into_days(entries)
        self.assertEqual(len(days), 1)
        self.assertAlmostEqual(sum(days[0].totals.values()), 5.0)
