"""Custom exceptions for the core focus session domain."""


class InvalidSessionError(Exception):
    """Raised when a focus session is started with invalid parameters or state."""


class HabitError(Exception):
    """Raised when habit data cannot be processed safely."""
