import unittest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from project.core.focus_session import FocusSession
from project.core.habit import Habit
from project.analytics.focuscore import (
    compute_focus_score,
    focus_grade,
    compute_weekly_focus_score,
    compute_weekly_focus_with_grade,
)


class TestFocusCore(unittest.TestCase):
    """Test class for focuscore module functionality"""

    @classmethod
    def setUpClass(cls):
        cls.week_start = date(2024, 1, 1)
        cls.week_end = date(2024, 1, 7)

        # Create sample habits for all tests
        cls.sample_habits = [
            Mock(spec=Habit, is_completed_on_date=Mock(return_value=True)),
            Mock(spec=Habit, is_completed_on_date=Mock(return_value=False)),
            Mock(spec=Habit, is_completed_on_date=Mock(return_value=True)),
        ]

        print("Setting up TestFocusClass - Class level setup complete")

    @classmethod
    def tearDownClass(cls):
        cls.sample_habits.clear()
        print("Tearing down TestFocusClass - Class level cleanup complete")

    def setUp(self):
        # Create sample focus sessions for each test
        self.sample_sessions = [
            Mock(
                spec=FocusSession,
                start_time=datetime(2024, 1, 1, 9, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 30, 0),
                duration_minutes=90,
            ),
            Mock(
                spec=FocusSession,
                start_time=datetime(2024, 1, 2, 14, 0, 0),
                end_time=datetime(2024, 1, 2, 15, 45, 0),
                duration_minutes=105,
            ),
            Mock(
                spec=FocusSession,
                start_time=datetime(2024, 1, 3, 10, 0, 0),
                end_time=datetime(2024, 1, 3, 11, 0, 0),
                duration_minutes=60,
            ),
        ]

        # Reset habit completion mocks
        for habit in self.sample_habits:
            habit.is_completed_on_date.reset_mock()

        print("Test setup complete - ready to run test")

    def tearDown(self):
        self.sample_sessions.clear()
        print("Test teardown complete - cleaning up test data")

    def test_compute_focus_score_basic_cases(self):
        # Test case 1: Perfect score scenario
        score1 = compute_focus_score(
            total_focus_minutes=300,
            distraction_rate=0.0,
            habit_completion_rate=1.0,
        )

        # Test case 2: Minimum score scenario
        score2 = compute_focus_score(
            total_focus_minutes=0,
            distraction_rate=6.0,
            habit_completion_rate=0.0,
        )

        # Test case 3: Average scenario
        score3 = compute_focus_score(
            total_focus_minutes=150,
            distraction_rate=3.0,
            habit_completion_rate=0.5,
        )

        # Test case 4: No distraction data scenario
        score4 = compute_focus_score(
            total_focus_minutes=200,
            distraction_rate=None,
            habit_completion_rate=0.8,
        )

        # Assertions for test case 1 (Perfect score)
        self.assertEqual(score1, 100.0, "Perfect inputs should yield perfect score")
        self.assertGreaterEqual(score1, 0.0, "Score should be non-negative")
        self.assertLessEqual(score1, 100.0, "Score should not exceed 100")
        self.assertIsInstance(score1, float, "Score should be a float")

        # Assertions for test case 2 (Minimum score)
        self.assertEqual(score2, 0.0, "Worst inputs should yield minimum score")
        self.assertGreaterEqual(score2, 0.0, "Score should be non-negative")
        self.assertLessEqual(score2, 100.0, "Score should not exceed 100")
        self.assertIsInstance(score2, float, "Score should be a float")

        # Assertions for test case 3 (Average scenario)
        self.assertGreater(score3, 0.0, "Average inputs should yield positive score")
        self.assertLess(score3, 100.0, "Average inputs should yield less than perfect score")
        self.assertGreaterEqual(score3, 0.0, "Score should be non-negative")
        self.assertIsInstance(score3, float, "Score should be a float")

        # Assertions for test case 4 (No distraction data)
        self.assertGreater(score4, 0.0, "Score with no distraction data should be positive")
        self.assertLess(score4, 100.0, "Score should be less than perfect")
        self.assertGreaterEqual(score4, 0.0, "Score should be non-negative")
        self.assertIsInstance(score4, float, "Score should be a float")

    def test_focus_grade_classification(self):
        # Test case 1: Elite focus classification
        grade1 = focus_grade(95.0)
        grade2 = focus_grade(85.0)
        grade3 = focus_grade(100.0)

        # Test case 2: Strong focus classification
        grade4 = focus_grade(75.0)
        grade5 = focus_grade(79.9)

        # Test case 3: OK focus classification
        grade6 = focus_grade(59.9)
        grade7 = focus_grade(50.0)
        grade8 = focus_grade(40.0)

        # Test case 4: Needs work classification
        grade9 = focus_grade(35.0)
        grade10 = focus_grade(0.0)
        grade11 = focus_grade(39.9)

        # Assertions for Elite focus
        self.assertEqual(grade1, "Elite focus", "Score >= 80 should be Elite focus")
        self.assertEqual(grade2, "Elite focus", "Score >= 80 should be Elite focus")
        self.assertEqual(grade3, "Elite focus", "Score >= 80 should be Elite focus")
        self.assertIsInstance(grade1, str, "Grade should be a string")

        # Assertions for Strong focus
        self.assertEqual(grade4, "Strong", "Score between 60-80 should be Strong")
        self.assertEqual(grade5, "Strong", "Score between 60-80 should be Strong")
        self.assertIsInstance(grade4, str, "Grade should be a string")

        # Assertions for OK focus
        self.assertEqual(grade6, "OK", "Score between 40-60 should be OK")
        self.assertEqual(grade7, "OK", "Score between 40-60 should be OK")
        self.assertEqual(grade8, "OK", "Score between 40-60 should be OK")
        self.assertIsInstance(grade6, str, "Grade should be a string")

        # Assertions for Needs work
        self.assertEqual(grade9, "Needs work", "Score < 40 should be Needs work")
        self.assertEqual(grade10, "Needs work", "Score < 40 should be Needs work")
        self.assertEqual(grade11, "Needs work", "Score < 40 should be Needs work")
        self.assertIsInstance(grade9, str, "Grade should be a string")

    @patch("project.analytics.focuscore.compute_weekly_summary")
    @patch("project.analytics.focuscore.distraction_rate_per_hour")
    def test_compute_weekly_focus_score_integration(self, mock_distraction_rate, mock_weekly_summary):
        # Setup mock returns
        mock_weekly_summary.return_value = {
            "total_focus_minutes": 250,
            "habit_completion_rate": 0.8,
            "week_end": self.week_end,
        }
        mock_distraction_rate.return_value = 2.5

        # Execute the function
        score = compute_weekly_focus_score(
            sessions=self.sample_sessions,
            habits=self.sample_habits,
            week_start=self.week_start,
        )

        # Assertions for mock calls
        mock_weekly_summary.assert_called_once_with(self.sample_sessions, self.sample_habits, self.week_start)

        # Assertions for distraction rate call
        called_sessions = mock_distraction_rate.call_args[1]["sessions"]
        self.assertEqual(len(called_sessions), 3, "Should filter sessions for the week")
        mock_distraction_rate.assert_called_once()

        # Assertions for the result
        self.assertIsInstance(score, float, "Score should be a float")
        self.assertGreaterEqual(score, 0.0, "Score should be non-negative")
        self.assertLessEqual(score, 100.0, "Score should not exceed 100")
        self.assertGreater(score, 0.0, "Score with reasonable inputs should be positive")

    def test_compute_weekly_focus_with_grade_integration(self):
        with patch("project.analytics.focuscore.compute_weekly_focus_score") as mock_score:
            # Setup mock return
            mock_score.return_value = 75.5

            # Execute the function
            result = compute_weekly_focus_with_grade(
                sessions=self.sample_sessions,
                habits=self.sample_habits,
                week_start=self.week_start,
            )

            # Assertions
            mock_score.assert_called_once_with(self.sample_sessions, self.sample_habits, self.week_start)

            # Verify return type and structure
            self.assertIsInstance(result, tuple, "Should return a tuple")
            self.assertEqual(len(result), 2, "Tuple should contain score and grade")

            score, grade = result

            # Assertions for score
            self.assertEqual(score, 75.5, "Score should match mock return")
            self.assertIsInstance(score, float, "Score should be float")

            # Assertions for grade
            self.assertEqual(grade, "Strong", "75.5 should be Strong grade")
            self.assertIsInstance(grade, str, "Grade should be string")

            # Verify grade matches the score
            expected_grade = focus_grade(score)
            self.assertEqual(grade, expected_grade, "Grade should match focus_grade function")


def create_test_suite():
    """Create and return a test suite containing all test classes"""
    suite = unittest.TestSuite()

    # Add test cases from TestFocusCore class
    loader = unittest.TestLoader()

    # Add individual test methods
    suite.addTest(TestFocusCore("test_compute_focus_score_basic_cases"))
    suite.addTest(TestFocusCore("test_focus_grade_classification"))
    suite.addTest(TestFocusCore("test_compute_weekly_focus_score_integration"))
    suite.addTest(TestFocusCore("test_compute_weekly_focus_with_grade_integration"))

    return suite


if __name__ == "__main__":
    # Create test suite
    test_suite = create_test_suite()

    # Run the test suite
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print test results summary
    print(f"\nTest Results: {result.testsRun} tests run")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    # Verify the test suite called the test classes properly
    if result.wasSuccessful():
        print("Test suite executed successfully - all test classes called properly")
    else:
        print("Test suite had failures or errors")
