"""Rich text formatter for terminal output."""

from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.text import Text

from ossval.models import AnalysisResult


def format_text(result: AnalysisResult, output_file: Optional[str] = None) -> str:
    """
    Format analysis results as rich text for terminal.

    Args:
        result: AnalysisResult to format
        output_file: Optional file path to write to

    Returns:
        Formatted text string
    """
    if output_file:
        console = Console(file=open(output_file, "w"))
    else:
        console = Console()

    # Header
    console.print()
    console.print("═" * 64, style="bold")
    console.print("                    OSSVAL Analysis Report", style="bold")
    console.print(
        f"                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        style="dim",
    )
    console.print("═" * 64, style="bold")
    console.print()

    # Executive Summary
    console.print("Executive Summary", style="bold")
    console.print("─" * 64)

    summary = result.summary
    total_cost = summary.get("total_cost_usd", 0)
    total_cost_low = summary.get("total_cost_usd_low", 0)
    total_cost_high = summary.get("total_cost_usd_high", 0)
    total_effort_years = summary.get("total_effort_person_years", 0)
    total_sloc = summary.get("total_sloc", 0)
    total_packages = summary.get("total_packages", 0)
    analyzed_packages = summary.get("analyzed_packages", 0)
    failed_packages = summary.get("failed_packages", 0)

    console.print(f"💰 Total OSS Value: ${total_cost:,.0f}")
    console.print(
        f"   Estimate Range: ${total_cost_low:,.0f} - ${total_cost_high:,.0f}",
        style="dim",
    )
    console.print()
    console.print(f"⏱️  Development Effort: {total_effort_years:.1f} person-years")
    console.print()
    console.print(f"📊 Total Source Lines: {total_sloc:,}")
    console.print()
    console.print(f"📦 Packages Analyzed: {analyzed_packages} / {total_packages}")
    packages_without_sloc = summary.get("packages_without_sloc", 0)
    if packages_without_sloc > 0:
        console.print(
            f"   ℹ️  {packages_without_sloc} packages found but no SLOC data (use --clone to analyze)",
            style="dim",
        )
    if failed_packages > 0:
        console.print(f"   ⚠ {failed_packages} packages had analysis errors", style="yellow")
    console.print()

    # Top 10 Packages by Value (if any have cost estimates)
    sorted_packages = sorted(
        result.packages,
        key=lambda p: p.cost_estimate.cost_usd if p.cost_estimate else 0,
        reverse=True,
    )[:10]

    packages_with_estimates = [p for p in sorted_packages if p.cost_estimate]
    if packages_with_estimates:
        console.print("Top 10 Packages by Value", style="bold")
        console.print("─" * 64)

        table = Table(show_header=True, header_style="bold")
        table.add_column("#", width=3)
        table.add_column("Package", width=30)
        table.add_column("Value (USD)", justify="right", width=15)
        table.add_column("% of Total", justify="right", width=12)

        for i, pkg in enumerate(packages_with_estimates, 1):
            cost = pkg.cost_estimate.cost_usd
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            table.add_row(
                str(i),
                pkg.name,
                f"${cost:,.0f}",
                f"{percentage:.1f}%",
            )

        console.print(table)
        console.print()
    elif result.packages:
        # Show packages that were found but don't have cost estimates
        console.print("Packages Found (No Cost Estimates - SLOC data required)", style="bold")
        console.print("─" * 64)
        console.print("Run without --no-clone to analyze SLOC and calculate costs", style="dim")
        console.print()
        
        table = Table(show_header=True, header_style="bold")
        table.add_column("#", width=3)
        table.add_column("Package", width=30)
        table.add_column("Version", width=15)
        table.add_column("Repository", width=30)
        
        for i, pkg in enumerate(result.packages[:10], 1):
            repo = pkg.repository_url.replace(".git", "") if pkg.repository_url else "N/A"
            table.add_row(
                str(i),
                pkg.name,
                pkg.version or "N/A",
                repo[:30] + "..." if len(repo) > 30 else repo,
            )
        
        console.print(table)
        console.print()

    # Value by Language
    by_language = {}
    for pkg in result.packages:
        if pkg.cost_estimate and pkg.language:
            by_language[pkg.language] = (
                by_language.get(pkg.language, 0) + pkg.cost_estimate.cost_usd
            )

    if by_language:
        console.print("Value by Language", style="bold")
        console.print("─" * 64)

        sorted_languages = sorted(by_language.items(), key=lambda x: x[1], reverse=True)
        for lang, cost in sorted_languages[:10]:
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            bar_length = int(percentage / 2)  # Scale bar
            bar = "█" * bar_length
            console.print(
                f"  {lang:15} ${cost:>12,.0f} ({percentage:5.1f}%) {bar}",
            )
        console.print()

    # Critical Packages
    if result.critical_packages:
        console.print("⚠ Critical Packages Requiring Attention", style="bold yellow")
        console.print("─" * 64)

        table = Table(show_header=True, header_style="bold")
        table.add_column("Package", width=25)
        table.add_column("Value", justify="right", width=12)
        table.add_column("Contributors", justify="right", width=12)
        table.add_column("Last Commit", width=12)
        table.add_column("Risk Factors", width=30)

        for pkg in result.critical_packages[:10]:
            cost = pkg.cost_estimate.cost_usd if pkg.cost_estimate else 0
            contributors = (
                pkg.health.contributors_count if pkg.health else None
            )
            last_commit = (
                pkg.health.last_commit_date.strftime("%Y-%m-%d")
                if pkg.health and pkg.health.last_commit_date
                else "Unknown"
            )
            risk_factors = ", ".join(pkg.risk_factors) if pkg.risk_factors else ""

            table.add_row(
                pkg.name,
                f"${cost:,.0f}",
                str(contributors) if contributors else "N/A",
                last_commit,
                risk_factors,
            )

        console.print(table)
        console.print()

    # Methodology
    config = result.meta.get("config", {})
    methodology = config.get("methodology", "cocomo2").upper()
    region = config.get("region", "global_average")
    source_type = result.meta.get("source_type", "unknown")

    console.print("─" * 64)
    console.print(
        f"Methodology: {methodology} | Region: {region} | Source: {source_type}",
        style="dim",
    )
    console.print()

    # Return empty string - console handles output directly
    if output_file:
        console.file.close()
    return ""

