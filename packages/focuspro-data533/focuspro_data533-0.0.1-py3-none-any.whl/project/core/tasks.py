from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class Task:
    """
    Represents a single task with minimal scheduling metadata.
    """

    name: str
    duration: int  # minutes
    category: Optional[str] = None
    deadline: Optional[date] = None
    difficulty: int = 3  # 1-5
    priority: int = 1
    must_do_today: bool = False
    notes: str = ""
    pomodoro: bool = False
    planned_distractions: Optional[int] = None
    completed: bool = False

    def __post_init__(self) -> None:
        # Normalize numeric fields and keep them in sensible bounds.
        try:
            self.duration = max(0, int(self.duration))
        except Exception:
            self.duration = 0

        try:
            diff = int(self.difficulty)
        except Exception:
            diff = 3
        self.difficulty = max(1, min(5, diff))

        try:
            self.priority = int(self.priority)
        except Exception:
            self.priority = 1

        try:
            self.pomodoro = bool(self.pomodoro)
        except Exception:
            self.pomodoro = False

        # planned_distractions may be None or an int >= 0
        if self.planned_distractions is not None:
            try:
                self.planned_distractions = max(0, int(self.planned_distractions))
            except Exception:
                self.planned_distractions = None

    def mark_complete(self) -> None:
        """Mark the task as done."""
        self.completed = True

    def summary(self) -> str:
        """Compact human-readable summary."""
        cat = self.category or "general"
        return f"{self.name} ({self.duration} min, {cat})"


class TaskManager:
    """
    Lightweight container for Task objects.
    """

    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Store a task."""
        self.tasks.append(task)

    def list_tasks(self) -> List[Task]:
        """Return all tasks in insertion order."""
        return list(self.tasks)

    def remove_task(self, name: str) -> bool:
        """Remove first task matching the given name."""
        for idx, task in enumerate(self.tasks):
            try:
                match = task.name == name
            except Exception:
                match = False
            if match:
                del self.tasks[idx]
                return True
        return False

    def next_task(self) -> Optional[Task]:
        """Return the first task, if any."""
        return self.tasks[0] if self.tasks else None


__all__ = ["Task", "TaskManager"]
