"""Multipliers for project types and complexity levels."""

from typing import Optional

from ossval.models import ComplexityLevel, GitHistoryMetrics, HalsteadMetrics, ProjectType

# Project type multipliers (salary and effort)
# Effort multiplier = sqrt(salary multiplier) - expertise affects salary more than raw effort
PROJECT_TYPE_MULTIPLIERS: dict[ProjectType, dict[str, float]] = {
    ProjectType.SCRIPT: {"salary": 0.7, "effort": 0.84},
    ProjectType.LIBRARY: {"salary": 1.0, "effort": 1.0},
    ProjectType.FRAMEWORK: {"salary": 1.15, "effort": 1.07},
    ProjectType.COMPILER: {"salary": 1.5, "effort": 1.22},
    ProjectType.DATABASE: {"salary": 1.4, "effort": 1.18},
    ProjectType.OPERATING_SYSTEM: {"salary": 1.5, "effort": 1.22},
    ProjectType.CRYPTOGRAPHY: {"salary": 1.6, "effort": 1.26},
    ProjectType.MACHINE_LEARNING: {"salary": 1.4, "effort": 1.18},
    ProjectType.NETWORKING: {"salary": 1.2, "effort": 1.10},
    ProjectType.EMBEDDED: {"salary": 1.25, "effort": 1.12},
    ProjectType.GRAPHICS: {"salary": 1.3, "effort": 1.14},
    ProjectType.SCIENTIFIC: {"salary": 1.2, "effort": 1.10},
    ProjectType.DEVTOOLS: {"salary": 1.1, "effort": 1.05},
}

# Complexity multipliers based on cyclomatic complexity
COMPLEXITY_MULTIPLIERS: dict[ComplexityLevel, float] = {
    ComplexityLevel.TRIVIAL: 0.7,
    ComplexityLevel.SIMPLE: 0.9,
    ComplexityLevel.MODERATE: 1.0,
    ComplexityLevel.COMPLEX: 1.3,
    ComplexityLevel.VERY_COMPLEX: 1.7,
}


def get_project_type_multiplier(project_type: ProjectType, multiplier_type: str = "effort") -> float:
    """Get multiplier for a project type."""
    multipliers = PROJECT_TYPE_MULTIPLIERS.get(project_type, PROJECT_TYPE_MULTIPLIERS[ProjectType.LIBRARY])
    return multipliers.get(multiplier_type, 1.0)


def get_complexity_multiplier(complexity_level: ComplexityLevel) -> float:
    """Get multiplier for a complexity level."""
    return COMPLEXITY_MULTIPLIERS.get(complexity_level, 1.0)


def get_maturity_multiplier(git_history: Optional[GitHistoryMetrics]) -> float:
    """
    Calculate maturity multiplier based on git history.

    Projects with long history, many commits, and many contributors
    are more complex to maintain and understand.

    Args:
        git_history: Git history metrics

    Returns:
        Multiplier between 1.0 and 2.5
    """
    if not git_history:
        return 1.0

    multiplier = 1.0

    # Age multiplier (mature projects are more complex)
    # 0-1 year: 1.0x
    # 1-3 years: 1.1x
    # 3-5 years: 1.2x
    # 5-10 years: 1.4x
    # 10+ years: 1.6x
    if git_history.age_years >= 10:
        multiplier += 0.6
    elif git_history.age_years >= 5:
        multiplier += 0.4
    elif git_history.age_years >= 3:
        multiplier += 0.2
    elif git_history.age_years >= 1:
        multiplier += 0.1

    # Contributor count multiplier (more contributors = more complexity)
    # 1-5: 1.0x
    # 6-20: 1.1x
    # 21-50: 1.2x
    # 51-100: 1.3x
    # 100+: 1.5x
    if git_history.contributor_count >= 100:
        multiplier += 0.5
    elif git_history.contributor_count >= 51:
        multiplier += 0.3
    elif git_history.contributor_count >= 21:
        multiplier += 0.2
    elif git_history.contributor_count >= 6:
        multiplier += 0.1

    # Commit count multiplier (many commits = evolved complexity)
    # <1000: 1.0x
    # 1000-5000: 1.1x
    # 5000-10000: 1.15x
    # 10000-20000: 1.2x
    # 20000+: 1.3x
    if git_history.commit_count >= 20000:
        multiplier += 0.3
    elif git_history.commit_count >= 10000:
        multiplier += 0.2
    elif git_history.commit_count >= 5000:
        multiplier += 0.15
    elif git_history.commit_count >= 1000:
        multiplier += 0.1

    # Cap at 2.5x for very mature/large projects
    return min(multiplier, 2.5)


def get_halstead_multiplier(halstead: Optional[HalsteadMetrics]) -> float:
    """
    Calculate complexity multiplier based on Halstead metrics.

    Higher difficulty and effort indicate more complex code.

    Args:
        halstead: Halstead metrics

    Returns:
        Multiplier between 0.8 and 1.8
    """
    if not halstead:
        return 1.0

    # Use difficulty as primary indicator
    # Low difficulty (< 10): 0.8-0.9x
    # Medium difficulty (10-20): 1.0x
    # High difficulty (20-40): 1.2-1.4x
    # Very high difficulty (> 40): 1.5-1.8x

    if halstead.difficulty < 10:
        return 0.8 + (halstead.difficulty / 100)
    elif halstead.difficulty < 20:
        return 0.9 + (halstead.difficulty - 10) / 100
    elif halstead.difficulty < 40:
        return 1.0 + (halstead.difficulty - 20) / 50
    else:
        return min(1.5 + (halstead.difficulty - 40) / 100, 1.8)

