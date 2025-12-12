"""yarn.lock parser for Yarn."""

import re
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class YarnLockParser(BaseParser):
    """Parser for yarn.lock files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is yarn.lock."""
        path = Path(filepath)
        return path.name.lower() == "yarn.lock"

    def parse(self, filepath: str) -> ParseResult:
        """Parse yarn.lock file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Yarn.lock format: "package-name@version":
            #   version "x.y.z"
            pattern = re.compile(
                r'"([^@"]+)@([^"]+)"\s*:\s*version\s+"([^"]+)"',
                re.MULTILINE,
            )

            matches = pattern.finditer(content)
            seen = set()
            for match in matches:
                name = match.group(1)
                spec = match.group(2)  # Version specifier
                version = match.group(3)  # Actual resolved version

                # Use name@spec as key to avoid duplicates
                key = f"{name}@{spec}"
                if key not in seen:
                    seen.add(key)
                    packages.append(
                        Package(
                            name=name,
                            version=self._normalize_version(version),
                            ecosystem="npm",
                        )
                    )

        except Exception as e:
            errors.append(f"Failed to parse yarn.lock: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.YARN,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

