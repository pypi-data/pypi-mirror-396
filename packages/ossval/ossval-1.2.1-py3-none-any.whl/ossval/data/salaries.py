"""Regional salary data for cost calculations."""

from ossval.models import Region

# Base annual salaries (USD) for mid-senior software engineers
REGIONAL_SALARIES: dict[Region, dict[str, float]] = {
    Region.US_SF: {"base_salary": 220000.0, "overhead_multiplier": 2.3},
    Region.US_NYC: {"base_salary": 200000.0, "overhead_multiplier": 2.2},
    Region.US_SEATTLE: {"base_salary": 210000.0, "overhead_multiplier": 2.1},
    Region.US_OTHER: {"base_salary": 160000.0, "overhead_multiplier": 2.0},
    Region.CANADA: {"base_salary": 130000.0, "overhead_multiplier": 1.9},
    Region.UK: {"base_salary": 95000.0, "overhead_multiplier": 1.85},
    Region.GERMANY: {"base_salary": 90000.0, "overhead_multiplier": 1.9},
    Region.FRANCE: {"base_salary": 75000.0, "overhead_multiplier": 2.0},
    Region.NETHERLANDS: {"base_salary": 85000.0, "overhead_multiplier": 1.85},
    Region.SWITZERLAND: {"base_salary": 140000.0, "overhead_multiplier": 2.0},
    Region.ISRAEL: {"base_salary": 110000.0, "overhead_multiplier": 1.8},
    Region.JAPAN: {"base_salary": 70000.0, "overhead_multiplier": 1.7},
    Region.AUSTRALIA: {"base_salary": 115000.0, "overhead_multiplier": 1.85},
    Region.INDIA: {"base_salary": 30000.0, "overhead_multiplier": 1.5},
    Region.CHINA: {"base_salary": 50000.0, "overhead_multiplier": 1.6},
    Region.BRAZIL: {"base_salary": 35000.0, "overhead_multiplier": 1.7},
    Region.LATIN_AMERICA: {"base_salary": 28000.0, "overhead_multiplier": 1.5},
    Region.EASTERN_EUROPE: {"base_salary": 45000.0, "overhead_multiplier": 1.5},
    Region.GLOBAL_AVERAGE: {"base_salary": 75000.0, "overhead_multiplier": 1.8},
}


def get_regional_salary(region: Region) -> dict[str, float]:
    """Get salary data for a region."""
    return REGIONAL_SALARIES.get(region, REGIONAL_SALARIES[Region.GLOBAL_AVERAGE])


def get_monthly_rate(region: Region) -> float:
    """
    Calculate fully loaded monthly rate for a region.

    Formula: (Annual Salary / 12) × Overhead Multiplier
    """
    salary_data = get_regional_salary(region)
    annual_salary = salary_data["base_salary"]
    overhead = salary_data["overhead_multiplier"]
    return (annual_salary / 12) * overhead

