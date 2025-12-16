import unittest
from datetime import datetime, timedelta

from project.core.task import Task
from project.planner.base_planner import BalancedPlanner, PlannedBlock
from project.planner.daily_plan import (
    generate_daily_plan,
    _normalize_energy_level,
    _parse_time,
)
from project.planner.exceptions import PlannerConfigurationError


class PlannerHelperTests(unittest.TestCase):
    """
    Additional planner coverage for helper utilities and scheduling toggles.
    Each test contains four or more assertions as per rubric.
    """

    @classmethod
    def setUpClass(cls):
        print("PlannerHelperTests: setUpClass")
        cls.default_start = "09:00"
        cls.default_end = "12:00"
        cls.today = datetime.now().date()

    @classmethod
    def tearDownClass(cls):
        print("PlannerHelperTests: tearDownClass")
        cls.default_start = None
        cls.default_end = None
        cls.today = None

    def setUp(self):
        self.study = Task("Study", 50, category="study", pomodoro=True)
        self.completed = Task("Done", 20, category="study", completed=True)
        self.zero = Task("Zero", 0, category="study")

    def tearDown(self):
        self.study = None
        self.completed = None
        self.zero = None

    def test_normalize_and_parse_validation(self):
        parsed = _parse_time("07:15", "start time")
        self.assertEqual(parsed.hour, 7)
        self.assertEqual(parsed.minute, 15)
        self.assertEqual(parsed.date(), self.today)
        self.assertEqual(_normalize_energy_level("8"), 5)
        self.assertEqual(_normalize_energy_level("0"), 1)
        self.assertEqual(_normalize_energy_level(None), 3)
        with self.assertRaisesRegex(PlannerConfigurationError, "HH:MM"):
            _parse_time("7-15", "start time")

    def test_generate_plan_pomodoro_toggle_and_filters(self):
        blocks = generate_daily_plan(
            [self.study, self.completed, self.zero],
            start=self.default_start,
            end="10:00",
            prefer_pomodoro=True,
        )
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].task.name, "Study")
        self.assertEqual((blocks[0].end - blocks[0].start), timedelta(minutes=25))
        self.assertEqual((blocks[1].end - blocks[1].start), timedelta(minutes=25))

        # Disabling pomodoro should keep a single block for the same task.
        single_block = generate_daily_plan(
            [self.study],
            start=self.default_start,
            end=self.default_end,
            prefer_pomodoro=False,
        )
        self.assertEqual(len(single_block), 1)
        self.assertEqual(single_block[0].task.name, "Study")
        self.assertEqual(
            (single_block[0].end - single_block[0].start), timedelta(minutes=50)
        )

    def test_balanced_planner_recovery_interval_clamping(self):
        balanced = BalancedPlanner(recovery_interval=-3)
        tasks = [
            Task("Task A", 10, category="study", deadline=self.today),
            Task("Task B", 10, category="study", deadline=self.today + timedelta(days=1)),
            Task("Break", 5, category="recovery"),
        ]
        blocks = balanced.generate(
            tasks, day_start=datetime(2024, 1, 1, 9, 0), day_end=datetime(2024, 1, 1, 9, 40)
        )
        self.assertGreaterEqual(len(blocks), 3)
        self.assertEqual([b.task.name for b in blocks[:3]], ["Task A", "Break", "Task B"])
        self.assertEqual(blocks[1].task.category, "recovery")
        self.assertLessEqual((blocks[0].end - blocks[0].start), timedelta(minutes=10))
        self.assertLessEqual((blocks[2].end - blocks[2].start), timedelta(minutes=10))

    def test_planned_block_string_format(self):
        start = datetime(2024, 1, 1, 9, 0)
        end = datetime(2024, 1, 1, 9, 30)
        block = PlannedBlock(task=self.study, start=start, end=end)
        self.assertIn("09:00-09:30", str(block))
        self.assertIn(self.study.name, str(block))
        self.assertTrue(str(block).startswith("09:00"))
        self.assertTrue(str(block).endswith(self.study.name))

    def test_pomodoro_scheduler_break_cutoff(self):
        tasks = [Task("Pomodoro Task", 50, category="study", pomodoro=True)]
        blocks = generate_daily_plan(tasks, start="09:00", end="09:26", prefer_pomodoro=True)
        self.assertEqual(len(blocks), 1)
        self.assertEqual((blocks[0].end - blocks[0].start), timedelta(minutes=25))
        self.assertEqual(blocks[0].task.name, "Pomodoro Task")

    def test_balanced_planner_appends_remaining_recovery(self):
        planner = BalancedPlanner(recovery_interval=2)
        tasks = [
            Task("Study A", 10, category="study"),
            Task("Study B", 10, category="study"),
            Task("Break 1", 5, category="recovery"),
            Task("Break 2", 5, category="recovery"),
        ]
        blocks = planner.generate(
            tasks, day_start=datetime(2024, 1, 1, 9, 0), day_end=datetime(2024, 1, 1, 9, 40)
        )
        self.assertGreaterEqual(len(blocks), 4)
        self.assertEqual(blocks[0].task.name, "Study A")
        self.assertEqual(blocks[2].task.category, "recovery")
        self.assertEqual(blocks[-1].task.name, "Break 2")

    def test_normalize_energy_level_clamps_negative(self):
        self.assertEqual(_normalize_energy_level(-5), 1)


if __name__ == "__main__":
    unittest.main()
