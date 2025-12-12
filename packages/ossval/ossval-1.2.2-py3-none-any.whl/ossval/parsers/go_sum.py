"""go.sum parser for Go modules."""

import re
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class GoSumParser(BaseParser):
    """Parser for go.sum files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is go.sum."""
        path = Path(filepath)
        return path.name.lower() == "go.sum"

    def parse(self, filepath: str) -> ParseResult:
        """Parse go.sum file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue

                    # go.sum format: module_path version hash
                    # Example: github.com/user/repo v1.2.3 h1:abc123...
                    parts = line.split()
                    if len(parts) >= 2:
                        module_path = parts[0]
                        version = parts[1]
                        # Remove h1: prefix if present
                        if version.startswith("h1:") or version.startswith("go1."):
                            continue  # Skip hash lines

                        packages.append(
                            Package(
                                name=module_path,
                                version=self._normalize_version(version),
                                ecosystem="go",
                            )
                        )

        except Exception as e:
            errors.append(f"Failed to parse go.sum: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.GO_SUM,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

