"""Base estimator interface."""

from abc import ABC, abstractmethod

from ossval.models import CostEstimate, Package, Region


class BaseEstimator(ABC):
    """Abstract base class for cost estimators."""

    @abstractmethod
    def estimate(self, package: Package, region: Region) -> CostEstimate:
        """
        Estimate cost for a package.

        Args:
            package: Package to estimate
            region: Region for salary calculation

        Returns:
            CostEstimate with cost calculations
        """
        pass

