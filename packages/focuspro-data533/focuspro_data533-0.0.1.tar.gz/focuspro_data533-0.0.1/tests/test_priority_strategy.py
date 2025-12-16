import unittest
from datetime import date, timedelta

from project.core.task import Task
from project.planner.priority_strategy import (
    SimplePriority,
    DeadlinePriority,
    EnergyAwarePriority,
)


class TestPriorityStrategy(unittest.TestCase):
    def setUp(self) -> None:
        self.simple = SimplePriority()
        self.deadline = DeadlinePriority()
        self.energy = EnergyAwarePriority(energy_level=2)

    class Exploding:
        def __getattr__(self, item):
            raise RuntimeError("boom")

    class BadNumber:
        def __float__(self):
            raise RuntimeError("boom")

        def __int__(self):
            raise RuntimeError("boom")

    class BadDeadline:
        def __sub__(self, other):
            raise RuntimeError("boom")

    def test_simple_priority_handles_invalid_inputs(self) -> None:
        bad = Task("Bad", duration="x", priority="high")
        score = self.simple.score(bad)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        short = Task("Short", duration=30, priority=3)
        long = Task("Long", duration=180, priority=3)
        self.assertGreater(self.simple.score(short), self.simple.score(long))

    def test_deadline_priority_urgency_and_must_do(self) -> None:
        today = date.today()
        overdue = Task("Overdue", duration=30, deadline=today - timedelta(days=1), category="study", difficulty=5)
        due_soon = Task("Due soon", duration=30, deadline=today + timedelta(days=1), category="admin", difficulty=2)
        no_deadline = Task("Anytime", duration=30, category="other", difficulty=1)
        must_today = Task("Must today", duration=30, category="study", must_do_today=True)
        bad_deadline = Task("Bad deadline", duration="oops", deadline="not a date", category=None, difficulty="x")

        scores = {
            "overdue": self.deadline.score(overdue),
            "due_soon": self.deadline.score(due_soon),
            "no_deadline": self.deadline.score(no_deadline),
            "must_today": self.deadline.score(must_today),
            "bad_deadline": self.deadline.score(bad_deadline),
        }
        self.assertGreater(scores["overdue"], scores["due_soon"])
        self.assertGreater(scores["due_soon"], scores["no_deadline"])
        self.assertGreater(scores["must_today"], scores["no_deadline"])
        self.assertIsInstance(scores["bad_deadline"], float)

    def test_energy_aware_matches_low_energy(self) -> None:
        low_energy = EnergyAwarePriority(energy_level=1)
        high_energy = EnergyAwarePriority(energy_level=10)  # clamps to 5
        easy = Task("Easy", duration=20, difficulty=1)
        hard = Task("Hard", duration=20, difficulty=5)
        self.assertGreater(low_energy.score(easy), low_energy.score(hard))
        self.assertGreater(high_energy.score(hard), high_energy.score(easy))

    def test_energy_aware_deadline_influence(self) -> None:
        today = date.today()
        with_deadline = Task("Deadline task", duration=20, difficulty=3, deadline=today + timedelta(days=1))
        no_deadline = Task("No deadline", duration=20, difficulty=3)
        base = EnergyAwarePriority(energy_level=3)
        self.assertGreater(base.score(with_deadline), base.score(no_deadline))

    def test_energy_aware_handles_invalid_difficulty(self) -> None:
        base = EnergyAwarePriority(energy_level=-3)  # clamps to 1
        weird = Task("Weird", duration=10, difficulty="hard")
        score = base.score(weird)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)

    def test_exception_branches_are_safe(self) -> None:
        bad_number = self.BadNumber()
        bad_deadline = self.BadDeadline()

        class WeirdTask:
            def __init__(self):
                self.duration = bad_number
                self.priority = bad_number
                self.difficulty = bad_number
                self.deadline = bad_deadline
                self.category = None
                self.must_do_today = False

        weird = WeirdTask()

        # SimplePriority should swallow RuntimeError on duration/priority conversion
        self.assertIsInstance(self.simple.score(weird), float)  # type: ignore[arg-type]

        # DeadlinePriority should swallow RuntimeError on difficulty/duration math
        self.assertIsInstance(self.deadline.score(weird), float)  # type: ignore[arg-type]

        # EnergyAwarePriority should swallow RuntimeError on difficulty/deadline math
        self.assertIsInstance(self.energy.score(weird), float)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
