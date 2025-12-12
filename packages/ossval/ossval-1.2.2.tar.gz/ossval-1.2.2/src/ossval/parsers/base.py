"""Base parser interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ossval.models import Package, SourceType


@dataclass
class ParseResult:
    """Result from parsing a file."""

    packages: List[Package]
    source_type: SourceType
    source_file: str
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        """Initialize default lists."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class BaseParser(ABC):
    """Abstract base class for all parsers."""

    @abstractmethod
    def can_parse(self, filepath: str) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            filepath: Path to the file to check

        Returns:
            True if this parser can handle the file
        """
        pass

    @abstractmethod
    def parse(self, filepath: str) -> ParseResult:
        """
        Parse a file and extract package information.

        Args:
            filepath: Path to the file to parse

        Returns:
            ParseResult with extracted packages
        """
        pass

    def _normalize_version(self, version: Optional[str]) -> Optional[str]:
        """Normalize version string (remove leading v, etc.)."""
        if not version:
            return None
        version = version.strip()
        if version.startswith("v"):
            version = version[1:]
        return version if version else None

    def _extract_ecosystem_from_file(self, filepath: str) -> Optional[str]:
        """Try to infer ecosystem from file extension or path."""
        path = Path(filepath)
        ext = path.suffix.lower()
        name = path.name.lower()

        if "package.json" in name or ext == ".json":
            # Could be npm, but need to check content
            return None
        if "requirements" in name or ext == ".txt":
            return "pypi"
        if "cargo" in name or ext == ".toml":
            return "cargo"
        if "go.mod" in name:
            return "go"
        if "pom.xml" in name or ext == ".xml":
            return "maven"
        if "gemfile" in name:
            return "rubygems"
        if "composer" in name:
            return "composer"
        if ext == ".csproj":
            return "nuget"
        if "package.swift" in name:
            return "swift"

        return None

