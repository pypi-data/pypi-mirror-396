"""Git history metrics analyzer."""

import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ossval.models import GitHistoryMetrics


async def analyze_git_history(
    repo_path: Path, use_cache: bool = True
) -> Optional[GitHistoryMetrics]:
    """
    Analyze git repository history for maturity and scale metrics.

    Args:
        repo_path: Path to git repository
        use_cache: Whether to use cached results

    Returns:
        GitHistoryMetrics if successful, None otherwise
    """
    if not (repo_path / ".git").exists():
        return None

    try:
        # Get total commit count
        commit_count = await _get_commit_count(repo_path)

        # Get contributor count and top contributors
        contributors = await _get_contributors(repo_path)
        contributor_count = len(contributors)

        # Get repository age
        first_commit_date = await _get_first_commit_date(repo_path)
        last_commit_date = await _get_last_commit_date(repo_path)

        age_days = 0
        age_years = 0.0
        if first_commit_date and last_commit_date:
            age_days = (last_commit_date - first_commit_date).days
            age_years = age_days / 365.25

        # Get release/tag count
        release_count = await _get_release_count(repo_path)

        # Calculate commit frequency (commits per month over last year)
        recent_commits = await _get_recent_commit_count(repo_path, days=365)
        commits_per_month = (recent_commits / 12.0) if recent_commits else 0.0

        # Get file churn metrics (files changed frequently)
        file_churn = await _get_file_churn(repo_path)

        # Get average commit size (files per commit)
        avg_files_per_commit = await _get_avg_files_per_commit(repo_path)

        # Calculate bus factor (simplified: top contributors with >5% of commits)
        bus_factor = _calculate_bus_factor(contributors, commit_count)

        return GitHistoryMetrics(
            commit_count=commit_count,
            contributor_count=contributor_count,
            age_days=age_days,
            age_years=age_years,
            first_commit_date=first_commit_date,
            last_commit_date=last_commit_date,
            release_count=release_count,
            commits_per_month=commits_per_month,
            avg_files_per_commit=avg_files_per_commit,
            high_churn_files=file_churn,
            bus_factor=bus_factor,
        )

    except Exception as e:
        return None


async def _get_commit_count(repo_path: Path) -> int:
    """Get total commit count."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "rev-list",
            "--count",
            "HEAD",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return int(stdout.decode().strip())
    except Exception:
        return 0


async def _get_contributors(repo_path: Path) -> Dict[str, int]:
    """Get contributor list with commit counts."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "shortlog",
            "-sn",
            "--all",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()

        contributors = {}
        for line in stdout.decode().splitlines():
            match = re.match(r"\s*(\d+)\s+(.+)", line)
            if match:
                count, name = match.groups()
                contributors[name] = int(count)

        return contributors
    except Exception:
        return {}


async def _get_first_commit_date(repo_path: Path) -> Optional[datetime]:
    """Get date of first commit."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "--reverse",
            "--format=%aI",
            "--max-count=1",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        date_str = stdout.decode().strip()
        if date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        pass
    return None


async def _get_last_commit_date(repo_path: Path) -> Optional[datetime]:
    """Get date of last commit."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "--format=%aI",
            "--max-count=1",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        date_str = stdout.decode().strip()
        if date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        pass
    return None


async def _get_release_count(repo_path: Path) -> int:
    """Get count of releases/tags."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "tag",
            "--list",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        tags = stdout.decode().strip().split("\n")
        return len([t for t in tags if t])
    except Exception:
        return 0


async def _get_recent_commit_count(repo_path: Path, days: int = 365) -> int:
    """Get commit count in recent period."""
    try:
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        proc = await asyncio.create_subprocess_exec(
            "git",
            "rev-list",
            "--count",
            f"--since={since_date}",
            "HEAD",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return int(stdout.decode().strip())
    except Exception:
        return 0


async def _get_file_churn(repo_path: Path, top_n: int = 10) -> int:
    """Get count of high-churn files (changed frequently)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "--format=",
            "--name-only",
            "--since=1.year",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()

        file_changes: Dict[str, int] = {}
        for line in stdout.decode().splitlines():
            line = line.strip()
            if line:
                file_changes[line] = file_changes.get(line, 0) + 1

        # Count files changed more than 10 times in the last year
        high_churn = len([f for f, count in file_changes.items() if count > 10])
        return high_churn
    except Exception:
        return 0


async def _get_avg_files_per_commit(repo_path: Path) -> float:
    """Get average files changed per commit."""
    try:
        # Get total files changed across all commits
        proc1 = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "--format=",
            "--name-only",
            "--all",
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout1, _ = await proc1.communicate()
        file_count = len([line for line in stdout1.decode().splitlines() if line.strip()])

        # Get commit count
        commit_count = await _get_commit_count(repo_path)

        if commit_count > 0:
            return file_count / commit_count
        return 0.0
    except Exception:
        return 0.0


def _calculate_bus_factor(contributors: Dict[str, int], total_commits: int) -> int:
    """
    Calculate bus factor (number of contributors needed to account for 50% of commits).

    Args:
        contributors: Dict mapping contributor name to commit count
        total_commits: Total commit count

    Returns:
        Bus factor (minimum number of people who do 50% of work)
    """
    if not contributors or total_commits == 0:
        return 1

    # Sort by commit count descending
    sorted_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)

    cumulative = 0
    bus_factor = 0
    threshold = total_commits * 0.5

    for name, commits in sorted_contributors:
        cumulative += commits
        bus_factor += 1
        if cumulative >= threshold:
            break

    return max(1, bus_factor)
