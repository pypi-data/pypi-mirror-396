"""Command-line interface for OSSVAL."""

import asyncio
import os
from pathlib import Path

import click

from ossval import __version__
from ossval.cache import AnalysisCache
from ossval.core import analyze, quick_estimate
from ossval.models import AnalysisConfig, Region, ProjectType
from ossval.output import format_csv, format_json, format_text


@click.group()
@click.version_option(version=__version__)
def main():
    """OSSVAL: Open Source Software Valuation Tool."""
    pass


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option(
    "--region",
    "-r",
    type=click.Choice([r.value for r in Region], case_sensitive=False),
    default="global_average",
    help="Region for salary calculation",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["text", "json", "csv"], case_sensitive=False),
    default="text",
    help="Output format",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file or directory",
)
@click.option(
    "--no-clone",
    is_flag=True,
    help="Don't clone repos for SLOC analysis",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Don't use disk cache",
)
@click.option(
    "--cache-dir",
    type=click.Path(),
    help="Cache directory path",
)
@click.option(
    "--concurrency",
    "-c",
    type=int,
    default=4,
    help="Max parallel operations",
)
@click.option(
    "--github-token",
    envvar="GITHUB_TOKEN",
    help="GitHub API token (or set GITHUB_TOKEN env var)",
)
@click.option(
    "--methodology",
    type=click.Choice(["cocomo2", "sloccount"], case_sensitive=False),
    default="cocomo2",
    help="Cost estimation methodology",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice([pt.value for pt in ProjectType], case_sensitive=False),
    help="Override project type detection",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Quiet mode")
def analyze_cmd(
    filepath,
    region,
    format,
    output,
    no_clone,
    no_cache,
    cache_dir,
    concurrency,
    github_token,
    methodology,
    type,
    verbose,
    quiet,
):
    """Analyze SBOM or lockfile and calculate OSS value."""
    # Build config
    config = AnalysisConfig(
        region=Region(region),
        clone_repos=not no_clone,
        use_cache=not no_cache,
        cache_dir=cache_dir,
        concurrency=concurrency,
        github_token=github_token or os.getenv("GITHUB_TOKEN"),
        methodology=methodology,
        project_type_override=ProjectType(type) if type else None,
        verbose=verbose,
        quiet=quiet,
    )

    if not quiet:
        click.echo(f"Analyzing {filepath}...", err=True)
        if config.clone_repos:
            click.echo("  Cloning repositories and analyzing SLOC (this may take a while)...", err=True)

    # Run analysis
    result = asyncio.run(analyze(filepath, config))
    
    if not quiet and config.clone_repos:
        # Show summary of what happened
        packages_with_repos = len([p for p in result.packages if p.repository_url])
        packages_with_sloc = len([p for p in result.packages if p.sloc])
        if packages_with_repos > 0:
            click.echo(
                f"  Analyzed {packages_with_sloc}/{packages_with_repos} packages with repository URLs",
                err=True,
            )

    # Format output
    if format == "text":
        output_text = format_text(result, output_file=output)
        if not output:
            click.echo(output_text)
    elif format == "json":
        output_text = format_json(result, output_file=output)
        if not output:
            click.echo(output_text)
    elif format == "csv":
        csv_files = format_csv(result, output_dir=output)
        if not quiet:
            click.echo(f"Generated CSV files:", err=True)
            for key, path in csv_files.items():
                click.echo(f"  {key}: {path}", err=True)

    # Exit with error code if there were failures
    if result.summary.get("failed_packages", 0) > 0:
        click.get_current_context().exit(1)


@main.command()
@click.option("--sloc", type=int, required=True, help="Source lines of code")
@click.option(
    "--region",
    "-r",
    type=click.Choice([r.value for r in Region], case_sensitive=False),
    default="global_average",
    help="Region for salary calculation",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice([pt.value for pt in ProjectType], case_sensitive=False),
    default="library",
    help="Project type",
)
def estimate(sloc, region, type):
    """Quick cost estimate from SLOC only."""
    result = quick_estimate(sloc, Region(region), ProjectType(type))

    click.echo(f"Estimated cost: ${result['cost_usd']:,.0f}")
    click.echo(f"  Range: ${result['cost_usd_low']:,.0f} - ${result['cost_usd_high']:,.0f}")
    click.echo(f"  Effort: {result['effort_person_years']:.1f} person-years")
    click.echo(f"  Methodology: {result['methodology']}")


@main.group()
def formats():
    """List supported file formats."""
    pass


@formats.command("list")
def formats_list():
    """List all supported input formats."""
    click.echo("Supported SBOM Formats:")
    click.echo("  - CycloneDX (JSON, XML)")
    click.echo("  - SPDX (JSON, tag-value)")
    click.echo()
    click.echo("Supported Lockfile Formats:")
    click.echo("  - Python: requirements.txt, Pipfile.lock, poetry.lock, pyproject.toml")
    click.echo("  - JavaScript: package.json, package-lock.json, yarn.lock")
    click.echo("  - Rust: Cargo.toml, Cargo.lock")
    click.echo("  - Go: go.mod, go.sum")
    click.echo("  - Java: pom.xml, build.gradle")
    click.echo("  - Simple text format (one package per line)")


@formats.command("project-types")
def formats_project_types():
    """List all supported project types and their multipliers."""
    from ossval.data.multipliers import PROJECT_TYPE_MULTIPLIERS

    click.echo("Supported Project Types and Cost Multipliers:")
    click.echo("=" * 60)
    click.echo(f"{'Type':<20} {'Salary Multiplier':<20} {'Effort Multiplier':<20}")
    click.echo("-" * 60)

    # Sort by salary multiplier descending
    sorted_types = sorted(PROJECT_TYPE_MULTIPLIERS.items(),
                         key=lambda x: x[1]['salary'], reverse=True)

    for project_type, multipliers in sorted_types:
        type_name = project_type.value.replace('_', ' ').title()
        salary_mult = multipliers['salary']
        effort_mult = multipliers['effort']
        click.echo(f"{type_name:<20} {salary_mult:<20.2f} {effort_mult:<20.2f}")

    click.echo()
    click.echo("Notes:")
    click.echo("- Multipliers are applied to base cost estimates")
    click.echo("- Cryptography projects have the highest multiplier (1.6x salary)")
    click.echo("- Script/utility projects have the lowest multiplier (0.7x salary)")
    click.echo("- Library type is the baseline (1.0x)")


@formats.command("methodologies")
def formats_methodologies():
    """List available cost estimation methodologies."""
    click.echo("Available Cost Estimation Methodologies:")
    click.echo("=" * 60)
    click.echo()
    click.echo("1. COCOMO II (Primary)")
    click.echo("   - Most sophisticated and widely used")
    click.echo("   - Formula: Effort = a × (KSLOC)^b × EAF × Multipliers")
    click.echo("   - Default: a=2.94, b=1.0997, EAF=1.0")
    click.echo("   - Accounts for project type and complexity")
    click.echo("   - Provides 70%-150% confidence ranges")
    click.echo()
    click.echo("2. SLOCCount (Alternative)")
    click.echo("   - Simpler model based on David Wheeler's SLOCCount")
    click.echo("   - Formula: Effort = a × (KSLOC)^b")
    click.echo("   - Default: a=2.4, b=1.05")
    click.echo("   - Less sophisticated but faster")
    click.echo("   - Lower confidence scores")
    click.echo()
    click.echo("Both models use:")
    click.echo("- Regional salary data (18+ regions)")
    click.echo("- Project type detection")
    click.echo("- Complexity analysis")
    click.echo("- Language-specific adjustments")


@main.group()
def cache():
    """Cache management commands."""
    pass


@cache.command("clear")
@click.option(
    "--cache-dir",
    type=click.Path(),
    help="Cache directory path",
)
def cache_clear(cache_dir):
    """Clear analysis cache."""
    cache = AnalysisCache(cache_dir=cache_dir)
    cache.clear()
    click.echo("Cache cleared.")


@cache.command("info")
@click.option(
    "--cache-dir",
    type=click.Path(),
    help="Cache directory path",
)
def cache_info(cache_dir):
    """Show cache information."""
    cache = AnalysisCache(cache_dir=cache_dir)
    info = cache.info()
    click.echo(f"Cache directory: {info['cache_dir']}")
    click.echo(f"Cache size: {info['size']:,} bytes")
    click.echo(f"Cache entries: {info['count']:,}")


if __name__ == "__main__":
    main()

