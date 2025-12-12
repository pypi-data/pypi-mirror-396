"""Data modules for salaries, multipliers, and project types."""

from ossval.data.multipliers import (
    COMPLEXITY_MULTIPLIERS,
    PROJECT_TYPE_MULTIPLIERS,
    get_complexity_multiplier,
    get_project_type_multiplier,
)
from ossval.data.project_types import detect_project_type
from ossval.data.salaries import (
    REGIONAL_SALARIES,
    get_monthly_rate,
    get_regional_salary,
)

__all__ = [
    "REGIONAL_SALARIES",
    "get_regional_salary",
    "get_monthly_rate",
    "PROJECT_TYPE_MULTIPLIERS",
    "COMPLEXITY_MULTIPLIERS",
    "get_project_type_multiplier",
    "get_complexity_multiplier",
    "detect_project_type",
]

