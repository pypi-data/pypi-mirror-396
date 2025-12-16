

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol

try:
    from core.task import Task
except ImportError:  # Allow use when planner is imported as src.project.planner.*
    from ..core.task import Task


class SupportsDeadline(Protocol):
    deadline: date | None


class SupportsDifficulty(Protocol):
    difficulty: int | None


class PriorityStrategy(ABC):
   
    @abstractmethod
    def score(self, task: Task) -> float:
        raise NotImplementedError


class SimplePriority(PriorityStrategy):
    

    def score(self, task: Task) -> float:
        try:
            duration = float(getattr(task, "duration", 0) or 0)  # minutes
        except (TypeError, ValueError):
            duration = 0
        except Exception:
            duration = 0
        try:
            base_priority = float(getattr(task, "priority", 1) or 1)
        except (TypeError, ValueError):
            base_priority = 1
        except Exception:
            base_priority = 1

        # Shorter tasks get slightly higher score (less penalty)
        duration_hours = duration / 60
        duration_penalty = 0.2 * duration_hours

        return float(base_priority) - duration_penalty


class DeadlinePriority(PriorityStrategy):
    

    def score(self, task: Task) -> float:
        today = date.today()

        # 1) Urgency based on time until deadline
        deadline = getattr(task, "deadline", None)
        if deadline is not None:
            try:
                days_left = (deadline - today).days
            except Exception:
                days_left = 0
            if days_left < 0:
                # Overdue work should jump to the front of the queue.
                urgency = 2.0 + abs(days_left)
            else:
                # Nearer deadlines score higher; tomorrow should be lower than today.
                urgency = 1.0 / (days_left + 1)
        else:
            urgency = 0.0

        # 2) Difficulty (default 3 on a 1-5 scale)
        try:
            difficulty = int(getattr(task, "difficulty", 3) or 3)
        except (TypeError, ValueError):
            difficulty = 3
        except Exception:
            difficulty = 3

        # 3) Importance from category
        category = getattr(task, "category", None)
        category_weights = {
            "study": 3.0,
            "admin": 1.0,
            "recovery": 2.0,
            "other": 1.0,
            None: 1.0,
        }
        importance = category_weights.get(category, 1.0)

        # 4) Duration penalty (long tasks are slightly harder to fit)
        try:
            duration = float(getattr(task, "duration", 0) or 0)
        except (TypeError, ValueError):
            duration = 0
        except Exception:
            duration = 0
        duration_hours = duration / 60.0
        duration_penalty = 0.3 * duration_hours

        score = (
            4.0 * urgency
            + 3.0 * importance
            + 2.0 * difficulty
            - duration_penalty
        )

        # Optional bump if the task is explicitly marked as must-do-today
        if getattr(task, "must_do_today", False):
            score += 10.0

        return float(score)


class EnergyAwarePriority(PriorityStrategy):
   

    def __init__(self, energy_level: int = 3) -> None:
        self.energy_level = max(1, min(5, energy_level))

    def score(self, task: Task) -> float:
        try:
            difficulty = int(getattr(task, "difficulty", 3) or 3)
        except (TypeError, ValueError):
            difficulty = 3
        except Exception:
            difficulty = 3
        difficulty = max(1, min(5, difficulty))

        # Compatibility: smaller difference -> better match
        diff = abs(difficulty - self.energy_level)
        compatibility = max(0.0, 5.0 - diff)  # 0 to 5

        # Slight emphasis on tasks with deadlines
        today = date.today()
        deadline = getattr(task, "deadline", None)
        urgency = 0.0
        if deadline is not None:
            try:
                days_left = (deadline - today).days
                urgency = 1.0 / max(days_left, 1)
            except Exception:
                urgency = 0.0

        # Combine compatibility and urgency
        score = 2.5 * compatibility + 3.0 * urgency

        return float(score)
