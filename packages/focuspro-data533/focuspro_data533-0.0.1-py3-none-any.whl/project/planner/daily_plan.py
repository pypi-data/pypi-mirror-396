
from __future__ import annotations

from datetime import datetime
import sys
from pathlib import Path
from typing import List, Sequence

# Allow running this module directly by adding repo root to sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from core.task import Task
except ImportError:  # Allow use when planner is imported as src.project.planner.*
    from ..core.task import Task
from .base_planner import (
    Planner,
    StudyPlanner,
    EnergyPlanner,
    BalancedPlanner,
    PlannedBlock,
)
from .schedulers import Scheduler, PomodoroScheduler
from .exceptions import PlannerConfigurationError, SchedulingWindowError


def _normalize_energy_level(value) -> int:
    """
    Coerce arbitrary input into the 1-5 range used by EnergyPlanner.
    Falls back to 3 if the value cannot be parsed.
    """
    try:
        level = int(value)
    except (TypeError, ValueError):
        return 3
    except Exception:
        return 3
    return max(1, min(5, level))


def _parse_time(time_str: str, label: str) -> datetime:
    """
    Parse an HH:MM string into a datetime on today's date.
    Raises ValueError with a user-friendly message on bad input.
    """
    today = datetime.today().date()
    try:
        parsed = datetime.strptime(time_str, "%H:%M")
    except (TypeError, ValueError):
        raise PlannerConfigurationError(
            f"{label} must be in HH:MM (24-hour) format."
        )
    except Exception as exc:
        raise PlannerConfigurationError(f"Unexpected error parsing {label}") from exc
    return parsed.replace(year=today.year, month=today.month, day=today.day)


def get_planner(
    mode: str = "study",
    energy_level: int = 3,
    scheduler: Scheduler | None = None,
) -> Planner:

    mode = mode.lower()
    energy_level = _normalize_energy_level(energy_level)

    if mode == "study":
        return StudyPlanner(scheduler=scheduler)

    elif mode == "energy":
        return EnergyPlanner(energy_level=energy_level, scheduler=scheduler)

    elif mode == "balanced":
        return BalancedPlanner(scheduler=scheduler)

    else:
        raise PlannerConfigurationError(
            f"Unknown planner mode '{mode}'. Use 'study', 'energy', or 'balanced'."
        )


def generate_daily_plan(
    tasks: Sequence[Task],
    mode: str = "study",
    energy_level: int = 3,
    start: str = "09:00",
    end: str = "18:00",
    prefer_pomodoro: bool = True,
) -> List[PlannedBlock]:
    """
    Build a daily plan by selecting a planner and scheduler, validating inputs,
    and delegating to the planner's generate method.
    """
    start_dt = _parse_time(start, "start time")
    end_dt = _parse_time(end, "end time")
    energy_level = _normalize_energy_level(energy_level)

    if end_dt <= start_dt:
        raise SchedulingWindowError("End time must be after start time.")

    active_tasks = [
        t
        for t in tasks
        if not getattr(t, "completed", False)
        and (getattr(t, "duration", 0) or 0) > 0
    ]
    if not active_tasks:
        return []

    scheduler: Scheduler | None = None
    if prefer_pomodoro and any(getattr(t, "pomodoro", False) for t in active_tasks):
        scheduler = PomodoroScheduler()

    planner = get_planner(mode=mode, energy_level=energy_level, scheduler=scheduler)

    return planner.generate(tasks=active_tasks, day_start=start_dt, day_end=end_dt)



def _demo():

    # Example placeholder tasks
    tasks = [
        Task("Study MDS", duration=90, category="study"),
        Task("Read textbook", duration=45, category="study"),
        Task("Email admin office", duration=20, category="admin"),
        Task("Stretch / break", duration=10, category="recovery"),
    ]

    print("\n=== FocusForge Daily Planner Demo ===")
    mode = input("Choose planner mode (study / balanced / energy): ").strip().lower()

    if mode == "energy":
        level = int(input("Energy level (1-5): ").strip())
    else:
        level = 3

    blocks = generate_daily_plan(tasks, mode=mode, energy_level=level)

    print("\nGenerated Plan:")
    for block in blocks:
        print(" ", block)


# Allow running file directly
if __name__ == "__main__":
    _demo()
