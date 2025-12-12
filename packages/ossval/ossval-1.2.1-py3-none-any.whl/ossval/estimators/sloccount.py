"""SLOCCount cost estimation model."""

from ossval.data.multipliers import (
    get_complexity_multiplier,
    get_halstead_multiplier,
    get_maturity_multiplier,
    get_project_type_multiplier,
)
from ossval.data.salaries import get_monthly_rate
from ossval.estimators.base import BaseEstimator
from ossval.models import CostEstimate, Package, Region


class SLOCCountEstimator(BaseEstimator):
    """
    SLOCCount estimator (simpler model).

    Formula:
        Effort = 2.4 × (KSLOC)^1.05
        Cost (USD) = Effort × Monthly_Fully_Loaded_Rate
    """

    def __init__(self, a: float = 2.4, b: float = 1.05):
        """
        Initialize SLOCCount estimator.

        Args:
            a: Calibration constant (default: 2.4)
            b: Scale factor (default: 1.05)
        """
        self.a = a
        self.b = b

    def estimate(self, package: Package, region: Region) -> CostEstimate:
        """
        Estimate cost using SLOCCount model.

        Args:
            package: Package to estimate
            region: Region for salary calculation

        Returns:
            CostEstimate with cost calculations
        """
        if not package.sloc or package.sloc.total == 0:
            return CostEstimate(
                effort_person_months=0.0,
                effort_person_years=0.0,
                cost_usd=0.0,
                cost_usd_low=0.0,
                cost_usd_high=0.0,
                methodology="SLOCCount",
                confidence=0.0,
                region=region,
                project_type=package.project_type,
                complexity_multiplier=1.0,
                project_type_multiplier=1.0,
                maturity_multiplier=1.0,
                halstead_multiplier=1.0,
            )

        # Calculate KSLOC
        ksloc = package.sloc.code_lines / 1000.0

        # Get multipliers
        complexity_multiplier = 1.0
        if package.complexity:
            complexity_multiplier = get_complexity_multiplier(
                package.complexity.complexity_level
            )

        project_type_multiplier = get_project_type_multiplier(
            package.project_type, multiplier_type="effort"
        )

        # Get new multipliers based on git history and Halstead metrics
        maturity_multiplier = get_maturity_multiplier(package.git_history)
        halstead_multiplier = get_halstead_multiplier(package.halstead)

        # Calculate effort with all multipliers
        effort_person_months = (
            self.a
            * (ksloc ** self.b)
            * complexity_multiplier
            * project_type_multiplier
            * maturity_multiplier
            * halstead_multiplier
        )

        effort_person_years = effort_person_months / 12.0

        # Get monthly rate
        monthly_rate = get_monthly_rate(region)

        # Get salary multiplier
        salary_multiplier = get_project_type_multiplier(
            package.project_type, multiplier_type="salary"
        )

        # Calculate cost
        base_cost = effort_person_months * monthly_rate * salary_multiplier

        # Confidence
        confidence = 0.4
        if package.sloc:
            confidence += 0.2
        if package.complexity:
            confidence += 0.1
        if package.halstead:
            confidence += 0.1
        if package.git_history:
            confidence += 0.1
        confidence = min(confidence, 1.0)

        cost_usd_low = base_cost * 0.7
        cost_usd_high = base_cost * 1.5

        return CostEstimate(
            effort_person_months=effort_person_months,
            effort_person_years=effort_person_years,
            cost_usd=base_cost,
            cost_usd_low=cost_usd_low,
            cost_usd_high=cost_usd_high,
            methodology="SLOCCount",
            confidence=confidence,
            region=region,
            project_type=package.project_type,
            complexity_multiplier=complexity_multiplier,
            project_type_multiplier=project_type_multiplier,
            maturity_multiplier=maturity_multiplier,
            halstead_multiplier=halstead_multiplier,
        )

