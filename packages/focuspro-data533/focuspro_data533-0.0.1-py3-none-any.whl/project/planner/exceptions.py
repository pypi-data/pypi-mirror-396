"""Custom exceptions for the planner subpackage."""


class PlannerConfigurationError(ValueError):
    """Raised when planner configuration or inputs are invalid."""

    pass


class SchedulingWindowError(PlannerConfigurationError):
    """Raised when an invalid scheduling window is provided."""

    pass
