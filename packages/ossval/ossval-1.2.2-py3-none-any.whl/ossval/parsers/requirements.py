"""Python requirements.txt parser."""

import re
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class RequirementsParser(BaseParser):
    """Parser for Python requirements.txt files."""

    # Pattern: package==version or package>=version, etc.
    REQUIREMENT_PATTERN = re.compile(
        r"^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*(==|>=|<=|>|<|~=|\^|!=)\s*([0-9.]+.*)$"
    )
    # Pattern: just package name
    NAME_ONLY_PATTERN = re.compile(r"^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*$")

    def can_parse(self, filepath: str) -> bool:
        """Check if file is requirements.txt."""
        path = Path(filepath)
        return path.name.lower() == "requirements.txt" or (
            path.suffix.lower() == ".txt" and "requirement" in path.name.lower()
        )

    def parse(self, filepath: str) -> ParseResult:
        """Parse requirements.txt file."""
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

                    # Remove inline comments
                    if "#" in line:
                        line = line.split("#")[0].strip()

                    # Skip -r, -e, -- flags
                    if line.startswith("-"):
                        continue

                    # Try to parse requirement
                    match = self.REQUIREMENT_PATTERN.match(line)
                    if match:
                        name, op, version = match.groups()
                        # For now, just extract version (ignore operator)
                        packages.append(
                            Package(
                                name=name,
                                version=self._normalize_version(version),
                                ecosystem="pypi",
                            )
                        )
                    else:
                        # Try name only
                        match = self.NAME_ONLY_PATTERN.match(line)
                        if match:
                            name = match.group(1)
                            packages.append(
                                Package(name=name, version=None, ecosystem="pypi")
                            )
                        else:
                            warnings.append(
                                f"Line {line_num}: Could not parse '{line}' - skipping"
                            )

        except Exception as e:
            errors.append(f"Failed to parse requirements.txt: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.REQUIREMENTS,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )
