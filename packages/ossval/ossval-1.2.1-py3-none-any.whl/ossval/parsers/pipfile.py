"""Pipfile.lock parser for Pipenv."""

import json
from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class PipfileLockParser(BaseParser):
    """Parser for Pipfile.lock files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is Pipfile.lock."""
        path = Path(filepath)
        return path.name.lower() == "pipfile.lock"

    def parse(self, filepath: str) -> ParseResult:
        """Parse Pipfile.lock file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Pipfile.lock has "default" and "develop" sections
            default_deps = data.get("default", {})
            develop_deps = data.get("develop", {})

            all_deps = {**default_deps, **develop_deps}

            for name, dep_info in all_deps.items():
                if isinstance(dep_info, dict):
                    version = dep_info.get("version", "").strip()
                    # Remove == prefix if present
                    if version.startswith("=="):
                        version = version[2:]
                    packages.append(
                        Package(
                            name=name,
                            version=self._normalize_version(version) if version else None,
                            ecosystem="pypi",
                        )
                    )

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in Pipfile.lock: {str(e)}")
        except Exception as e:
            errors.append(f"Failed to parse Pipfile.lock: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.PIPFILE,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

