"""Repository health metrics from GitHub API."""

from datetime import datetime, timedelta
from typing import Optional

import httpx

from ossval.models import HealthMetrics


async def analyze_health(
    repository_url: str, github_token: Optional[str] = None
) -> Optional[HealthMetrics]:
    """
    Analyze repository health metrics from GitHub API.

    Args:
        repository_url: Repository URL (must be GitHub)
        github_token: Optional GitHub API token

    Returns:
        HealthMetrics if successful, None otherwise
    """
    if not repository_url or "github.com" not in repository_url.lower():
        return None

    # Extract owner/repo from URL
    owner, repo = _extract_github_repo(repository_url)
    if not owner or not repo:
        return None

    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Get repository info
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            repo_response = await client.get(repo_url, headers=headers)

            if repo_response.status_code != 200:
                return None

            repo_data = repo_response.json()

            # Get contributors
            contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
            contributors_response = await client.get(
                contributors_url, headers=headers, params={"per_page": 1, "anon": "true"}
            )

            contributors_count = None
            if contributors_response.status_code == 200:
                # Get total count from Link header if available
                link_header = contributors_response.headers.get("Link", "")
                if link_header:
                    # Try to extract count from Link header
                    # This is a simplified approach
                    contributors_data = contributors_response.json()
                    contributors_count = len(contributors_data)
                else:
                    contributors_data = contributors_response.json()
                    contributors_count = len(contributors_data)

            # Calculate bus factor (number of contributors with significant commits)
            # For now, use contributors_count as approximation
            bus_factor = contributors_count

            # Parse dates
            created_date = None
            if repo_data.get("created_at"):
                created_date = datetime.fromisoformat(
                    repo_data["created_at"].replace("Z", "+00:00")
                )

            last_commit_date = None
            if repo_data.get("pushed_at"):
                last_commit_date = datetime.fromisoformat(
                    repo_data["pushed_at"].replace("Z", "+00:00")
                )

            # Check if actively maintained (commits in last 6 months)
            is_actively_maintained = False
            if last_commit_date:
                six_months_ago = datetime.now(last_commit_date.tzinfo) - timedelta(days=180)
                is_actively_maintained = last_commit_date > six_months_ago

            return HealthMetrics(
                stars=repo_data.get("stargazers_count"),
                forks=repo_data.get("forks_count"),
                contributors_count=contributors_count,
                open_issues=repo_data.get("open_issues_count"),
                last_commit_date=last_commit_date,
                created_date=created_date,
                license=repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                has_funding=repo_data.get("has_sponsorships", False),
                has_security_policy=repo_data.get("security_and_analysis", {}).get(
                    "advanced_security", {}
                ).get("status")
                == "enabled",
                bus_factor=bus_factor,
                is_actively_maintained=is_actively_maintained,
            )

        except Exception:
            return None


def _extract_github_repo(repository_url: str) -> tuple[Optional[str], Optional[str]]:
    """Extract owner and repo name from GitHub URL."""
    import re

    # Patterns: https://github.com/owner/repo.git or https://github.com/owner/repo
    patterns = [
        r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"github\.com/([^/]+)/([^/]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, repository_url)
        if match:
            return match.group(1), match.group(2).replace(".git", "")

    return None, None

