"""
run_demo.py

Expanded demonstration that touches the planner, habits, focus sessions,
and analytics in one go.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Iterable, List, Tuple

# Make imports robust without requiring PYTHONPATH to be set manually.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SRC_DIR = REPO_ROOT / "src"
for path in (REPO_ROOT, SRC_DIR, HERE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from analytics.distraction import distraction_rate_by_task, distraction_rate_per_hour
from analytics.focuscore import compute_weekly_focus_with_grade
from analytics.weekly_report import compute_weekly_summary, format_weekly_report_text
from core.focus_session import (
    start_custom_session,
    start_habit_session,
    start_task_session,
)
from core.habit import Habit, HabitManager
from core.task import Task, TaskManager
from planner.daily_plan import generate_daily_plan


# File locations for auto-loading user-provided tasks/habits.
DATA_DIR = Path(__file__).parent
TASKS_FILE = DATA_DIR / "tasks.json"
HABITS_FILE = DATA_DIR / "habits.json"


def print_section(title: str, lines: Iterable[str], log: List[str] | None = None) -> None:
    header = f"\n--- {title} ---"
    print(header)
    if log is not None:
        log.append(header)
    for line in lines:
        print(line)
        if log is not None:
            log.append(line)


def shift_session(session, days: int):
    """Return a shallow copy of a session shifted by N days for demo analytics."""
    if getattr(session, "task", None):
        clone = start_task_session(session.task)
    elif getattr(session, "habit", None):
        clone = start_habit_session(session.habit, auto_checkin=True)
    elif getattr(session, "kind", None) == "custom":
        clone = start_custom_session(session.label)
    else:
        clone = start_custom_session(getattr(session, "label", "Custom"))
    clone.label = session.label
    clone.kind = session.kind
    clone.start_time = session.start_time - timedelta(days=days)
    clone.end_time = session.end_time - timedelta(days=days)
    clone.distractions = session.distractions
    clone.focus_rating = session.focus_rating
    clone.notes = list(getattr(session, "notes", []))
    return clone


def summarize_timeline(sessions: list) -> None:
    """Print a simple chronological timeline to lengthen the demo narrative."""
    lines: List[str] = []
    for s in sorted(sessions, key=lambda x: x.start_time):
        start_str = s.start_time.strftime("%Y-%m-%d %H:%M")
        end_str = s.end_time.strftime("%H:%M") if s.end_time else "??"
        lines.append(f"- {start_str}-{end_str}: {s.label} ({s.kind})")
    print_section("Timeline (multi-day)", lines)


def summarize_stats(sessions: list) -> None:
    """Aggregate quick stats to discuss during the demo."""
    total_minutes = sum(filter(None, (s.duration_minutes() for s in sessions)))
    by_kind: dict[str, int] = {}
    for s in sessions:
        by_kind[s.kind] = by_kind.get(s.kind, 0) + 1
    lines = [
        f"Total sessions: {len(sessions)}",
        f"Total minutes: {total_minutes}",
        "Sessions by kind:",
    ]
    for kind, count in by_kind.items():
        lines.append(f"  - {kind}: {count}")
    print_section("Session stats", lines)


def load_tasks_from_file(path: Path = TASKS_FILE) -> list[Task]:
    """
    Load tasks from a JSON array of objects.
    Missing/invalid fields fall back to reasonable defaults.
    """
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - demo helper
        print(f"Could not load tasks from {path}: {exc}")
        return []

    if not isinstance(raw, list):
        print(f"Task file {path} must contain a JSON list.")
        return []

    tasks: list[Task] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        name = item.get("name")
        if not name:
            continue

        tasks.append(
            Task(
                name,
                item.get("duration", 25),
                category=item.get("category"),
                difficulty=item.get("difficulty", 3),
                priority=item.get("priority", 1),
                must_do_today=item.get("must_do_today", False),
                notes=item.get("notes", ""),
                pomodoro=bool(item.get("pomodoro", False)),
                planned_distractions=item.get("planned_distractions"),
            )
        )
    return tasks


def load_habits_from_file(path: Path = HABITS_FILE) -> list[Habit]:
    """Load habits from a JSON array of objects."""
    if not path.exists():
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - demo helper
        print(f"Could not load habits from {path}: {exc}")
        return []

    if not isinstance(raw, list):
        print(f"Habit file {path} must contain a JSON list.")
        return []

    habits: list[Habit] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        name = item.get("name")
        if not name:
            continue

        habits.append(Habit(name, frequency=item.get("frequency", "daily")))

    return habits


def prompt_str(prompt: str, default: str = "") -> str:
    """Input helper that falls back to default in non-interactive environments."""
    try:
        text = input(prompt).strip()
        return text or default
    except (OSError, EOFError):
        return default


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Ask a yes/no question with a default."""
    default_char = "y" if default else "n"
    resp = prompt_str(f"{prompt} (y/N): ", default_char).lower()
    # Reject numeric inputs explicitly for clarity.
    if resp.isdigit():
        print("Please enter y or n.")
        return default
    return resp.startswith("y")


def prompt_int(prompt: str, default: int = 0, minimum: int | None = None) -> int:
    """Parse an integer with defaults and an optional lower bound."""
    raw = prompt_str(prompt, str(default))
    try:
        value = int(raw)
    except ValueError:
        value = default
    if minimum is not None:
        value = max(minimum, value)
    return value


def prompt_category() -> str | None:
    """Let the user pick a category from a small menu or type one."""
    options = ["study", "admin", "recovery", "personal", "health", "work"]
    print("Categories:")
    for idx, opt in enumerate(options, start=1):
        print(f"  {idx}. {opt}")
    choice = prompt_str("Pick category number or type custom (Enter to skip): ")
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
    if choice:
        return choice
    return None


def prompt_tasks_from_user() -> list[Task]:
    """
    Ask the user to enter tasks interactively.
    First asks how many tasks to add.
    """
    if not prompt_yes_no("\nDo you want to add tasks now?", default=True):
        return []

    print("Enter tasks")
    count = prompt_int("How many tasks do you want to add? (0 to skip): ", 0, minimum=0)
    if count <= 0:
        return []

    tasks: list[Task] = []
    for idx in range(1, count + 1):
        print(f"\nTask {idx} of {count}")
        name = prompt_str("Task name: ")
        if not name:
            print("Skipped empty task name.")
            continue

        duration = prompt_int("Duration minutes (default 25): ", 25, minimum=1)
        category = prompt_category()
        difficulty = prompt_int("Difficulty 1-5 (default 3): ", 3, minimum=1)
        priority = prompt_int("Priority (default 1): ", 1, minimum=1)
        pomodoro = False
        planned_distractions = None
        if category == "study":
            pomodoro = prompt_yes_no("Use Pomodoro (25/5)?", default=False)

        tasks.append(
            Task(
                name,
                duration,
                category=category,
                difficulty=difficulty,
                priority=priority,
                pomodoro=pomodoro,
                planned_distractions=planned_distractions,
                notes="pomodoro" if pomodoro else "",
            )
        )
        print("Added task.\n")
    return tasks


def enforce_pomodoro_study_only(tasks: list[Task]) -> list[Task]:
    """
    Ensure Pomodoro is only applied to study-category tasks.
    Non-study tasks get pomodoro turned off but keep their distractions/notes.
    """
    for t in tasks:
        if getattr(t, "category", None) != "study":
            t.pomodoro = False
            # Leave planned_distractions as-is; user may still track them.
    return tasks


def prompt_habits_from_user() -> list[Habit]:
    """
    Ask the user to enter habits interactively.
    Stops when the user submits a blank habit name.
    """
    print("\nEnter habits (leave name empty to stop):")
    habits: list[Habit] = []
    while True:
        name = prompt_str("Habit name: ")
        if not name:
            break
        freq = prompt_str("Frequency (default daily): ", "daily") or "daily"
        habits.append(Habit(name, frequency=freq))
        print("Added habit.\n")
    return habits


def prompt_distractions_for_sessions(sessions) -> None:
    """
    Let the user override distraction counts for each session.
    Falls back to existing defaults if input is unavailable.
    """
    if not sessions:
        return

    print("\nDistractions per session (press Enter to keep defaults):")
    for session in sessions:
        default_val = session.distractions
        resp = prompt_str(
            f"- {session.label}: ",
            str(default_val),
        )
        try:
            session.distractions = max(0, int(resp))
        except ValueError:
            session.distractions = default_val


def summarize_inputs(tasks: list[Task], habits: list[Habit]) -> None:
    """Print a concise recap of tasks/habits before planning."""
    lines: List[str] = []
    if tasks:
        for t in tasks:
            flags = []
            if getattr(t, "completed", False):
                flags.append("completed")
            if getattr(t, "pomodoro", False):
                flags.append("pomodoro")
            flag_text = f" ({', '.join(flags)})" if flags else ""
            lines.append(f"- {t.name}: {t.duration} min, cat={t.category or 'n/a'}{flag_text}")
    else:
        lines.append("No tasks provided.")

    if habits:
        for h in habits:
            lines.append(f"- Habit: {h.name} ({getattr(h, 'frequency', 'daily')})")
    else:
        lines.append("No habits provided.")

    print_section("Inputs recap", lines)


def review_existing_tasks(tasks: list[Task], log: List[str], auto_skip: bool, quiet: bool) -> Tuple[list[Task], List[str]]:
    """Walk the user through optionally clearing finished tasks before planning."""
    reasons_log: List[str] = []
    if not tasks or auto_skip:
        return tasks, reasons_log
    if not prompt_yes_no("Review previous tasks before planning?", default=True):
        return tasks, reasons_log

    remaining = list(tasks)
    while True:
        print("\nExisting tasks:")
        for idx, t in enumerate(remaining, start=1):
            print(f"  {idx}. {t.name} ({t.duration} min, cat={t.category or 'n/a'})")
        choice = prompt_str("Enter a task number to review (blank to continue): ")
        if not choice:
            break
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        idx = int(choice) - 1
        if not (0 <= idx < len(remaining)):
            print("Out of range.")
            continue
        task = remaining[idx]
        if not prompt_yes_no(f"Did you finish '{task.name}'?", default=False):
            continue
        if not prompt_yes_no(f"Remove '{task.name}' from today's plan?", default=True):
            continue

        reasons = [
            "Task is finished",
            "Higher-priority tasks today",
            "Rescheduling to another day",
        ]
        print("Why remove it?")
        for i, r in enumerate(reasons, start=1):
            print(f"  {i}. {r}")
        sel = prompt_str("Select a reason (1-3, optional): ", "")
        reason_text = None
        if sel.isdigit() and 1 <= int(sel) <= len(reasons):
            reason_text = reasons[int(sel) - 1]
        if reason_text:
            msg = f"Removed '{task.name}' ({reason_text})"
            reasons_log.append(msg)
            if not quiet:
                print(msg)
        del remaining[idx]
    return remaining, reasons_log


def build_sample_sessions(tasks: list[Task], habit: Habit):
    """Create focus sessions for every task plus a habit session."""
    now = datetime.now()
    sessions = []

    base_start = now - timedelta(hours=len(tasks))

    for idx, task in enumerate(tasks):
        session = start_task_session(task)
        session.start_time = base_start + timedelta(minutes=idx * 45)
        duration = max(10, min(task.duration, 90))
        session.end_time = session.start_time + timedelta(minutes=duration)

        if getattr(task, "pomodoro", False):
            session.notes.append("Pomodoro")

        # Use user-planned distractions when supplied; otherwise demo defaults.
        if task.planned_distractions is not None:
            session.distractions = task.planned_distractions
            session.rate_focus(5 if session.distractions == 0 else 4)
        else:
            if idx == 0:
                session.record_distraction()
                session.record_distraction()
                session.rate_focus(4)
            elif idx == 1:
                session.record_distraction()
                session.rate_focus(3)
            else:
                session.rate_focus(5)

        sessions.append(session)

    # Habit session that auto-checks in
    session_habit = start_habit_session(habit, auto_checkin=True)
    session_habit.start_time = now - timedelta(minutes=20)
    session_habit.end_session()
    session_habit.rate_focus(5)
    sessions.append(session_habit)

    return sessions


def show_plan(tasks: list[Task]) -> None:
    lines: List[str] = []
    use_pomodoro = any(getattr(t, "pomodoro", False) for t in tasks)
    if use_pomodoro:
        lines.append("Using Pomodoro scheduling for tasks marked Pomodoro.")
    blocks = generate_daily_plan(
        tasks,
        mode="study",
        start="09:00",
        end="12:00",
        prefer_pomodoro=True,
    )
    for block in blocks:
        lines.append(f"- {block}")
    if not blocks:
        lines.append("No schedulable tasks.")
    print_section("Daily plan (study mode)", lines)


def show_alternate_plans(tasks: list[Task]) -> None:
    """Show additional planner modes to demonstrate flexibility."""
    energy_lines: List[str] = ["Energy plan (energy level = 2):"]
    energy_blocks = generate_daily_plan(
        tasks,
        mode="energy",
        energy_level=2,
        start="13:00",
        end="15:00",
        prefer_pomodoro=False,
    )
    if energy_blocks:
        for block in energy_blocks:
            energy_lines.append(f"- {block}")
    else:
        energy_lines.append("No schedulable tasks.")

    balanced_lines: List[str] = ["Balanced plan (recovery interleave):"]
    balanced_blocks = generate_daily_plan(
        tasks,
        mode="balanced",
        start="15:30",
        end="17:00",
        prefer_pomodoro=True,
    )
    if balanced_blocks:
        for block in balanced_blocks:
            balanced_lines.append(f"- {block}")
    else:
        balanced_lines.append("No schedulable tasks.")

    print_section("Additional plans", energy_lines + [""] + balanced_lines)


def show_analytics(sessions, habits):
    week_start = date.today() - timedelta(days=date.today().weekday())

    summary = compute_weekly_summary(sessions, habits, week_start=week_start)
    score, grade = compute_weekly_focus_with_grade(
        sessions, habits, week_start=week_start
    )

    drate = distraction_rate_per_hour(sessions)
    lines: List[str] = [
        f"Focus score: {score:.1f} ({grade})",
        f"Distractions per hour: {drate:.2f}" if drate is not None else "Distractions per hour: n/a",
    ]

    by_task = distraction_rate_by_task(sessions)
    if by_task:
        lines.append("Distractions per hour by task:")
        for name, rate in by_task.items():
            lines.append(f"  - {name}: {rate:.2f}")

    lines.append("Weekly report:")
    lines.append(format_weekly_report_text(summary))
    print_section("Analytics", lines)


def main():
    parser = argparse.ArgumentParser(description="Focus Pro interactive demo")
    parser.add_argument("--auto", action="store_true", help="Skip prompts and use defaults")
    parser.add_argument("--fast", action="store_true", help="Skip prompts, defaults, minimal sections")
    parser.add_argument("--verbose", action="store_true", help="Show extra planning context")
    parser.add_argument("--quiet", action="store_true", help="Suppress chit-chat during review/removal")
    parser.add_argument("--export", metavar="PATH", help="Export all sections to a text file")
    parser.add_argument("--no-timeline", action="store_true", help="Hide timeline and session stats sections")
    parser.add_argument("--days", type=int, default=1, help="Duplicate sessions across N days for richer analytics (default 1)")
    args = parser.parse_args()

    log: List[str] = []

    print("\n=== Focus Pro Demo ===")
    intro_msg = "Before we start, we'll review previous tasks and optionally remove finished ones."
    print(intro_msg)
    log.append(intro_msg)
    if args.auto or args.fast:
        # No prompts; defaults only
        tasks = [
            Task("Study MDS", 90, category="study", difficulty=4, priority=2),
            Task("Email admin", 20, category="admin", difficulty=1),
            Task("Stretch break", 10, category="recovery", difficulty=1),
            Task("Review research notes", 45, category="study", difficulty=3),
        ]
    else:
        tasks = load_tasks_from_file()
        if not tasks:
            tasks = prompt_tasks_from_user()
        if not tasks:
            tasks = [
                Task("Study MDS", 90, category="study", difficulty=4, priority=2),
                Task("Email admin", 20, category="admin", difficulty=1),
                Task("Stretch break", 10, category="recovery", difficulty=1),
                Task("Review research notes", 45, category="study", difficulty=3),
            ]
    tasks = enforce_pomodoro_study_only(tasks)

    # Always offer review unless fast/auto
    tasks, removal_log = review_existing_tasks(tasks, log, auto_skip=(args.auto or args.fast), quiet=args.quiet)
    if removal_log:
        print_section("Removed tasks", removal_log, log)
    active_tasks = [t for t in tasks if not t.completed]
    skipped_completed = len(tasks) - len(active_tasks)
    if skipped_completed:
        print(f"\nSkipping {skipped_completed} task(s) marked completed.")

    task_manager = TaskManager()
    for t in active_tasks:
        task_manager.add_task(t)

    # Habit and habit manager (prefers habits.json; otherwise asks user)
    habit_manager = HabitManager()
    habits = load_habits_from_file()
    if not habits:
        habits = prompt_habits_from_user()
    if habits:
        for h in habits:
            habit_manager.add_habit(h)
    else:
        habit_manager.add_habit(Habit("Hydrate regularly", frequency="daily"))

    habit = habit_manager.list_habits()[0]

    summarize_inputs(task_manager.list_tasks(), habit_manager.list_habits())

    show_plan(task_manager.list_tasks())
    show_alternate_plans(task_manager.list_tasks())

    sessions = build_sample_sessions(task_manager.list_tasks(), habit)
    if not (args.auto or args.fast) and prompt_yes_no("Do you want to enter distractions now?", default=True):
        prompt_distractions_for_sessions(sessions)

    # Add one custom session to demonstrate the custom label flow.
    custom = start_custom_session("Strategy review")
    custom.start_time = datetime.now() - timedelta(minutes=35)
    custom.end_time = datetime.now()
    custom.distractions = 1
    custom.rate_focus(4)
    sessions.append(custom)

    # Optionally create additional days to enrich analytics for demo.
    combined_sessions = list(sessions)
    if args.days > 1:
        for offset in range(1, args.days):
            combined_sessions.extend(shift_session(s, days=offset) for s in sessions)

    session_lines: List[str] = []
    for s in combined_sessions:
        summary = s.summary()
        session_lines.append(
            f"- {summary['label']} ({summary['kind']}): "
            f"{summary.get('duration_minutes')} min, "
            f"distractions={summary.get('distractions')}, "
            f"rating={summary.get('rating')}"
        )
    print_section("Focus sessions", session_lines, log)

    if not args.no_timeline:
        summarize_timeline(combined_sessions)
        summarize_stats(combined_sessions)

    show_analytics(combined_sessions, habit_manager.list_habits())

    if args.export:
        Path(args.export).write_text("\n".join(log), encoding="utf-8")
        if not args.quiet:
            print(f"\nExported demo output to {args.export}")

    if not args.fast:
        print("\nDemo complete.\n")


if __name__ == "__main__":
    main()
