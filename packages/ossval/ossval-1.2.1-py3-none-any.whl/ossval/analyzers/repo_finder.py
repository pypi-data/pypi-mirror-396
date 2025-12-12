"""Repository URL discovery using purl2src."""

import subprocess
from typing import Optional


def _generate_purl(package_name: str, ecosystem: str, version: Optional[str] = None) -> str:
    """Generate Package URL (PURL) from package info."""
    purl = f"pkg:{ecosystem}/{package_name}"
    if version:
        purl = f"{purl}@{version}"
    return purl


async def find_repository_url(
    package_name: str, ecosystem: Optional[str] = None, version: Optional[str] = None
) -> Optional[str]:
    """
    Find repository URL for a package.
    
    Strategy:
    1. Try registry APIs first (fastest)
    2. If that fails, use purl2src to get download URL, download package, extract repo URL from metadata

    Args:
        package_name: Package name
        ecosystem: Package ecosystem (pypi, npm, cargo, etc.)
        version: Optional package version

    Returns:
        Repository URL if found, None otherwise
    """
    if not ecosystem:
        return None

    ecosystem = ecosystem.lower()
    
    # First, try registry APIs (fastest)
    repo_url = await _find_repo_from_registry(package_name, ecosystem, version)
    if repo_url:
        return repo_url
    
    # If registry lookup fails, try using purl2src to download and inspect
    # Generate PURL
    purl = _generate_purl(package_name, ecosystem, version)
    
    try:
        # Use purl2src to get download URL
        result = subprocess.run(
            ["purl2src", purl, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        if result.returncode == 0 and result.stdout:
            import json
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                download_url = data[0].get("download_url")
                if download_url:
                    # Download and extract repo URL from package metadata
                    repo_url = await _extract_repo_from_downloaded_package(
                        download_url, package_name, ecosystem
                    )
                    if repo_url:
                        return repo_url
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError, Exception):
        # If purl2src fails, return None
        pass
    
    return None


async def _extract_repo_from_downloaded_package(
    download_url: str, package_name: str, ecosystem: str
) -> Optional[str]:
    """Download package and extract repository URL from metadata."""
    # For now, skip this as it's expensive
    # In the future, we could download, extract, and read package.json/pyproject.toml/etc.
    return None


async def _find_repo_from_registry(
    package_name: str, ecosystem: str, version: Optional[str] = None
) -> Optional[str]:
    """Fallback: Find repository URL by querying package registries."""
    try:
        if ecosystem == "pypi":
            return await _find_pypi_repo(package_name)
        elif ecosystem == "npm":
            return await _find_npm_repo(package_name)
        elif ecosystem == "cargo":
            return await _find_cargo_repo(package_name)
        elif ecosystem == "go":
            return _find_go_repo(package_name)
        elif ecosystem == "rubygems":
            return await _find_rubygems_repo(package_name)
        elif ecosystem == "maven":
            return _find_maven_repo(package_name)
    except Exception:
        pass

    return None


def _is_valid_git_url(url: str) -> bool:
    """Check if URL looks like a valid git repository."""
    if not url:
        return False
    url_lower = url.lower()
    # Check for common git hosting platforms (with or without trailing slash)
    return (
        "github.com" in url_lower
        or "gitlab.com" in url_lower
        or "bitbucket.org" in url_lower
        or url_lower.startswith("git+")
        or url_lower.endswith(".git")
        or url_lower.endswith(".git/")
        or url_lower.startswith("git://")
    )


def _normalize_git_url(url: str) -> str:
    """Normalize git URL to standard HTTPS format."""
    from urllib.parse import urlparse
    
    if not url:
        return url

    # Remove git+ prefix
    if url.startswith("git+"):
        url = url[4:]

    # Remove trailing slash
    if url.endswith("/"):
        url = url[:-1]

    # Remove .git suffix if present (we'll add it back)
    if url.endswith(".git"):
        url = url[:-4]

    # Convert ssh to https
    if url.startswith("git@"):
        # git@github.com:user/repo -> https://github.com/user/repo
        url = url[4:]  # Remove "git@"
        url = url.replace(":", "/", 1)  # Replace first ":" with "/"
        url = f"https://{url}"

    # Ensure it starts with http:// or https://
    if not url.startswith(("http://", "https://")):
        if "github.com" in url or "gitlab.com" in url or "bitbucket.org" in url:
            url = f"https://{url}"

    # Add .git suffix if it's a GitHub/GitLab/Bitbucket URL
    try:
        parsed = urlparse(url)
        if parsed.netloc in ["github.com", "gitlab.com", "bitbucket.org"]:
            if not url.endswith(".git"):
                url = f"{url}.git"
    except Exception:
        pass

    return url


async def _find_pypi_repo(package_name: str) -> Optional[str]:
    """Find repository URL from PyPI."""
    import httpx
    
    url = f"https://pypi.org/pypi/{package_name}/json"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                info = data.get("info", {})
                project_urls = info.get("project_urls", {})
                # Try various URL fields
                for key in ["Source", "Source Code", "Repository", "Homepage"]:
                    if key in project_urls:
                        repo_url = project_urls[key]
                        if repo_url:
                            # Check if it's a git URL
                            if _is_valid_git_url(repo_url):
                                return _normalize_git_url(repo_url)
                # Try homepage
                homepage = info.get("home_page")
                if homepage and _is_valid_git_url(homepage):
                    return _normalize_git_url(homepage)
        except Exception:
            pass
    return None


async def _find_npm_repo(package_name: str) -> Optional[str]:
    """Find repository URL from npm registry."""
    import httpx
    
    url = f"https://registry.npmjs.org/{package_name}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                # Get latest version info
                latest = data.get("dist-tags", {}).get("latest")
                if latest:
                    version_data = data.get("versions", {}).get(latest, {})
                    repository = version_data.get("repository", {})
                    if isinstance(repository, dict):
                        repo_url = repository.get("url", "")
                    else:
                        repo_url = repository
                    if repo_url and _is_valid_git_url(repo_url):
                        return _normalize_git_url(repo_url)
        except Exception:
            pass
    return None


async def _find_cargo_repo(package_name: str) -> Optional[str]:
    """Find repository URL from crates.io."""
    import httpx
    
    url = f"https://crates.io/api/v1/crates/{package_name}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                crate = data.get("crate", {})
                repository = crate.get("repository")
                if repository and _is_valid_git_url(repository):
                    return _normalize_git_url(repository)
        except Exception:
            pass
    return None


def _find_go_repo(package_name: str) -> Optional[str]:
    """Find repository URL from Go module path."""
    # Go modules often follow github.com/user/repo pattern
    if package_name.startswith("github.com/"):
        return f"https://{package_name}.git"
    elif package_name.startswith("gitlab.com/"):
        return f"https://{package_name}.git"
    elif package_name.startswith("bitbucket.org/"):
        return f"https://{package_name}.git"
    # Try to infer from common patterns
    elif "." in package_name and "/" in package_name:
        # Might be a domain-based module path
        parts = package_name.split("/")
        if len(parts) >= 3:
            # Assume it's a git repository
            return f"https://{package_name}.git"
    return None


async def _find_rubygems_repo(package_name: str) -> Optional[str]:
    """Find repository URL from RubyGems."""
    import httpx
    
    url = f"https://rubygems.org/api/v1/gems/{package_name}.json"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                source_code_uri = data.get("source_code_uri")
                if source_code_uri and _is_valid_git_url(source_code_uri):
                    return _normalize_git_url(source_code_uri)
                homepage_uri = data.get("homepage_uri")
                if homepage_uri and _is_valid_git_url(homepage_uri):
                    return _normalize_git_url(homepage_uri)
        except Exception:
            pass
    return None


def _find_maven_repo(package_name: str) -> Optional[str]:
    """Find repository URL from Maven coordinates."""
    # Maven coordinates: group:artifact
    # Often maps to GitHub: github.com/group/artifact
    if ":" in package_name:
        parts = package_name.split(":")
        if len(parts) >= 2:
            group = parts[0]
            artifact = parts[1]
            # Common pattern: com.company.project -> github.com/company/project
            if group.startswith("com."):
                org = group.split(".")[-1]
                return f"https://github.com/{org}/{artifact}.git"
            elif group.startswith("org."):
                org = group.split(".")[-1]
                return f"https://github.com/{org}/{artifact}.git"
    return None


# Duplicate _normalize_git_url removed - using the one defined earlier

