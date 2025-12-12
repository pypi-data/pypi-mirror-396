"""package-lock.json parser for npm."""

import json
from pathlib import Path
from typing import Dict, List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class PackageLockParser(BaseParser):
    """Parser for package-lock.json files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is package-lock.json."""
        path = Path(filepath)
        return path.name.lower() == "package-lock.json"

    def parse(self, filepath: str) -> ParseResult:
        """Parse package-lock.json file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # package-lock.json v2+ has "packages" object
            # v1 has "dependencies" object
            if "packages" in data:
                # v2+ format
                packages_data = data["packages"]
                for pkg_path, pkg_info in packages_data.items():
                    # Skip root package
                    if pkg_path == "":
                        continue
                    if isinstance(pkg_info, dict) and "version" in pkg_info:
                        name = pkg_info.get("name")
                        version = pkg_info.get("version")
                        if name and version:
                            packages.append(
                                Package(
                                    name=name,
                                    version=self._normalize_version(version),
                                    ecosystem="npm",
                                )
                            )
            elif "dependencies" in data:
                # v1 format
                deps = data["dependencies"]
                self._extract_dependencies(deps, packages)

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in package-lock.json: {str(e)}")
        except Exception as e:
            errors.append(f"Failed to parse package-lock.json: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.PACKAGE_LOCK,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

    def _extract_dependencies(self, deps: Dict, packages: List[Package], seen: set = None):
        """Recursively extract dependencies from v1 format."""
        if seen is None:
            seen = set()

        for name, dep_info in deps.items():
            if name in seen:
                continue
            seen.add(name)

            if isinstance(dep_info, dict):
                version = dep_info.get("version")
                if version:
                    packages.append(
                        Package(
                            name=name,
                            version=self._normalize_version(version),
                            ecosystem="npm",
                        )
                    )
                # Recurse into nested dependencies
                if "dependencies" in dep_info:
                    self._extract_dependencies(dep_info["dependencies"], packages, seen)

