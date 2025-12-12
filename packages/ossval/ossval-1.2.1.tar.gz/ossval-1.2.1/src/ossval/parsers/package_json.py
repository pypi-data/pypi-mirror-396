"""npm package.json parser."""

import json
from pathlib import Path
from typing import Dict, List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class PackageJsonParser(BaseParser):
    """Parser for npm package.json files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is package.json."""
        path = Path(filepath)
        return path.name.lower() == "package.json"

    def parse(self, filepath: str) -> ParseResult:
        """Parse package.json file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Parse dependencies
            deps = data.get("dependencies", {})
            dev_deps = data.get("devDependencies", {})
            peer_deps = data.get("peerDependencies", {})

            all_deps = {**deps, **dev_deps, **peer_deps}

            for name, version_spec in all_deps.items():
                # Extract version from spec (handle ^, ~, >=, etc.)
                version = self._extract_version(version_spec)
                packages.append(
                    Package(
                        name=name,
                        version=self._normalize_version(version),
                        ecosystem="npm",
                    )
                )

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in package.json: {str(e)}")
        except Exception as e:
            errors.append(f"Failed to parse package.json: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.PACKAGE_JSON,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

    def _extract_version(self, version_spec: str) -> str | None:
        """Extract version from npm version spec (^1.2.3, ~1.2.3, >=1.2.3, etc.)."""
        if not version_spec:
            return None

        # Remove operators
        version_spec = version_spec.strip()
        if version_spec.startswith("^") or version_spec.startswith("~"):
            return version_spec[1:]
        if version_spec.startswith(">=") or version_spec.startswith("<="):
            return version_spec[2:]
        if version_spec.startswith(">") or version_spec.startswith("<"):
            return version_spec[1:]
        if version_spec.startswith("="):
            return version_spec[1:]

        # If it's a URL or file path, return None
        if version_spec.startswith(("http://", "https://", "file:", "git+")):
            return None

        return version_spec

