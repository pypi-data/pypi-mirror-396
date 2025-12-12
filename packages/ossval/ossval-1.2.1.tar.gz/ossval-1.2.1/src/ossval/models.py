"""Core data models for OSSVAL."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Region(str, Enum):
    """Regional salary data identifiers."""

    US_SF = "us_sf"
    US_NYC = "us_nyc"
    US_SEATTLE = "us_seattle"
    US_OTHER = "us_other"
    CANADA = "canada"
    UK = "uk"
    GERMANY = "germany"
    FRANCE = "france"
    NETHERLANDS = "netherlands"
    SWITZERLAND = "switzerland"
    ISRAEL = "israel"
    JAPAN = "japan"
    AUSTRALIA = "australia"
    INDIA = "india"
    CHINA = "china"
    BRAZIL = "brazil"
    LATIN_AMERICA = "latin_america"
    EASTERN_EUROPE = "eastern_europe"
    GLOBAL_AVERAGE = "global_average"


class ProjectType(str, Enum):
    """Project type classifications."""

    SCRIPT = "script"
    LIBRARY = "library"
    FRAMEWORK = "framework"
    COMPILER = "compiler"
    DATABASE = "database"
    OPERATING_SYSTEM = "operating_system"
    CRYPTOGRAPHY = "cryptography"
    MACHINE_LEARNING = "machine_learning"
    NETWORKING = "networking"
    EMBEDDED = "embedded"
    GRAPHICS = "graphics"
    SCIENTIFIC = "scientific"
    DEVTOOLS = "devtools"


class ComplexityLevel(str, Enum):
    """Cyclomatic complexity levels."""

    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class SourceType(str, Enum):
    """Source file types."""

    CYCLONEDX = "cyclonedx"
    SPDX = "spdx"
    REQUIREMENTS = "requirements"
    PACKAGE_JSON = "package_json"
    CARGO = "cargo"
    GO_MOD = "go_mod"
    MAVEN = "maven"
    GRADLE = "gradle"
    GEMFILE = "gemfile"
    COMPOSER = "composer"
    NUGET = "nuget"
    SWIFT = "swift"
    CONAN = "conan"
    VCPKG = "vcpkg"
    SIMPLE = "simple"
    PIPFILE = "pipfile"
    POETRY = "poetry"
    PACKAGE_LOCK = "package_lock"
    YARN = "yarn"
    GO_SUM = "go_sum"


class SLOCMetrics(BaseModel):
    """Source lines of code metrics."""

    total: int = Field(description="Total SLOC")
    code_lines: int = Field(description="Lines of code (excluding comments/blanks)")
    comment_lines: int = Field(description="Lines of comments")
    blank_lines: int = Field(description="Blank lines")
    by_language: Dict[str, int] = Field(
        default_factory=dict, description="SLOC by programming language"
    )


class ComplexityMetrics(BaseModel):
    """Cyclomatic complexity metrics."""

    cyclomatic_complexity_avg: Optional[float] = Field(
        None, description="Average cyclomatic complexity"
    )
    cyclomatic_complexity_max: Optional[int] = Field(
        None, description="Maximum cyclomatic complexity"
    )
    cyclomatic_complexity_sum: Optional[int] = Field(
        None, description="Sum of cyclomatic complexity"
    )
    complexity_level: ComplexityLevel = Field(
        ComplexityLevel.MODERATE, description="Complexity level classification"
    )


class HalsteadMetrics(BaseModel):
    """Halstead complexity metrics."""

    vocabulary: int = Field(description="n = n1 + n2 (unique operators + operands)")
    length: int = Field(description="N = N1 + N2 (total operators + operands)")
    calculated_length: float = Field(description="Estimated length")
    volume: float = Field(description="Program volume (N × log2(n))")
    difficulty: float = Field(description="Program difficulty")
    effort: float = Field(description="Effort to implement/understand")
    time_seconds: float = Field(description="Time required to program (seconds)")
    bugs: float = Field(description="Estimated number of bugs (volume / 3000)")


class GitHistoryMetrics(BaseModel):
    """Git repository history metrics."""

    commit_count: int = Field(description="Total number of commits")
    contributor_count: int = Field(description="Total number of contributors")
    age_days: int = Field(description="Repository age in days")
    age_years: float = Field(description="Repository age in years")
    first_commit_date: Optional[datetime] = Field(None, description="Date of first commit")
    last_commit_date: Optional[datetime] = Field(None, description="Date of last commit")
    release_count: int = Field(description="Number of releases/tags")
    commits_per_month: float = Field(description="Average commits per month (last year)")
    avg_files_per_commit: float = Field(description="Average files changed per commit")
    high_churn_files: int = Field(description="Number of frequently changed files")
    bus_factor: int = Field(description="Minimum contributors for 50% of commits")


class MaintainabilityMetrics(BaseModel):
    """Maintainability Index and derived metrics."""

    maintainability_index: float = Field(
        ge=0.0, le=100.0, description="Maintainability Index (0-100, higher is better)"
    )
    maintainability_level: str = Field(description="Low/Medium/High maintainability")
    comment_ratio: float = Field(description="Ratio of comment lines to code lines")
    avg_complexity_per_kloc: float = Field(
        description="Average cyclomatic complexity per 1000 LOC"
    )


class HealthMetrics(BaseModel):
    """Repository health metrics from GitHub API."""

    stars: Optional[int] = None
    forks: Optional[int] = None
    contributors_count: Optional[int] = None
    open_issues: Optional[int] = None
    last_commit_date: Optional[datetime] = None
    created_date: Optional[datetime] = None
    license: Optional[str] = None
    has_funding: Optional[bool] = None
    has_security_policy: Optional[bool] = None
    bus_factor: Optional[int] = Field(None, description="Number of key contributors")
    is_actively_maintained: Optional[bool] = Field(
        None, description="True if commits in last 6 months"
    )


class CostEstimate(BaseModel):
    """Cost estimation results."""

    effort_person_months: float = Field(description="Estimated effort in person-months")
    effort_person_years: float = Field(description="Estimated effort in person-years")
    cost_usd: float = Field(description="Estimated cost in USD")
    cost_usd_low: float = Field(description="Lower bound estimate (70% of base)")
    cost_usd_high: float = Field(description="Upper bound estimate (150% of base)")
    methodology: str = Field(description="Estimation methodology used")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)"
    )
    region: Region = Field(description="Region used for salary calculation")
    project_type: ProjectType = Field(description="Project type classification")
    complexity_multiplier: float = Field(description="Complexity multiplier applied")
    project_type_multiplier: float = Field(description="Project type multiplier applied")
    maturity_multiplier: float = Field(
        default=1.0, description="Maturity/scale multiplier from git history"
    )
    halstead_multiplier: float = Field(
        default=1.0, description="Halstead complexity multiplier"
    )


class Package(BaseModel):
    """Represents a single package/dependency."""

    name: str = Field(description="Package name")
    version: Optional[str] = Field(None, description="Package version")
    ecosystem: Optional[str] = Field(None, description="Package ecosystem (pypi, npm, etc.)")
    language: Optional[str] = Field(None, description="Primary programming language")
    project_type: ProjectType = Field(
        ProjectType.LIBRARY, description="Project type classification"
    )
    project_type_detection: Optional[Dict[str, Any]] = Field(
        None, description="Details about how project type was detected"
    )
    repository_url: Optional[str] = Field(None, description="Source repository URL")
    sloc: Optional[SLOCMetrics] = Field(None, description="SLOC metrics")
    complexity: Optional[ComplexityMetrics] = Field(None, description="Complexity metrics")
    halstead: Optional[HalsteadMetrics] = Field(None, description="Halstead complexity metrics")
    maintainability: Optional[MaintainabilityMetrics] = Field(
        None, description="Maintainability metrics"
    )
    git_history: Optional[GitHistoryMetrics] = Field(None, description="Git history metrics")
    health: Optional[HealthMetrics] = Field(None, description="Health metrics")
    cost_estimate: Optional[CostEstimate] = Field(None, description="Cost estimate")
    is_critical: bool = Field(
        False, description="True if package is critical (high value + risk factors)"
    )
    risk_factors: List[str] = Field(
        default_factory=list, description="List of identified risk factors"
    )
    errors: List[str] = Field(
        default_factory=list, description="Errors encountered during analysis"
    )
    warnings: List[str] = Field(
        default_factory=list, description="Warnings during analysis"
    )


class AnalysisConfig(BaseModel):
    """Configuration for analysis."""

    region: Region = Field(Region.GLOBAL_AVERAGE, description="Region for salary calculation")
    clone_repos: bool = Field(True, description="Whether to clone repositories for SLOC analysis")
    use_cache: bool = Field(True, description="Whether to use disk cache")
    cache_dir: Optional[str] = Field(None, description="Cache directory path")
    cache_ttl_days: int = Field(30, description="Cache TTL in days")
    concurrency: int = Field(4, ge=1, le=32, description="Max parallel operations")
    github_token: Optional[str] = Field(None, description="GitHub API token")
    methodology: str = Field("cocomo2", description="Cost estimation methodology")
    verbose: bool = Field(False, description="Verbose output")
    quiet: bool = Field(False, description="Quiet mode (minimal output)")
    project_type_override: Optional[ProjectType] = Field(None, description="Override project type detection")


class AnalysisResult(BaseModel):
    """Complete analysis results."""

    meta: Dict[str, Any] = Field(default_factory=dict, description="Metadata")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Summary statistics")
    packages: List[Package] = Field(default_factory=list, description="Analyzed packages")
    critical_packages: List[Package] = Field(
        default_factory=list, description="Packages requiring attention"
    )
    errors: List[str] = Field(default_factory=list, description="Global errors")
    warnings: List[str] = Field(default_factory=list, description="Global warnings")

    def to_json(self, filepath: Optional[str] = None) -> str:
        """Export results as JSON."""
        import json
        from datetime import datetime

        # Convert to dict with proper serialization
        data = self.model_dump(mode="json")
        json_str = json.dumps(data, indent=2, default=str)

        if filepath:
            with open(filepath, "w") as f:
                f.write(json_str)

        return json_str

    def to_csv(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """Export results as CSV files."""
        import csv
        from pathlib import Path

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path.cwd()

        # Summary CSV
        summary_file = output_path / "summary.csv"
        with open(summary_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            for key, value in self.summary.items():
                writer.writerow([key, value])

        # Packages CSV
        packages_file = output_path / "packages.csv"
        if self.packages:
            fieldnames = [
                "name",
                "version",
                "ecosystem",
                "language",
                "project_type",
                "sloc",
                "complexity_level",
                "cost_usd",
                "cost_usd_low",
                "cost_usd_high",
                "effort_months",
                "contributors",
                "last_commit",
                "is_critical",
            ]
            with open(packages_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for pkg in self.packages:
                    row = {
                        "name": pkg.name,
                        "version": pkg.version or "",
                        "ecosystem": pkg.ecosystem or "",
                        "language": pkg.language or "",
                        "project_type": pkg.project_type.value,
                        "sloc": pkg.sloc.total if pkg.sloc else 0,
                        "complexity_level": (
                            pkg.complexity.complexity_level.value if pkg.complexity else ""
                        ),
                        "cost_usd": (
                            int(pkg.cost_estimate.cost_usd) if pkg.cost_estimate else 0
                        ),
                        "cost_usd_low": (
                            int(pkg.cost_estimate.cost_usd_low) if pkg.cost_estimate else 0
                        ),
                        "cost_usd_high": (
                            int(pkg.cost_estimate.cost_usd_high) if pkg.cost_estimate else 0
                        ),
                        "effort_months": (
                            round(pkg.cost_estimate.effort_person_months, 1)
                            if pkg.cost_estimate
                            else 0
                        ),
                        "contributors": (
                            pkg.health.contributors_count if pkg.health else None
                        ),
                        "last_commit": (
                            pkg.health.last_commit_date.isoformat()
                            if pkg.health and pkg.health.last_commit_date
                            else ""
                        ),
                        "is_critical": pkg.is_critical,
                    }
                    writer.writerow(row)

        return {
            "summary": str(summary_file),
            "packages": str(packages_file),
        }

