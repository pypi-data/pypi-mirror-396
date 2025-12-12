"""poetry.lock parser for Poetry."""

import re
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class PoetryLockParser(BaseParser):
    """Parser for poetry.lock files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is poetry.lock."""
        path = Path(filepath)
        return path.name.lower() == "poetry.lock"

    def parse(self, filepath: str) -> ParseResult:
        """Parse poetry.lock file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Poetry.lock uses TOML format
            # Find [[package]] sections - handle multiline
            package_pattern = re.compile(
                r'\[\[package\]\]\s+name\s*=\s*"([^"]+)"[^\[]*?version\s*=\s*"([^"]+)"',
                re.MULTILINE | re.DOTALL,
            )

            matches = package_pattern.finditer(content)
            for match in matches:
                name = match.group(1)
                version = match.group(2)
                # Skip the root package (usually has no name or is the project itself)
                if name and name != "root":
                    packages.append(
                        Package(
                            name=name,
                            version=self._normalize_version(version),
                            ecosystem="pypi",
                        )
                    )

        except Exception as e:
            errors.append(f"Failed to parse poetry.lock: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.POETRY,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

