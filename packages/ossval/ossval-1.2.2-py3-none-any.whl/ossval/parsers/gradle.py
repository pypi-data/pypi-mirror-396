"""Gradle build.gradle parser."""

import re
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class GradleParser(BaseParser):
    """Parser for Gradle build.gradle files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is build.gradle."""
        path = Path(filepath)
        name = path.name.lower()
        return name in ["build.gradle", "build.gradle.kts"]

    def parse(self, filepath: str) -> ParseResult:
        """Parse build.gradle file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Gradle dependency formats:
            # implementation 'group:artifact:version'
            # implementation("group:artifact:version")
            # compile 'group:artifact:version'
            # testImplementation 'group:artifact:version'

            # Pattern for dependencies
            patterns = [
                # Single quotes
                re.compile(
                    r"(?:implementation|compile|api|testImplementation|testCompile)\s+['\"]([^'\"]+)['\"]",
                    re.MULTILINE,
                ),
                # Parentheses
                re.compile(
                    r"(?:implementation|compile|api|testImplementation|testCompile)\s*\(['\"]([^'\"]+)['\"]\)",
                    re.MULTILINE,
                ),
            ]

            seen = set()
            for pattern in patterns:
                matches = pattern.finditer(content)
                for match in matches:
                    dep_spec = match.group(1)
                    # Skip if it's a project dependency or file dependency
                    if dep_spec.startswith("project") or dep_spec.startswith("files"):
                        continue

                    if dep_spec not in seen:
                        seen.add(dep_spec)
                        # Parse group:artifact:version
                        parts = dep_spec.split(":")
                        if len(parts) >= 2:
                            group = parts[0]
                            artifact = parts[1]
                            version = parts[2] if len(parts) >= 3 else None
                            name = f"{group}:{artifact}"
                            packages.append(
                                Package(
                                    name=name,
                                    version=self._normalize_version(version),
                                    ecosystem="maven",
                                )
                            )

        except Exception as e:
            errors.append(f"Failed to parse build.gradle: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.GRADLE,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

