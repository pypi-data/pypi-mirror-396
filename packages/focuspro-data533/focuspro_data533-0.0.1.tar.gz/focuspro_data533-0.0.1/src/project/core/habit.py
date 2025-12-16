from typing import Optional
from datetime import date, datetime, timedelta
from .exceptions import HabitError

class Habit:
    """
    Represents a recurring habit in FocusForge.
    Tracks name, frequency, streak, and last completion date.
    """

    def __init__(self, name: str, frequency: str = "daily",
                 streak: int = 0, last_completed: Optional[date] = None) -> None:
        self.name = name
        try:
            self.frequency = str(frequency).lower() if frequency else "daily"
        except Exception:
            self.frequency = "daily"

        try:
            self.streak = max(0, int(streak))
        except Exception:
            self.streak = 0

        # Only store valid date objects; otherwise default to None.
        self.last_completed = last_completed if isinstance(last_completed, date) else None

    def __repr__(self) -> str:
        return (
            f"Habit(name={self.name}, frequency={self.frequency}, "
            f"streak={self.streak}, last_completed={self.last_completed})"
        )

    def complete_today(self) -> None:
        """Mark the habit as completed today, updating streak."""
        try:
            today = date.today()
        except Exception as exc:
            raise HabitError("Failed to compute today's date") from exc

        if self.last_completed == today:
            print("Habit already completed today.")
            return

        try:
            if self.last_completed == today - timedelta(days=1):
                self.streak += 1
            else:
                self.streak = 1
        except Exception as exc:
            raise HabitError("Failed to update streak") from exc

        self.last_completed = today

    def reset_streak(self) -> None:
        """Reset habit streak."""
        self.streak = 0
        self.last_completed = None

    def is_due(self) -> bool:
        """
        Returns True if the habit is due today.
        Currently supports only 'daily' habits.
        """
        today = date.today()
        if self.frequency == "daily":
            return self.last_completed != today
        return False

def add_habit_from_input(default_name: str = "Sample Habit",
                         default_frq: str = "daily") -> Habit:
    """Create a Habit object from user input, with fallbacks for sandbox."""
    try:
        name = input(f"Habit name (default: {default_name}): ").strip()
        if not name:
            name = default_name
    except (OSError, TypeError, ValueError):
        name = default_name
    except Exception:
        name = default_name

    try:
        freq = input(f"Frequency (default: {default_frq}): ").strip().lower()
        if not freq:
            freq = default_frq
    except (OSError, TypeError, ValueError):
        freq = default_frq
    except Exception:
        freq = default_frq

    return Habit(name=name, frequency=freq)

def show_habit_menu(habits: list[Habit]) -> None:
    """Display a numbered list of habits."""
    if not habits:
        print("No habits available.")
        return

    print("\nAvailable Habits:")
    for idx, habit in enumerate(habits, start=1):
        status = "done" if not habit.is_due() else "due"
        print(f"{idx}. {habit.name} (Streak: {habit.streak}, Status: {status})")

def choose_habit(habits: list[Habit]) -> Optional[Habit]:
    """
    Let user pick a habit by number.
    Returns selected Habit or None.
    """
    if not habits:
        print("No habits to choose from.")
        return None

    show_habit_menu(habits)

    while True:
        try:
            choice = input("Select a habit by number (or 'q' to quit): ").strip()
        except (OSError, TypeError, ValueError):
            print("Input unavailable. Returning None.")
            return None
        except Exception:
            print("Unexpected input error. Returning None.")
            return None

        if choice.lower() == "q":
            return None

        if not choice.isdigit():
            print("Invalid input. Enter a number.")
            continue

        index = int(choice) - 1
        if 0 <= index < len(habits):
            return habits[index]

        print("Invalid selection. Try again.")

# --------------------------------------------------------------
#               HABIT MANAGER (NEW CLASS)
# --------------------------------------------------------------

class HabitManager:
    """
    Holds and manages all Habit objects.
    Handles adding, listing, and check-in.
    """

    def __init__(self) -> None:
        self.habits: list[Habit] = []

    def add_habit(self, habit: Habit) -> None:
        """Add a Habit to the internal list."""
        self.habits.append(habit)

    def add_habit_from_input(self) -> Habit:
        """Create a Habit through user input and add it."""
        habit = add_habit_from_input()
        self.habits.append(habit)
        return habit

    def list_habits(self) -> list[Habit]:
        """Return all habits."""
        return self.habits

    def checkin(self) -> None:
        """Choose a habit and check it in."""
        if not self.habits:
            print("No habits to check in.")
            return

        habit = choose_habit(self.habits)
        if habit is None:
            return

        habit.complete_today()
        print(f"Checked in: {habit.name}. New streak: {habit.streak}")

if __name__ == "__main__":  # pragma: no cover
    # Simple demo / manual test for the habit system
    manager = HabitManager()

    # Seed some example habits
    manager.add_habit(Habit("Morning prayer"))
    manager.add_habit(Habit("Study MDS"))
    manager.add_habit(Habit("Exercise"))
    manager.add_habit(Habit("Reading"))

    print("Welcome to FocusForge Habit Tracker\n")

    try:
        while True:
            print("\nWhat do you want to do?")
            print("1. Show habits")
            print("2. Add a new habit")
            print("3. Check in a habit")
            print("q. Quit")

            choice = input("Enter your choice: ").strip().lower()

            if choice == "1":
                show_habit_menu(manager.list_habits())

            elif choice == "2":
                manager.add_habit_from_input()

            elif choice == "3":
                manager.checkin()

            elif choice == "q":
                print("Goodbye.")
                break

            else:
                print("Invalid option. Please choose 1, 2, 3, or q.")

    except OSError:
        # For environments where input() is not available
        print("Input is not available in this environment. Demo finished.")
        print("Current habits:")
        show_habit_menu(manager.list_habits())
