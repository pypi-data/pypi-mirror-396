"""Core analysis orchestration."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ossval import __version__
from ossval.analyzers import (
    analyze_complexity,
    analyze_directory_halstead,
    analyze_git_history,
    analyze_health,
    analyze_sloc,
    calculate_maintainability_index,
    find_repository_url,
)
from ossval.data.project_types import detect_project_type
from ossval.estimators import COCOMO2Estimator, SLOCCountEstimator
from ossval.models import (
    AnalysisConfig,
    AnalysisResult,
    Package,
    ProjectType,
    Region,
    SourceType,
)
from ossval.parsers.base import BaseParser
from ossval.parsers.cargo import CargoParser
from ossval.parsers.cyclonedx import CycloneDXParser
from ossval.parsers.go_mod import GoModParser
from ossval.parsers.go_sum import GoSumParser
from ossval.parsers.gradle import GradleParser
from ossval.parsers.maven import MavenParser
from ossval.parsers.package_json import PackageJsonParser
from ossval.parsers.package_lock import PackageLockParser
from ossval.parsers.pipfile import PipfileLockParser
from ossval.parsers.poetry import PoetryLockParser
from ossval.parsers.pyproject import PyProjectParser
from ossval.parsers.requirements import RequirementsParser
from ossval.parsers.simple import SimpleParser
from ossval.parsers.spdx import SPDXParser
from ossval.parsers.yarn import YarnLockParser
from ossval.cache import AnalysisCache


def parse_sbom(filepath: str) -> List[Package]:
    """
    Parse SBOM or lockfile and return list of packages.

    Args:
        filepath: Path to SBOM/lockfile

    Returns:
        List of Package objects
    """
    parser = _select_parser(filepath)
    if not parser:
        raise ValueError(f"No parser found for file: {filepath}")

    parse_result = parser.parse(filepath)
    return parse_result.packages


# Registry of all parsers (order matters - more specific first)
PARSERS: List[BaseParser] = [
    CycloneDXParser(),
    SPDXParser(),
    RequirementsParser(),
    PipfileLockParser(),
    PoetryLockParser(),
    PyProjectParser(),
    PackageJsonParser(),
    PackageLockParser(),
    YarnLockParser(),
    CargoParser(),
    GoModParser(),
    GoSumParser(),
    MavenParser(),
    GradleParser(),
    SimpleParser(),  # Last as fallback
]


def _select_parser(filepath: str) -> Optional[BaseParser]:
    """Select appropriate parser for file."""
    for parser in PARSERS:
        if parser.can_parse(filepath):
            return parser
    return None


async def _analyze_package(
    package: Package,
    config: AnalysisConfig,
    cache: Optional[AnalysisCache] = None,
) -> Package:
    """Analyze a single package (async)."""
    # Find repository URL if not present
    if not package.repository_url and package.ecosystem:
        repo_url = await find_repository_url(
            package.name, package.ecosystem, package.version
        )
        if repo_url:
            package.repository_url = repo_url

    # Detect project type (or use override)
    if config.project_type_override:
        package.project_type = config.project_type_override
        package.project_type_detection = {"source": "cli_override", "confidence": 1.0}
    elif package.project_type == ProjectType.LIBRARY:
        project_type, detection_details = detect_project_type(
            package.name, package.repository_url
        )
        package.project_type = project_type
        package.project_type_detection = detection_details

    # Analyze SLOC if repository URL is available and cloning is enabled
    repo_path = None
    if config.clone_repos and package.repository_url:
        cache_dir = str(cache.cache_dir) if cache else None
        try:
            sloc = await analyze_sloc(
                package.repository_url,
                cache_dir=cache_dir,
                use_cache=config.use_cache,
            )
            if sloc and sloc.total > 0:
                package.sloc = sloc
                package.language = _infer_language_from_sloc(sloc)

                # Store repo path for additional analysis
                if cache_dir:
                    repo_name = package.repository_url.split("/")[-1].replace(".git", "")
                    repo_path = Path(cache_dir) / "repos" / repo_name
            elif sloc is None:
                # Failed to get SLOC - add warning
                package.warnings.append(
                    f"Could not analyze SLOC (clone or analysis failed)"
                )
        except Exception as e:
            package.warnings.append(f"Error analyzing SLOC: {str(e)}")

    # Analyze Halstead metrics if we have a cloned repository
    if repo_path and repo_path.exists():
        try:
            halstead = analyze_directory_halstead(repo_path)
            if halstead:
                package.halstead = halstead
        except Exception as e:
            package.warnings.append(f"Error analyzing Halstead metrics: {str(e)}")

    # Analyze git history if we have a cloned repository
    if repo_path and repo_path.exists():
        try:
            git_history = await analyze_git_history(repo_path, use_cache=config.use_cache)
            if git_history:
                package.git_history = git_history
        except Exception as e:
            package.warnings.append(f"Error analyzing git history: {str(e)}")

    # Analyze complexity (if we have code)
    # Note: For now, we'll use default complexity if no code is available
    if package.complexity is None:
        # Set default moderate complexity
        from ossval.models import ComplexityLevel, ComplexityMetrics

        package.complexity = ComplexityMetrics(complexity_level=ComplexityLevel.MODERATE)

    # Calculate maintainability index if we have SLOC
    if package.sloc:
        try:
            maintainability = calculate_maintainability_index(
                package.sloc, package.halstead, package.complexity
            )
            if maintainability:
                package.maintainability = maintainability
        except Exception as e:
            package.warnings.append(f"Error calculating maintainability index: {str(e)}")

    # Analyze health metrics (GitHub only)
    if package.repository_url and "github.com" in package.repository_url.lower():
        health = await analyze_health(package.repository_url, config.github_token)
        if health:
            package.health = health

    return package


def _infer_language_from_sloc(sloc) -> Optional[str]:
    """Infer primary language from SLOC data."""
    if not sloc or not sloc.by_language:
        return None

    # Get language with most lines
    if sloc.by_language:
        return max(sloc.by_language.items(), key=lambda x: x[1])[0]
    return None


async def _analyze_packages_parallel(
    packages: List[Package],
    config: AnalysisConfig,
    cache: Optional[AnalysisCache] = None,
) -> List[Package]:
    """Analyze packages in parallel with concurrency limit."""
    semaphore = asyncio.Semaphore(config.concurrency)
    tasks = []

    async def analyze_with_semaphore(pkg: Package) -> Package:
        async with semaphore:
            return await _analyze_package(pkg, config, cache)

    for package in packages:
        tasks.append(analyze_with_semaphore(package))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    analyzed_packages = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            packages[i].errors.append(str(result))
            analyzed_packages.append(packages[i])
        else:
            analyzed_packages.append(result)

    return analyzed_packages


def _estimate_costs(
    packages: List[Package], config: AnalysisConfig
) -> List[Package]:
    """Estimate costs for all packages."""
    # Select estimator
    if config.methodology.lower() == "cocomo2":
        estimator = COCOMO2Estimator()
    elif config.methodology.lower() == "sloccount":
        estimator = SLOCCountEstimator()
    else:
        estimator = COCOMO2Estimator()  # Default

    for package in packages:
        if package.sloc and package.sloc.total > 0:
            cost_estimate = estimator.estimate(package, config.region)
            package.cost_estimate = cost_estimate

    return packages


def _identify_critical_packages(packages: List[Package]) -> List[Package]:
    """Identify critical packages (high value + risk factors)."""
    # Calculate total cost
    total_cost = sum(
        pkg.cost_estimate.cost_usd if pkg.cost_estimate else 0 for pkg in packages
    )

    # Sort by cost
    sorted_packages = sorted(
        packages,
        key=lambda p: p.cost_estimate.cost_usd if p.cost_estimate else 0,
        reverse=True,
    )

    critical = []
    top_20_percent_threshold = len(sorted_packages) * 0.2
    one_percent_threshold = total_cost * 0.01

    for i, package in enumerate(sorted_packages):
        if not package.cost_estimate:
            continue

        cost = package.cost_estimate.cost_usd
        is_top_20 = i < top_20_percent_threshold
        is_above_1_percent = cost >= one_percent_threshold

        if is_top_20 or is_above_1_percent:
            # Check risk factors
            risk_factors = []

            if package.health:
                # Low bus factor
                if package.health.bus_factor and package.health.bus_factor <= 2:
                    risk_factors.append("low_bus_factor")
                    package.is_critical = True

                # Inactive
                if (
                    package.health.is_actively_maintained is False
                    or (
                        package.health.last_commit_date
                        and package.health.last_commit_date.year < 2023
                    )
                ):
                    risk_factors.append("inactive")
                    package.is_critical = True

                # No funding
                if package.health.has_funding is False:
                    risk_factors.append("no_funding")
                    if package.is_critical:
                        risk_factors.append("no_funding")

            if risk_factors:
                package.risk_factors = risk_factors
                critical.append(package)

    return critical


async def analyze(
    filepath: str | List[Package], config: Optional[AnalysisConfig] = None
) -> AnalysisResult:
    """
    Main analysis function.

    Args:
        filepath: Path to SBOM/lockfile or list of Package objects
        config: Optional analysis configuration

    Returns:
        AnalysisResult with complete analysis
    """
    if config is None:
        config = AnalysisConfig()

    # Initialize cache
    cache = AnalysisCache(
        cache_dir=config.cache_dir, ttl_days=config.cache_ttl_days
    ) if config.use_cache else None

    # Parse input
    if isinstance(filepath, list):
        # Already a list of packages
        packages = filepath
        source_type = SourceType.SIMPLE
        source_file = "inline"
    else:
        # Parse file
        parser = _select_parser(filepath)
        if not parser:
            return AnalysisResult(
                errors=[f"No parser found for file: {filepath}"],
                warnings=[],
            )

        parse_result = parser.parse(filepath)
        packages = parse_result.packages
        source_type = parse_result.source_type
        source_file = parse_result.source_file

    # Analyze packages
    analyzed_packages = await _analyze_packages_parallel(packages, config, cache)

    # Estimate costs
    analyzed_packages = _estimate_costs(analyzed_packages, config)

    # Identify critical packages
    critical_packages = _identify_critical_packages(analyzed_packages)

    # Calculate summary statistics
    total_packages = len(packages)
    analyzed_count = len([p for p in analyzed_packages if p.cost_estimate])
    # Count packages without SLOC (not errors, just missing data)
    packages_without_sloc = len([p for p in analyzed_packages if not p.sloc])
    failed_count = total_packages - analyzed_count - packages_without_sloc

    total_sloc = sum(
        p.sloc.total if p.sloc else 0 for p in analyzed_packages
    )
    total_effort_months = sum(
        p.cost_estimate.effort_person_months if p.cost_estimate else 0
        for p in analyzed_packages
    )
    total_effort_years = total_effort_months / 12.0
    total_cost = sum(
        p.cost_estimate.cost_usd if p.cost_estimate else 0
        for p in analyzed_packages
    )
    total_cost_low = sum(
        p.cost_estimate.cost_usd_low if p.cost_estimate else 0
        for p in analyzed_packages
    )
    total_cost_high = sum(
        p.cost_estimate.cost_usd_high if p.cost_estimate else 0
        for p in analyzed_packages
    )

    # Group by language, ecosystem, project type
    by_language: dict[str, float] = {}
    by_ecosystem: dict[str, float] = {}
    by_project_type: dict[str, float] = {}

    for package in analyzed_packages:
        if package.cost_estimate:
            cost = package.cost_estimate.cost_usd

            if package.language:
                by_language[package.language] = (
                    by_language.get(package.language, 0) + cost
                )

            if package.ecosystem:
                by_ecosystem[package.ecosystem] = (
                    by_ecosystem.get(package.ecosystem, 0) + cost
                )

            by_project_type[package.project_type.value] = (
                by_project_type.get(package.project_type.value, 0) + cost
            )

    # Build result
    result = AnalysisResult(
        meta={
            "tool": "ossval",
            "version": __version__,
            "analyzed_at": datetime.utcnow().isoformat() + "Z",
            "source_file": source_file,
            "source_type": source_type.value,
            "config": {
                "region": config.region.value,
                "clone_repos": config.clone_repos,
                "methodology": config.methodology,
                "project_type_override": config.project_type_override.value if config.project_type_override else None,
            },
        },
        summary={
            "total_packages": total_packages,
            "analyzed_packages": analyzed_count,
            "failed_packages": failed_count,
            "packages_without_sloc": packages_without_sloc,
            "total_sloc": total_sloc,
            "total_effort_person_months": total_effort_months,
            "total_effort_person_years": total_effort_years,
            "total_cost_usd": total_cost,
            "total_cost_usd_low": total_cost_low,
            "total_cost_usd_high": total_cost_high,
        },
        packages=analyzed_packages,
        critical_packages=critical_packages,
        errors=[],
        warnings=[],
    )

    return result


def quick_estimate(
    sloc: int,
    region: Region = Region.GLOBAL_AVERAGE,
    project_type: ProjectType = ProjectType.LIBRARY,
) -> dict[str, any]:
    """
    Quick cost estimate from SLOC only.

    Args:
        sloc: Source lines of code
        region: Region for salary calculation
        project_type: Project type

    Returns:
        Dictionary with cost estimate
    """
    from ossval.models import Package, SLOCMetrics

    # Create a minimal package
    package = Package(
        name="estimate",
        project_type=project_type,
        sloc=SLOCMetrics(
            total=sloc,
            code_lines=sloc,
            comment_lines=0,
            blank_lines=0,
            by_language={},
        ),
    )

    # Estimate using COCOMO II
    estimator = COCOMO2Estimator()
    cost_estimate = estimator.estimate(package, region)

    return {
        "sloc": sloc,
        "region": region.value,
        "project_type": project_type.value,
        "effort_person_months": cost_estimate.effort_person_months,
        "effort_person_years": cost_estimate.effort_person_years,
        "cost_usd": cost_estimate.cost_usd,
        "cost_usd_low": cost_estimate.cost_usd_low,
        "cost_usd_high": cost_estimate.cost_usd_high,
        "methodology": cost_estimate.methodology,
    }

