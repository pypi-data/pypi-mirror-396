from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Sequence

try:
    from core.task import Task
except ImportError:  # Allow use when planner is imported as src.project.planner.*
    from ..core.task import Task

# Type-checking import only to avoid runtime circular dependency.
if TYPE_CHECKING:
    from .base_planner import PlannedBlock

# NOTE: We import PlannedBlock lazily inside methods to avoid circular imports
# with base_planner.py (which also imports Scheduler).


class Scheduler(ABC):

    @abstractmethod
    def schedule(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List["PlannedBlock"]:
       
        raise NotImplementedError


class SequentialScheduler(Scheduler):
  

    def schedule(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List["PlannedBlock"]:
        from .base_planner import PlannedBlock  # lazy import

        blocks: List[PlannedBlock] = []
        current_start = day_start

        for task in tasks:
            try:
                duration_minutes = int(getattr(task, "duration", 0) or 0)
            except (TypeError, ValueError):
                continue  # skip tasks with non-numeric durations
            except Exception:
                continue
            if duration_minutes <= 0:
                continue  # skip zero-length tasks

            block_duration = timedelta(minutes=duration_minutes)
            block_end = current_start + block_duration

            if block_end > day_end:
                # No more room in the schedule
                break

            blocks.append(PlannedBlock(task=task, start=current_start, end=block_end))
            current_start = block_end

        return blocks


class PomodoroScheduler(Scheduler):


    def __init__(
        self,
        work_minutes: int = 25,
        break_minutes: int = 5,
    ) -> None:
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes

    def schedule(
        self,
        tasks: Sequence[Task],
        day_start: datetime,
        day_end: datetime,
    ) -> List["PlannedBlock"]:
        from .base_planner import PlannedBlock  # lazy import

        blocks: List[PlannedBlock] = []
        current_start = day_start

        work_delta = timedelta(minutes=self.work_minutes)
        break_delta = timedelta(minutes=self.break_minutes)

        for task in tasks:
            try:
                remaining_minutes = int(getattr(task, "duration", 0) or 0)
            except (TypeError, ValueError):
                continue
            except Exception:
                continue
            if remaining_minutes <= 0:
                continue

            while remaining_minutes > 0:
                block_end = current_start + work_delta
                if block_end > day_end:
                    return blocks 

                # Creating a work block
                blocks.append(
                    PlannedBlock(task=task, start=current_start, end=block_end)
                )

                remaining_minutes -= self.work_minutes
                current_start = block_end

               
                if remaining_minutes > 0:
                    break_end = current_start + break_delta
                    if break_end > day_end:
                        return blocks
                    current_start = break_end

        return blocks
