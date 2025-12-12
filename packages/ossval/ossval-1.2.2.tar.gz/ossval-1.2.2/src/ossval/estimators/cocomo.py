"""COCOMO II cost estimation model."""

from ossval.data.multipliers import (
    get_complexity_multiplier,
    get_halstead_multiplier,
    get_maturity_multiplier,
    get_project_type_multiplier,
)
from ossval.data.salaries import get_monthly_rate
from ossval.estimators.base import BaseEstimator
from ossval.models import CostEstimate, Package, ProjectType, Region


class COCOMO2Estimator(BaseEstimator):
    """
    COCOMO II (Constructive Cost Model) estimator.

    Formula:
        Effort (person-months) = a × (KSLOC)^b × EAF × Complexity_Multiplier × Project_Type_Multiplier
        Cost (USD) = Effort × Monthly_Fully_Loaded_Rate

    Where:
        - a = 2.94 (calibration constant, configurable)
        - b = 1.0997 (scale factor, configurable)
        - KSLOC = thousands of source lines of code
        - EAF = Effort Adjustment Factor (default 1.0, configurable)
    """

    def __init__(
        self,
        a: float = 2.94,
        b: float = 1.0997,
        eaf: float = 1.0,
    ):
        """
        Initialize COCOMO II estimator.

        Args:
            a: Calibration constant (default: 2.94)
            b: Scale factor (default: 1.0997)
            eaf: Effort Adjustment Factor (default: 1.0)
        """
        self.a = a
        self.b = b
        self.eaf = eaf

    def estimate(self, package: Package, region: Region) -> CostEstimate:
        """
        Estimate cost using COCOMO II model.

        Args:
            package: Package to estimate
            region: Region for salary calculation

        Returns:
            CostEstimate with cost calculations
        """
        if not package.sloc or package.sloc.total == 0:
            # Return zero estimate if no SLOC data
            return CostEstimate(
                effort_person_months=0.0,
                effort_person_years=0.0,
                cost_usd=0.0,
                cost_usd_low=0.0,
                cost_usd_high=0.0,
                methodology="COCOMO II",
                confidence=0.0,
                region=region,
                project_type=package.project_type,
                complexity_multiplier=1.0,
                project_type_multiplier=1.0,
                maturity_multiplier=1.0,
                halstead_multiplier=1.0,
            )

        # Calculate KSLOC (thousands of source lines of code)
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

        # Calculate effort using COCOMO II formula with new multipliers
        # Effort = a × (KSLOC)^b × EAF × Complexity × ProjectType × Maturity × Halstead
        effort_person_months = (
            self.a
            * (ksloc ** self.b)
            * self.eaf
            * complexity_multiplier
            * project_type_multiplier
            * maturity_multiplier
            * halstead_multiplier
        )

        # Convert to person-years
        effort_person_years = effort_person_months / 12.0

        # Get monthly rate for region
        monthly_rate = get_monthly_rate(region)

        # Get salary multiplier for project type
        salary_multiplier = get_project_type_multiplier(
            package.project_type, multiplier_type="salary"
        )

        # Calculate cost
        base_cost = effort_person_months * monthly_rate * salary_multiplier

        # Calculate confidence (based on data availability)
        confidence = 0.5  # Base confidence
        if package.sloc:
            confidence += 0.15
        if package.complexity:
            confidence += 0.1
        if package.halstead:
            confidence += 0.1
        if package.git_history:
            confidence += 0.1
        if package.health:
            confidence += 0.05
        confidence = min(confidence, 1.0)

        # Calculate low and high estimates (70% and 150% of base)
        cost_usd_low = base_cost * 0.7
        cost_usd_high = base_cost * 1.5

        return CostEstimate(
            effort_person_months=effort_person_months,
            effort_person_years=effort_person_years,
            cost_usd=base_cost,
            cost_usd_low=cost_usd_low,
            cost_usd_high=cost_usd_high,
            methodology="COCOMO II",
            confidence=confidence,
            region=region,
            project_type=package.project_type,
            complexity_multiplier=complexity_multiplier,
            project_type_multiplier=project_type_multiplier,
            maturity_multiplier=maturity_multiplier,
            halstead_multiplier=halstead_multiplier,
        )

