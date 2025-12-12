"""Simple text format parser for package lists."""

import re
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class SimpleParser(BaseParser):
    """Parser for simple text format with one package per line."""

    # Patterns for different package formats
    PATTERNS = {
        "pip": re.compile(r"^([a-zA-Z0-9_-]+)\s*==\s*([0-9.]+.*)$"),  # requests==2.31.0
        "npm": re.compile(r"^([a-zA-Z0-9_-]+)\s*@\s*([0-9.]+.*)$"),  # lodash@4.17.21
        "maven": re.compile(
            r"^([a-zA-Z0-9_.-]+):([a-zA-Z0-9_.-]+):([0-9.]+.*)$"
        ),  # com.google.guava:guava:32.1.2
        "name_only": re.compile(r"^([a-zA-Z0-9_-]+)\s*$"),  # tokio
    }

    def can_parse(self, filepath: str) -> bool:
        """Check if file looks like a simple text package list."""
        path = Path(filepath)
        # Accept .txt files or files with no extension
        if path.suffix.lower() in [".txt", ""] or path.name in [
            "requirements.txt",
            "packages.txt",
        ]:
            try:
                with open(filepath, "r") as f:
                    first_line = f.readline().strip()
                    # Check if it matches any of our patterns
                    for pattern in self.PATTERNS.values():
                        if pattern.match(first_line):
                            return True
                    # Also accept if it's a simple package name
                    if first_line and not first_line.startswith("#"):
                        return True
            except Exception:
                pass
        return False

    def parse(self, filepath: str) -> ParseResult:
        """Parse simple text format package list."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    package = self._parse_line(line)
                    if package:
                        packages.append(package)
                    else:
                        warnings.append(
                            f"Line {line_num}: Could not parse '{line}' - skipping"
                        )
        except Exception as e:
            errors.append(f"Failed to read file: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.SIMPLE,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

    def _parse_line(self, line: str) -> Package | None:
        """Parse a single line into a Package object."""
        line = line.strip()

        # Try pip format: package==version
        match = self.PATTERNS["pip"].match(line)
        if match:
            name, version = match.groups()
            return Package(
                name=name,
                version=self._normalize_version(version),
                ecosystem="pypi",
            )

        # Try npm format: package@version
        match = self.PATTERNS["npm"].match(line)
        if match:
            name, version = match.groups()
            return Package(
                name=name,
                version=self._normalize_version(version),
                ecosystem="npm",
            )

        # Try Maven format: group:artifact:version
        match = self.PATTERNS["maven"].match(line)
        if match:
            group, artifact, version = match.groups()
            name = f"{group}:{artifact}"
            return Package(
                name=name,
                version=self._normalize_version(version),
                ecosystem="maven",
            )

        # Try name only (will need to lookup version later)
        match = self.PATTERNS["name_only"].match(line)
        if match:
            name = match.group(1)
            # Try to infer ecosystem from common patterns
            ecosystem = None
            if "." in name and ":" in name:
                ecosystem = "maven"
            return Package(name=name, version=None, ecosystem=ecosystem)

        return None

