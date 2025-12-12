"""SPDX SBOM parser."""

import json
import re
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class SPDXParser(BaseParser):
    """Parser for SPDX SBOM format (JSON and tag-value)."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is SPDX format."""
        path = Path(filepath)
        if path.suffix.lower() == ".json":
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    return "spdxVersion" in data or "SPDXID" in data
            except Exception:
                return False
        elif path.suffix.lower() in [".spdx", ".txt", ""]:
            # Tag-value format
            try:
                with open(filepath, "r") as f:
                    first_line = f.readline()
                    return "SPDXVersion:" in first_line or "SPDXID:" in first_line
            except Exception:
                return False
        return False

    @staticmethod
    def _is_git_url(url: str) -> bool:
        """
        Safely check if a URL is a git repository URL.

        Checks:
        - Protocol starts with git+ (e.g., git+https://)
        - Domain is github.com, gitlab.com, or bitbucket.org

        Args:
            url: URL string to check

        Returns:
            True if it's a git URL, False otherwise
        """
        if not url or url == "NOASSERTION":
            return False

        # Check if it starts with git+ protocol
        if url.startswith("git+"):
            return True

        # Parse URL and check domain
        try:
            # Handle git@ SSH URLs
            if url.startswith("git@"):
                return True

            parsed = urlparse(url if "://" in url else f"https://{url}")
            return parsed.netloc in ["github.com", "gitlab.com", "bitbucket.org"]
        except Exception:
            return False

    def parse(self, filepath: str) -> ParseResult:
        """Parse SPDX SBOM file."""
        path = Path(filepath)
        errors = []
        warnings = []
        packages: List[Package] = []

        try:
            if path.suffix.lower() == ".json":
                packages = self._parse_json(filepath)
            else:
                packages = self._parse_tag_value(filepath)
        except Exception as e:
            errors.append(f"Failed to parse SPDX file: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.SPDX,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

    def _parse_json(self, filepath: str) -> List[Package]:
        """Parse SPDX JSON format."""
        with open(filepath, "r") as f:
            data = json.load(f)

        packages = []
        packages_data = data.get("packages", [])

        for pkg_data in packages_data:
            name = pkg_data.get("name", "")
            version_info = pkg_data.get("versionInfo")
            version = version_info if version_info else None

            # Extract external references for repository URL
            external_refs = pkg_data.get("externalRefs", [])
            repository_url = None
            ecosystem = None

            for ref in external_refs:
                ref_type = ref.get("referenceType")
                ref_locator = ref.get("referenceLocator", "")

                if ref_type == "vcs":
                    repository_url = ref_locator
                elif ref_type == "purl":
                    # Extract ecosystem from Package URL
                    ecosystem = self._extract_ecosystem_from_purl(ref_locator)

            # Extract download location as fallback
            if not repository_url:
                download_location = pkg_data.get("downloadLocation", "")
                if self._is_git_url(download_location):
                    # Try to extract git URL
                    repository_url = download_location.replace("git+", "").split("#")[0]

            package = Package(
                name=name,
                version=self._normalize_version(version),
                ecosystem=ecosystem,
                repository_url=repository_url,
            )
            packages.append(package)

        return packages

    def _parse_tag_value(self, filepath: str) -> List[Package]:
        """Parse SPDX tag-value format."""
        packages = []
        current_package = {}
        in_package = False

        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("PackageName:"):
                    if in_package and current_package.get("name"):
                        # Save previous package
                        packages.append(self._create_package_from_dict(current_package))
                        current_package = {}
                    current_package["name"] = line.split(":", 1)[1].strip()
                    in_package = True
                elif line.startswith("PackageVersion:") and in_package:
                    current_package["version"] = line.split(":", 1)[1].strip()
                elif line.startswith("ExternalRef:") and in_package:
                    # ExternalRef: PACKAGE-MANAGER pkg:npm/package@version
                    ref_line = line.split(":", 1)[1].strip()
                    if "pkg:" in ref_line:
                        # Extract purl
                        purl_match = re.search(r"pkg:([^\s]+)", ref_line)
                        if purl_match:
                            purl = purl_match.group(1)
                            ecosystem = self._extract_ecosystem_from_purl(f"pkg:{purl}")
                            if ecosystem:
                                current_package["ecosystem"] = ecosystem
                    else:
                        # Try to extract repository URL
                        url_match = re.search(r"(https?://[^\s]+|git\+[^\s]+)", ref_line)
                        if url_match and self._is_git_url(url_match.group(1)):
                            current_package["repository_url"] = url_match.group(1)
                elif line.startswith("PackageDownloadLocation:") and in_package:
                    download_loc = line.split(":", 1)[1].strip()
                    if self._is_git_url(download_loc):
                        current_package["repository_url"] = (
                            download_loc.replace("git+", "").split("#")[0]
                        )

            # Don't forget the last package
            if in_package and current_package.get("name"):
                packages.append(self._create_package_from_dict(current_package))

        return packages

    def _create_package_from_dict(self, pkg_dict: dict) -> Package:
        """Create Package object from dictionary."""
        return Package(
            name=pkg_dict.get("name", ""),
            version=self._normalize_version(pkg_dict.get("version")),
            ecosystem=pkg_dict.get("ecosystem"),
            repository_url=pkg_dict.get("repository_url"),
        )

    def _extract_ecosystem_from_purl(self, purl: str) -> str | None:
        """Extract ecosystem from Package URL."""
        if not purl or not purl.startswith("pkg:"):
            return None

        try:
            parts = purl[4:].split("/")
            if parts:
                ecosystem = parts[0].split("@")[0]
                ecosystem_map = {
                    "npm": "npm",
                    "pypi": "pypi",
                    "maven": "maven",
                    "cargo": "cargo",
                    "golang": "go",
                    "gem": "rubygems",
                    "composer": "composer",
                    "nuget": "nuget",
                    "swiftpm": "swift",
                }
                return ecosystem_map.get(ecosystem, ecosystem)
        except Exception:
            pass

        return None

