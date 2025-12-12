"""Go go.mod parser."""

import re
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class GoModParser(BaseParser):
    """Parser for Go go.mod files."""

    # Pattern: module path with optional version
    REQUIRE_PATTERN = re.compile(r"^\s*require\s+([^\s]+)\s+([^\s]+)\s*$")
    REQUIRE_BLOCK_START = re.compile(r"^\s*require\s*\($")

    def can_parse(self, filepath: str) -> bool:
        """Check if file is go.mod."""
        path = Path(filepath)
        return path.name.lower() == "go.mod"

    def parse(self, filepath: str) -> ParseResult:
        """Parse go.mod file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r") as f:
                in_require_block = False
                for line in f:
                    line = line.strip()

                    # Check for require block start
                    if self.REQUIRE_BLOCK_START.match(line):
                        in_require_block = True
                        continue

                    # Check for block end
                    if in_require_block and line == ")":
                        in_require_block = False
                        continue

                    # Parse require line
                    match = self.REQUIRE_PATTERN.match(line)
                    if match:
                        module_path, version = match.groups()
                        # Remove leading/trailing quotes if present
                        module_path = module_path.strip('"')
                        version = version.strip('"')

                        packages.append(
                            Package(
                                name=module_path,
                                version=self._normalize_version(version),
                                ecosystem="go",
                            )
                        )
                    elif line.startswith("require ") and not in_require_block:
                        # Single-line require
                        parts = line.split()
                        if len(parts) >= 3:
                            module_path = parts[1].strip('"')
                            version = parts[2].strip('"')
                            packages.append(
                                Package(
                                    name=module_path,
                                    version=self._normalize_version(version),
                                    ecosystem="go",
                                )
                            )

        except Exception as e:
            errors.append(f"Failed to parse go.mod: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.GO_MOD,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

