"""Maintainability Index analyzer."""

import math
from typing import Optional

from ossval.models import (
    ComplexityMetrics,
    HalsteadMetrics,
    MaintainabilityMetrics,
    SLOCMetrics,
)


def calculate_maintainability_index(
    sloc: SLOCMetrics,
    halstead: Optional[HalsteadMetrics] = None,
    complexity: Optional[ComplexityMetrics] = None,
) -> Optional[MaintainabilityMetrics]:
    """
    Calculate Maintainability Index (MI).

    Microsoft's formula:
    MI = MAX(0, 171 - 5.2 × ln(HV) - 0.23 × CC - 16.2 × ln(LOC) + 50 × sin(sqrt(2.4 × CM)))

    Where:
    - HV = Halstead Volume
    - CC = Cyclomatic Complexity (average)
    - LOC = Lines of Code
    - CM = Comment Ratio (% of lines that are comments)

    Simplified formula (when Halstead not available):
    MI = 171 - 5.2 × ln(LOC) - 0.23 × CC - 16.2 × ln(LOC)

    Args:
        sloc: SLOC metrics
        halstead: Optional Halstead metrics
        complexity: Optional complexity metrics

    Returns:
        MaintainabilityMetrics if calculable, None otherwise
    """
    if not sloc or sloc.code_lines == 0:
        return None

    # Get base values
    loc = sloc.code_lines
    comment_lines = sloc.comment_lines
    total_lines = sloc.total

    # Calculate comment ratio
    comment_ratio = comment_lines / total_lines if total_lines > 0 else 0.0

    # Get cyclomatic complexity
    cyclomatic_avg = 10.0  # Default moderate complexity
    complexity_per_kloc = 10.0
    if complexity and complexity.cyclomatic_complexity_avg:
        cyclomatic_avg = complexity.cyclomatic_complexity_avg
        complexity_per_kloc = (cyclomatic_avg / loc) * 1000 if loc > 0 else 10.0

    # Calculate MI using available metrics
    try:
        if halstead and halstead.volume > 0:
            # Full formula with Halstead
            halstead_term = 5.2 * math.log(halstead.volume)
            complexity_term = 0.23 * cyclomatic_avg
            loc_term = 16.2 * math.log(loc)
            comment_term = 50 * math.sin(math.sqrt(2.4 * comment_ratio))

            mi = 171 - halstead_term - complexity_term - loc_term + comment_term
        else:
            # Simplified formula without Halstead
            # Use alternative formula: 171 - 5.2 × ln(V) - 0.23 × CC - 16.2 × ln(LOC)
            # Where V is estimated as LOC × 4.79 (empirical approximation)
            estimated_volume = loc * 4.79
            halstead_term = 5.2 * math.log(max(1, estimated_volume))
            complexity_term = 0.23 * cyclomatic_avg
            loc_term = 16.2 * math.log(max(1, loc))
            comment_term = 50 * math.sin(math.sqrt(2.4 * comment_ratio))

            mi = 171 - halstead_term - complexity_term - loc_term + comment_term

        # Normalize to 0-100 range
        mi = max(0, min(100, mi))

        # Classify maintainability level
        if mi >= 20:
            level = "High"  # Green: highly maintainable
        elif mi >= 10:
            level = "Medium"  # Yellow: moderately maintainable
        else:
            level = "Low"  # Red: difficult to maintain

        return MaintainabilityMetrics(
            maintainability_index=mi,
            maintainability_level=level,
            comment_ratio=comment_ratio,
            avg_complexity_per_kloc=complexity_per_kloc,
        )

    except (ValueError, ZeroDivisionError):
        return None
