"""Python pyproject.toml parser."""

from pathlib import Path
from typing import List

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult

try:
    import tomllib  # Python 3.11+
    HAS_TOMLLIB = True
    HAS_TOMLI = False
except ImportError:
    HAS_TOMLLIB = False
    try:
        import tomli  # For Python < 3.11
        HAS_TOMLI = True
    except ImportError:
        HAS_TOMLI = False


class PyProjectParser(BaseParser):
    """Parser for Python pyproject.toml files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is pyproject.toml."""
        path = Path(filepath)
        return path.name.lower() == "pyproject.toml"

    def parse(self, filepath: str) -> ParseResult:
        """Parse pyproject.toml file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        if not HAS_TOMLLIB and not HAS_TOMLI:
            errors.append("No TOML parser available. Install tomli for Python < 3.11")
            return ParseResult(
                packages=[],
                source_type=SourceType.REQUIREMENTS,
                source_file=filepath,
                errors=errors,
                warnings=warnings,
            )

        try:
            with open(filepath, "rb") as f:
                if HAS_TOMLLIB:
                    data = tomllib.load(f)
                elif HAS_TOMLI:
                    import tomli
                    data = tomli.load(f)

            # Try different dependency sections
            # 1. Standard PEP 621: [project.dependencies]
            project_deps = data.get("project", {}).get("dependencies", [])
            if project_deps:
                for dep_spec in project_deps:
                    pkg = self._parse_dependency_spec(dep_spec)
                    if pkg:
                        packages.append(pkg)

            # 2. Optional dependencies: [project.optional-dependencies]
            optional_deps = data.get("project", {}).get("optional-dependencies", {})
            for group_name, deps in optional_deps.items():
                if isinstance(deps, list):
                    for dep_spec in deps:
                        pkg = self._parse_dependency_spec(dep_spec)
                        if pkg:
                            packages.append(pkg)

            # 3. Poetry: [tool.poetry.dependencies]
            poetry_deps = (
                data.get("tool", {})
                .get("poetry", {})
                .get("dependencies", {})
            )
            if poetry_deps and isinstance(poetry_deps, dict):
                for name, spec in poetry_deps.items():
                    if name == "python":  # Skip Python version spec
                        continue
                    pkg = self._parse_poetry_dependency(name, spec)
                    if pkg:
                        packages.append(pkg)

            # 4. Poetry dev dependencies: [tool.poetry.group.dev.dependencies]
            poetry_dev_deps = (
                data.get("tool", {})
                .get("poetry", {})
                .get("group", {})
                .get("dev", {})
                .get("dependencies", {})
            )
            if poetry_dev_deps and isinstance(poetry_dev_deps, dict):
                for name, spec in poetry_dev_deps.items():
                    pkg = self._parse_poetry_dependency(name, spec)
                    if pkg:
                        packages.append(pkg)

        except Exception as e:
            errors.append(f"Failed to parse pyproject.toml: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.REQUIREMENTS,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

    def _parse_dependency_spec(self, spec: str) -> Package | None:
        """Parse a PEP 508 dependency specification."""
        if not spec or not isinstance(spec, str):
            return None

        spec = spec.strip()

        # Remove extras: package[extra] -> package
        if "[" in spec:
            spec = spec.split("[")[0]

        # Parse version specifiers
        # Common patterns: package==1.0.0, package>=1.0.0, package~=1.0.0
        import re

        # Match package name and version
        match = re.match(
            r"^([a-zA-Z0-9_-]+[a-zA-Z0-9_.-]*)\s*(==|>=|<=|>|<|~=|\^|!=)?\s*([0-9.]+.*)?$",
            spec,
        )
        if match:
            name = match.group(1)
            version = match.group(3) if match.group(3) else None
            return Package(
                name=name,
                version=self._normalize_version(version),
                ecosystem="pypi",
            )

        # If no version, just return the name
        if spec and not any(c in spec for c in ">=<~!^"):
            return Package(name=spec, version=None, ecosystem="pypi")

        return None

    def _parse_poetry_dependency(self, name: str, spec) -> Package | None:
        """Parse a Poetry dependency specification."""
        if not name or name == "python":
            return None

        version = None
        if isinstance(spec, str):
            # String version like "^1.0.0" or "1.0.0"
            version = self._extract_version(spec)
        elif isinstance(spec, dict):
            # Dictionary with version, optional, etc.
            version = spec.get("version")
            if version:
                version = self._extract_version(version)

        return Package(
            name=name,
            version=self._normalize_version(version),
            ecosystem="pypi",
        )

    def _extract_version(self, version_spec: str) -> str | None:
        """Extract version from version specifier."""
        if not version_spec:
            return None

        version_spec = version_spec.strip()
        # Remove operators: ^, ~, >=, <=, >, <, ==
        if version_spec.startswith("^") or version_spec.startswith("~"):
            return version_spec[1:]
        if version_spec.startswith(">=") or version_spec.startswith("<="):
            return version_spec[2:]
        if version_spec.startswith(">") or version_spec.startswith("<"):
            return version_spec[1:]
        if version_spec.startswith("=="):
            return version_spec[2:]
        if version_spec.startswith("="):
            return version_spec[1:]

        return version_spec

