from __future__ import annotations

from datetime import date, timedelta
import sys
from pathlib import Path
from typing import Any, Dict, List

# Allow running this module directly (python weekly_report.py) by adding repo root to sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.core.focus_session import FocusSession
from project.core.habit import Habit
from project.analytics.exceptions import ReportExportError


def filter_sessions_for_week(
    sessions: List[FocusSession],
    week_start: date,
) -> List[FocusSession]:
    
    week_end_exclusive = week_start + timedelta(days=7)

    result: List[FocusSession] = []
    for s in sessions:
        try:
            start_day = s.start_time.date()
        except Exception:
            continue
        if week_start <= start_day < week_end_exclusive:
            result.append(s)
    return result


def _habit_completion_rate_for_week(
    habits: List[Habit],
    week_start: date,
) -> float:
    
    if not habits:
        return 0.0

    week_end_inclusive = week_start + timedelta(days=6)
    completed = 0
    considered = 0

    for h in habits:
        try:
            last = h.last_completed
        except Exception:
            continue

        # None or invalid dates are treated as incomplete but counted
        if last is None:
            considered += 1
            continue

        try:
            in_range = week_start <= last <= week_end_inclusive
        except Exception:
            considered += 1
            continue

        considered += 1
        if in_range:
            completed += 1
    return completed / considered if considered else 0.0


def compute_weekly_summary(
    sessions: List[FocusSession],
    habits: List[Habit],
    week_start: date,
) -> Dict[str, Any]:

    week_sessions = filter_sessions_for_week(sessions, week_start)

    total_focus_minutes = 0
    total_distractions = 0

    for s in week_sessions:
        try:
            duration = s.duration_minutes()
            distractions = int(getattr(s, "distractions", 0))
        except (AttributeError, TypeError, ValueError):
            continue
        except Exception:
            continue

        if duration is not None:
            total_focus_minutes += duration
        total_distractions += distractions

    num_sessions = len(week_sessions)
    if num_sessions > 0:
        average_session_length = total_focus_minutes / num_sessions
    else:
        average_session_length = 0.0

    habit_completion_rate = _habit_completion_rate_for_week(habits, week_start)

    # Top habits by streak (simple heuristic)
    try:
        sorted_habits = sorted(
            habits,
            key=lambda h: getattr(h, "streak", 0),
            reverse=True,
        )
    except Exception:
        sorted_habits = []
    top_habits = [getattr(h, "name", "Habit") for h in sorted_habits[:3]]

    summary: Dict[str, Any] = {
        "week_start": week_start,
        "week_end": week_start + timedelta(days=6),
        "total_focus_minutes": total_focus_minutes,
        "num_sessions": num_sessions,
        "average_session_length": average_session_length,
        "total_distractions": total_distractions,
        "habit_completion_rate": habit_completion_rate,
        "top_habits": top_habits,
    }

    return summary


def format_weekly_report_text(summary: Dict[str, Any]) -> str:
    week_start = summary.get("week_start")
    week_end = summary.get("week_end")

    lines = [
        f"Weekly Report ({week_start} -> {week_end})",
        "-" * 40,
        f"Total focus minutes   : {summary.get('total_focus_minutes', 0)}",
        f"Number of sessions    : {summary.get('num_sessions', 0)}",
        f"Avg session length    : {summary.get('average_session_length', 0):.1f} min",
        f"Total distractions    : {summary.get('total_distractions', 0)}",
        f"Habit completion rate : {summary.get('habit_completion_rate', 0.0) * 100:.1f} %",
        "",
        "Top habits (by streak):",
    ]

    top_habits = summary.get("top_habits", []) or []
    if not top_habits:
        lines.append("  (no habits tracked)")
    else:
        for name in top_habits:
            lines.append(f"  - {name}")

    return "\n".join(lines)


def export_weekly_report_markdown(
    summary: Dict[str, Any],
    filename: str,
) -> None:
    text = format_weekly_report_text(summary)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Simple markdown wrapper
            f.write("# Weekly Focus Report\n\n")
            f.write("```\n")
            f.write(text)
            f.write("\n```\n")
    except Exception as exc:
        raise ReportExportError(f"Failed to export weekly report to {filename}") from exc
