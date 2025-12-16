from __future__ import annotations

from datetime import date
import sys
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.core.focus_session import FocusSession
from project.core.habit import Habit

from project.analytics.weekly_report import compute_weekly_summary
from project.analytics.distraction import distraction_rate_per_hour


def compute_focus_score(
    total_focus_minutes: int,
    distraction_rate: Optional[float],
    habit_completion_rate: float,
) -> float:
    # Focus time: up to 40 points
    capped_minutes = max(0, min(total_focus_minutes, 300))
    focus_component = (capped_minutes / 300.0) * 40.0
    # Habits: up to 40 points
    h_rate = max(0.0, min(habit_completion_rate, 1.0))
    habit_component = h_rate * 40.0

    # Distractions: up to 20 points
    if distraction_rate is None:
        # If we have no data, assume neutral
        distraction_component = 10.0
    else:
        # 0 distractions/hour -> 20 pts, 6+ -> 0 pts (clamped)
        dr = max(0.0, min(distraction_rate, 6.0))
        distraction_component = 20.0 * (1.0 - dr / 6.0)

    score = focus_component + habit_component + distraction_component
    # Clamp to [0, 100]
    return max(0.0, min(score, 100.0))


def focus_grade(score: float) -> str:
    if score < 40:
        return "Needs work"
    if score < 60:
        return "OK"
    if score < 80:
        return "Strong"
    return "Elite focus"


def compute_weekly_focus_score(
    sessions: List[FocusSession],
    habits: List[Habit],
    week_start: date,
) -> float:

    summary = compute_weekly_summary(sessions, habits, week_start)
    d_rate = distraction_rate_per_hour(
        sessions=[s for s in sessions if week_start <= s.start_time.date() <= summary["week_end"]]
    )

    total_focus_minutes = int(summary.get("total_focus_minutes", 0))
    habit_completion_rate = float(summary.get("habit_completion_rate", 0.0))

    return compute_focus_score(
        total_focus_minutes=total_focus_minutes,
        distraction_rate=d_rate,
        habit_completion_rate=habit_completion_rate,
    )


def compute_weekly_focus_with_grade(
    sessions: List[FocusSession],
    habits: List[Habit],
    week_start: date,
) -> Tuple[float, str]:
    
    score = compute_weekly_focus_score(sessions, habits, week_start)
    grade = focus_grade(score)
    return score, grade
