"""Cyclomatic complexity analysis."""

from typing import Optional

from radon.complexity import cc_visit
from radon.raw import analyze

from ossval.models import ComplexityLevel, ComplexityMetrics


def analyze_complexity(
    code: str, language: str = "python"
) -> Optional[ComplexityMetrics]:
    """
    Analyze cyclomatic complexity of code.

    Args:
        code: Source code to analyze
        language: Programming language (currently only Python supported)

    Returns:
        ComplexityMetrics if successful, None otherwise
    """
    if language.lower() != "python":
        # For non-Python, return default moderate complexity
        return ComplexityMetrics(complexity_level=ComplexityLevel.MODERATE)

    try:
        # Use radon for Python complexity analysis
        results = cc_visit(code)

        if not results:
            return ComplexityMetrics(complexity_level=ComplexityLevel.MODERATE)

        complexities = [r.complexity for r in results if hasattr(r, "complexity")]
        if not complexities:
            return ComplexityMetrics(complexity_level=ComplexityLevel.MODERATE)

        avg_complexity = sum(complexities) / len(complexities)
        max_complexity = max(complexities)
        sum_complexity = sum(complexities)

        complexity_level = get_complexity_level(avg_complexity)

        return ComplexityMetrics(
            cyclomatic_complexity_avg=avg_complexity,
            cyclomatic_complexity_max=max_complexity,
            cyclomatic_complexity_sum=sum_complexity,
            complexity_level=complexity_level,
        )

    except Exception:
        # Return default on error
        return ComplexityMetrics(complexity_level=ComplexityLevel.MODERATE)


def get_complexity_level(avg_complexity: float) -> ComplexityLevel:
    """
    Determine complexity level from average cyclomatic complexity.

    Args:
        avg_complexity: Average cyclomatic complexity value

    Returns:
        ComplexityLevel enum value
    """
    if avg_complexity <= 5:
        return ComplexityLevel.TRIVIAL
    elif avg_complexity <= 10:
        return ComplexityLevel.SIMPLE
    elif avg_complexity <= 20:
        return ComplexityLevel.MODERATE
    elif avg_complexity <= 50:
        return ComplexityLevel.COMPLEX
    else:
        return ComplexityLevel.VERY_COMPLEX

