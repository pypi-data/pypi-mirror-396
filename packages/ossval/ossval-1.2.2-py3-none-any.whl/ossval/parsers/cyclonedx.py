"""CycloneDX SBOM parser."""

import json
from pathlib import Path
from typing import Any, Dict, List
from xml.etree import ElementTree as ET

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class CycloneDXParser(BaseParser):
    """Parser for CycloneDX SBOM format (JSON and XML)."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is CycloneDX format."""
        path = Path(filepath)
        if path.suffix.lower() in [".json", ".xml"]:
            try:
                if path.suffix.lower() == ".json":
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        return data.get("bomFormat") == "CycloneDX" or "components" in data
                else:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    # Check for CycloneDX namespace
                    return (
                        root.tag.endswith("bom")
                        or "{http://cyclonedx.org/schema/bom/1.4}" in root.tag
                        or "{http://cyclonedx.org/schema/bom/1.3}" in root.tag
                    )
            except Exception:
                return False
        return False

    def parse(self, filepath: str) -> ParseResult:
        """Parse CycloneDX SBOM file."""
        path = Path(filepath)
        errors = []
        warnings = []
        packages: List[Package] = []

        try:
            if path.suffix.lower() == ".json":
                packages = self._parse_json(filepath)
            else:
                packages = self._parse_xml(filepath)
        except Exception as e:
            errors.append(f"Failed to parse CycloneDX file: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.CYCLONEDX,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

    def _parse_json(self, filepath: str) -> List[Package]:
        """Parse CycloneDX JSON format."""
        with open(filepath, "r") as f:
            data = json.load(f)

        packages = []
        components = data.get("components", [])

        for component in components:
            name = component.get("name", "")
            version = component.get("version")
            pkg_type = component.get("type", "library")

            # Skip non-library components (application, container, etc.)
            if pkg_type != "library":
                continue

            # Extract ecosystem from purl (Package URL)
            purl = component.get("purl", "")
            ecosystem = self._extract_ecosystem_from_purl(purl)

            # Extract repository URL
            external_refs = component.get("externalReferences", [])
            repository_url = None
            for ref in external_refs:
                if ref.get("type") == "vcs" or ref.get("type") == "repository":
                    repository_url = ref.get("url")
                    break

            # Extract language
            properties = component.get("properties", [])
            language = None
            for prop in properties:
                if prop.get("name") == "cdx:language":
                    language = prop.get("value")
                    break

            package = Package(
                name=name,
                version=self._normalize_version(version),
                ecosystem=ecosystem,
                language=language,
                repository_url=repository_url,
            )
            packages.append(package)

        return packages

    def _parse_xml(self, filepath: str) -> List[Package]:
        """Parse CycloneDX XML format."""
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Handle namespaces
        ns = {"bom": "http://cyclonedx.org/schema/bom/1.4"}
        if not root.tag.startswith("{"):
            ns = {}

        packages = []
        components = root.findall(".//bom:component", ns) or root.findall(".//component")

        for component in components:
            name_elem = component.find("bom:name", ns) or component.find("name")
            version_elem = component.find("bom:version", ns) or component.find("version")
            type_elem = component.find("bom:type", ns) or component.find("type")

            if name_elem is None:
                continue

            name = name_elem.text or ""
            version = version_elem.text if version_elem is not None else None
            pkg_type = type_elem.text if type_elem is not None else "library"

            # Skip non-library components
            if pkg_type != "library":
                continue

            # Extract purl
            purl_elem = component.find("bom:purl", ns) or component.find("purl")
            purl = purl_elem.text if purl_elem is not None else ""
            ecosystem = self._extract_ecosystem_from_purl(purl)

            # Extract repository URL from external references
            ext_refs = component.findall(".//bom:externalReference", ns) or component.findall(
                ".//externalReference"
            )
            repository_url = None
            for ref in ext_refs:
                ref_type = ref.find("bom:type", ns) or ref.find("type")
                ref_url = ref.find("bom:url", ns) or ref.find("url")
                if ref_type is not None and ref_type.text in ["vcs", "repository"]:
                    if ref_url is not None:
                        repository_url = ref_url.text
                        break

            package = Package(
                name=name,
                version=self._normalize_version(version),
                ecosystem=ecosystem,
                repository_url=repository_url,
            )
            packages.append(package)

        return packages

    def _extract_ecosystem_from_purl(self, purl: str) -> str | None:
        """Extract ecosystem from Package URL (pkg:type/namespace/name@version)."""
        if not purl or not purl.startswith("pkg:"):
            return None

        try:
            # pkg:npm/package@version or pkg:pypi/package@version
            parts = purl[4:].split("/")
            if parts:
                ecosystem = parts[0].split("@")[0]  # Remove version if present
                # Normalize ecosystem names
                ecosystem_map = {
                    "npm": "npm",
                    "pypi": "pypi",
                    "maven": "maven",
                    "cargo": "cargo",
                    "golang": "go",
                    "gem": "rubygems",
                    "composer": "composer",
                    "nuget": "nuget",
                    "swiftpm": "swift",
                }
                return ecosystem_map.get(ecosystem, ecosystem)
        except Exception:
            pass

        return None

