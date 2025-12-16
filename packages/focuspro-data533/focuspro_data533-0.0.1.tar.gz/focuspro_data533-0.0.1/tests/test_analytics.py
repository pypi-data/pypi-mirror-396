from __future__ import annotations
import os
import tempfile
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from project.analytics.distraction import (
    total_distractions,
    distraction_rate_per_hour,
    distractions_by_day,
    distraction_rate_by_task,
)
from project.analytics.weekly_report import (
    filter_sessions_for_week,
    _habit_completion_rate_for_week,
    compute_weekly_summary,
    format_weekly_report_text,
    export_weekly_report_markdown,
)
from project.analytics.exceptions import ReportExportError


class _FakeSession:
    def __init__(
        self,
        start_time: datetime,
        duration: int | None = None,
        distractions: int | None = 0,
        task=None,
        habit=None,
        label: str | None = None,
    ):
        self.start_time = start_time
        self._duration = duration
        self.distractions = distractions if distractions is not None else 0
        self.task = task
        self.habit = habit
        self.label = label or "Session"

    def duration_minutes(self):
        return self._duration


class _BrokenSession:
    """Session that raises when accessed to exercise error handling."""

    def __getattr__(self, item):
        raise RuntimeError("broken session")

    def duration_minutes(self):
        raise RuntimeError("bad duration")


class _Habit:
    def __init__(self, name: str, last_completed):
        self.name = name
        self.last_completed = last_completed
        self.streak = 1


class AnalyticsModuleTests(unittest.TestCase):
    def test_distraction_helpers(self):
        base = datetime(2024, 1, 1, 9, 0, 0)
        sessions = [
            _FakeSession(base, duration=60, distractions=6, label="Task A"),
            _FakeSession(base + timedelta(hours=1), duration=None, distractions=5, label="Task B"),
            _FakeSession(base + timedelta(hours=2), duration=0, distractions=2, label="Task C"),
            _BrokenSession(),
        ]

        # total_distractions should skip broken entries and coerce ints
        self.assertEqual(total_distractions(sessions), 6 + 5 + 2)

        # rate should only use valid durations
        rate = distraction_rate_per_hour(sessions)
        self.assertAlmostEqual(rate, 6.0)

        # All invalid durations -> None
        self.assertIsNone(distraction_rate_per_hour([_FakeSession(base, duration=0), _BrokenSession()]))

    def test_distractions_by_day_and_by_task(self):
        base = datetime(2024, 1, 1, 9, 0, 0)

        class _Task:
            def __init__(self, name):
                self.name = name

        class _HabitObj:
            def __init__(self, name):
                self.name = name

        sessions = [
            _FakeSession(base, duration=30, distractions=3, task=_Task("Report")),
            _FakeSession(base + timedelta(days=1), duration=45, distractions=2, habit=_HabitObj("Yoga")),
            _FakeSession(base + timedelta(days=2), duration=60, distractions=1, label="Custom"),
            _BrokenSession(),
        ]

        by_day = distractions_by_day(sessions)
        self.assertEqual(by_day[base.date()], 3)
        self.assertEqual(by_day[(base + timedelta(days=1)).date()], 2)
        self.assertEqual(by_day[(base + timedelta(days=2)).date()], 1)

        rates = distraction_rate_by_task(sessions)
        self.assertAlmostEqual(rates["Report"], 6.0)  # 3 distractions / 0.5 hour
        self.assertAlmostEqual(rates["Habit: Yoga"], 2.6666, places=3)
        self.assertAlmostEqual(rates["Custom"], 1.0)

    def test_weekly_report_helpers(self):
        week_start = date(2024, 1, 1)
        in_range = _FakeSession(datetime(2024, 1, 2, 9, 0, 0), duration=30, distractions=1)
        out_of_range = _FakeSession(datetime(2023, 12, 25, 9, 0, 0), duration=45, distractions=2)

        filtered = filter_sessions_for_week([in_range, out_of_range, _BrokenSession()], week_start)
        self.assertEqual(filtered, [in_range])

        habits = [
            _Habit("In range", week_start + timedelta(days=2)),
            _Habit("Out of range", week_start - timedelta(days=1)),
            _Habit("None date", None),
            _Habit("Invalid type", "yesterday"),
        ]
        rate = _habit_completion_rate_for_week(habits, week_start)
        self.assertAlmostEqual(rate, 0.25)  # 1 of 4 considered

        summary = compute_weekly_summary([in_range], habits, week_start)
        self.assertEqual(summary["total_focus_minutes"], 30)
        self.assertEqual(summary["total_distractions"], 1)
        self.assertGreater(summary["habit_completion_rate"], 0)
        report_text = format_weekly_report_text(summary)
        self.assertIn("Weekly Report", report_text)

    def test_export_report_markdown(self):
        summary = {
            "week_start": date(2024, 1, 1),
            "week_end": date(2024, 1, 7),
            "total_focus_minutes": 90,
            "num_sessions": 2,
            "average_session_length": 45,
            "total_distractions": 3,
            "habit_completion_rate": 0.5,
            "top_habits": ["Test"],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = os.path.join(tmpdir, "report.md")
            export_weekly_report_markdown(summary, outfile)
            with open(outfile, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Weekly Focus Report", content)

        with patch("builtins.open", side_effect=OSError("no disk")):
            with self.assertRaises(ReportExportError):
                export_weekly_report_markdown(summary, "report.md")


if __name__ == "__main__":
    unittest.main()
