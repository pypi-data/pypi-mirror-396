"""Rust Cargo.toml parser."""

from pathlib import Path
from typing import Dict, List

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


class CargoParser(BaseParser):
    """Parser for Rust Cargo.toml and Cargo.lock files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is Cargo.toml or Cargo.lock."""
        path = Path(filepath)
        name = path.name.lower()
        return name in ["cargo.toml", "cargo.lock"]

    def parse(self, filepath: str) -> ParseResult:
        """Parse Cargo.toml or Cargo.lock file."""
        path = Path(filepath)
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            if path.name.lower() == "cargo.lock":
                packages = self._parse_lock(filepath)
            else:
                packages = self._parse_toml(filepath)
        except Exception as e:
            errors.append(f"Failed to parse Cargo file: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.CARGO,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

    def _parse_toml(self, filepath: str) -> List[Package]:
        """Parse Cargo.toml file."""
        packages = []

        with open(filepath, "rb") as f:
            if HAS_TOMLLIB:
                data = tomllib.load(f)
            elif HAS_TOMLI:
                import tomli
                data = tomli.load(f)
            else:
                raise ImportError("No TOML parser available. Install tomli for Python < 3.11")

        # Parse dependencies
        deps = data.get("dependencies", {})
        dev_deps = data.get("dev-dependencies", {})

        all_deps = {**deps, **dev_deps}

        for name, spec in all_deps.items():
            if isinstance(spec, str):
                # Version string like "1.2.3" or "^1.2.3"
                version = self._extract_version(spec)
                packages.append(
                    Package(
                        name=name,
                        version=self._normalize_version(version),
                        ecosystem="cargo",
                    )
                )
            elif isinstance(spec, dict):
                # Dependency object with version, path, git, etc.
                version = spec.get("version")
                if version:
                    version = self._extract_version(version)
                    packages.append(
                        Package(
                            name=name,
                            version=self._normalize_version(version),
                            ecosystem="cargo",
                        )
                    )

        return packages

    def _parse_lock(self, filepath: str) -> List[Package]:
        """Parse Cargo.lock file."""
        packages = []

        with open(filepath, "rb") as f:
            if HAS_TOMLLIB:
                data = tomllib.load(f)
            elif HAS_TOMLI:
                import tomli
                data = tomli.load(f)
            else:
                raise ImportError("No TOML parser available. Install tomli for Python < 3.11")

        # Cargo.lock has a [[package]] array
        package_list = data.get("package", [])

        for pkg in package_list:
            name = pkg.get("name", "")
            version = pkg.get("version")
            if name:
                packages.append(
                    Package(
                        name=name,
                        version=self._normalize_version(version),
                        ecosystem="cargo",
                    )
                )

        return packages

    def _extract_version(self, version_spec: str) -> str | None:
        """Extract version from Cargo version spec."""
        if not version_spec:
            return None

        version_spec = version_spec.strip()
        # Remove operators
        if version_spec.startswith("^") or version_spec.startswith("~"):
            return version_spec[1:]
        if version_spec.startswith(">=") or version_spec.startswith("<="):
            return version_spec[2:]
        if version_spec.startswith(">") or version_spec.startswith("<"):
            return version_spec[1:]
        if version_spec.startswith("="):
            return version_spec[1:]

        return version_spec

