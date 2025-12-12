"""Maven pom.xml parser."""

from pathlib import Path
from typing import List
from xml.etree import ElementTree as ET

from ossval.models import Package, SourceType
from ossval.parsers.base import BaseParser, ParseResult


class MavenParser(BaseParser):
    """Parser for Maven pom.xml files."""

    def can_parse(self, filepath: str) -> bool:
        """Check if file is pom.xml."""
        path = Path(filepath)
        return path.name.lower() == "pom.xml"

    def parse(self, filepath: str) -> ParseResult:
        """Parse pom.xml file."""
        packages: List[Package] = []
        errors = []
        warnings = []

        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            # Handle Maven namespaces
            # Extract namespace from root tag
            ns_uri = None
            if root.tag.startswith("{"):
                # Extract namespace URI
                ns_uri = root.tag.split("}")[0][1:]
            
            # Parse dependencies - use full namespace URI in tag name
            if ns_uri:
                deps = root.findall(f".//{{{ns_uri}}}dependency")
            else:
                deps = root.findall(".//dependency")

            for dep in deps:
                # Use namespace URI if available
                if ns_uri:
                    group_id_elem = dep.find(f"{{{ns_uri}}}groupId")
                    artifact_id_elem = dep.find(f"{{{ns_uri}}}artifactId")
                    version_elem = dep.find(f"{{{ns_uri}}}version")
                else:
                    group_id_elem = dep.find("groupId")
                    artifact_id_elem = dep.find("artifactId")
                    version_elem = dep.find("version")

                if group_id_elem is not None and artifact_id_elem is not None:
                    group_id = group_id_elem.text or ""
                    artifact_id = artifact_id_elem.text or ""
                    version = version_elem.text if version_elem is not None else None

                    if group_id and artifact_id:
                        name = f"{group_id}:{artifact_id}"
                        packages.append(
                            Package(
                                name=name,
                                version=self._normalize_version(version),
                                ecosystem="maven",
                            )
                        )

        except ET.ParseError as e:
            errors.append(f"Invalid XML in pom.xml: {str(e)}")
        except Exception as e:
            errors.append(f"Failed to parse pom.xml: {str(e)}")

        return ParseResult(
            packages=packages,
            source_type=SourceType.MAVEN,
            source_file=filepath,
            errors=errors,
            warnings=warnings,
        )

