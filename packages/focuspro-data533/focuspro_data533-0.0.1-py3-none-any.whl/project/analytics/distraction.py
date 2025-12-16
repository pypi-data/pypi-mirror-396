from __future__ import annotations

from datetime import date
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.core.focus_session import FocusSession


def total_distractions(sessions: List[FocusSession]) -> int:
    total = 0
    for s in sessions:
        try:
            total += int(getattr(s, "distractions", 0))
        except (TypeError, AttributeError, ValueError):
            # Skip sessions with unusable distraction data.
            continue
        except Exception:
            continue
    return total


def distraction_rate_per_hour(
    sessions: List[FocusSession],
) -> Optional[float]:
    total_minutes = 0
    total = 0

    for s in sessions:
        try:
            duration = s.duration_minutes()
            distractions = int(getattr(s, "distractions", 0))
        except (AttributeError, TypeError, ValueError):
            continue
        except Exception:
            continue

        if duration is not None and duration > 0:
            total_minutes += duration
            total += distractions

    if total_minutes == 0:
        return None

    hours = total_minutes / 60.0
    return total / hours


def distractions_by_day(
    sessions: List[FocusSession],
) -> Dict[date, int]:
    
    result: Dict[date, int] = {}

    for s in sessions:
        try:
            day = s.start_time.date()
            distractions = int(getattr(s, "distractions", 0))
        except (AttributeError, TypeError, ValueError):
            continue
        except Exception:
            continue
        result[day] = result.get(day, 0) + distractions

    return result


def distraction_rate_by_task(
    sessions: List[FocusSession],
) -> Dict[str, float]:
   
    total_minutes_by_label: Dict[str, int] = {}
    total_distractions_by_label: Dict[str, int] = {}

    for s in sessions:
        try:
            if getattr(s, "task", None) is not None:
                label = getattr(s.task, "name", "Task")
            elif getattr(s, "habit", None) is not None:
                label = f"Habit: {getattr(s.habit, 'name', 'Habit')}"
            else:
                label = getattr(s, "label", "Session")

            duration = s.duration_minutes()
            distractions = int(getattr(s, "distractions", 0))
        except (AttributeError, TypeError, ValueError):
            continue
        except Exception:
            continue

        if duration is None or duration <= 0:
            continue

        total_minutes_by_label[label] = total_minutes_by_label.get(label, 0) + duration
        total_distractions_by_label[label] = (
            total_distractions_by_label.get(label, 0) + distractions
        )

    rates: Dict[str, float] = {}
    for label, minutes in total_minutes_by_label.items():
        hours = minutes / 60.0
        if hours <= 0:
            continue
        total = total_distractions_by_label.get(label, 0)
        rates[label] = total / hours

    return rates
