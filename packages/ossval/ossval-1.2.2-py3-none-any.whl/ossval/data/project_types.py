"""Project type detection based on package name and keywords."""

from typing import Dict, List, Optional

from ossval.models import ProjectType


# Detection keywords and patterns for each project type
PROJECT_TYPE_PATTERNS: Dict[ProjectType, List[str]] = {
    ProjectType.SCRIPT: [
        "-utils",
        "-helper",
        "-tools",
        "-cli",
        "-script",
    ],
    ProjectType.FRAMEWORK: [
        "framework",
        "react",
        "django",
        "rails",
        "spring",
        "express",
        "flask",
        "fastapi",
        "angular",
        "vue",
        "ember",
        "svelte",
        "next",
        "nuxt",
        "gatsby",
    ],
    ProjectType.COMPILER: [
        "compiler",
        "llvm",
        "parser",
        "hermes",
        "v8",
        "babel",
        "typescript",
        "swiftc",
        "rustc",
        "gcc",
        "clang",
    ],
    ProjectType.DATABASE: [
        "database",
        "sql",
        "redis",
        "mongo",
        "postgres",
        "mysql",
        "sqlite",
        "cassandra",
        "elasticsearch",
        "influx",
        "neo4j",
        "couch",
        "dynamo",
    ],
    ProjectType.OPERATING_SYSTEM: [
        "kernel",
        "driver",
        "systemd",
        "init",
        "bootloader",
        "firmware",
    ],
    ProjectType.CRYPTOGRAPHY: [
        "crypto",
        "ssl",
        "tls",
        "encryption",
        "openssl",
        "boringssl",
        "libsodium",
        "nacl",
        "bcrypt",
        "scrypt",
        "argon",
    ],
    ProjectType.MACHINE_LEARNING: [
        "tensorflow",
        "pytorch",
        "sklearn",
        "scikit",
        "keras",
        "theano",
        "mxnet",
        "caffe",
        "torch",
        "jax",
        "transformers",
    ],
    ProjectType.NETWORKING: [
        "http",
        "grpc",
        "proxy",
        "socket",
        "network",
        "tcp",
        "udp",
        "websocket",
        "rest",
        "graphql",
        "rpc",
    ],
    ProjectType.EMBEDDED: [
        "embedded",
        "firmware",
        "rtos",
        "arduino",
        "raspberry",
        "microcontroller",
        "iot",
    ],
    ProjectType.GRAPHICS: [
        "opengl",
        "vulkan",
        "graphics",
        "game",
        "render",
        "canvas",
        "webgl",
        "directx",
        "metal",
    ],
    ProjectType.SCIENTIFIC: [
        "scipy",
        "numerical",
        "simulation",
        "numpy",
        "pandas",
        "matplotlib",
        "plotly",
        "seaborn",
    ],
    ProjectType.DEVTOOLS: [
        "lint",
        "format",
        "debugger",
        "ci",
        "test",
        "coverage",
        "build",
        "bundler",
        "webpack",
        "rollup",
        "vite",
    ],
}


def detect_project_type(
    package_name: str, repository_url: Optional[str] = None, description: Optional[str] = None
) -> tuple[ProjectType, Dict[str, any]]:
    """
    Detect project type based on package name, repository URL, and description.

    Returns:
        Tuple of (ProjectType, detection_details)
    """
    search_text = package_name.lower()
    if repository_url:
        search_text += " " + repository_url.lower()
    if description:
        search_text += " " + description.lower()

    # Check patterns in priority order (most specific first)
    # Priority: Compiler > OS > Crypto > Database > ML > Framework > etc.
    priority_order = [
        ProjectType.COMPILER,
        ProjectType.OPERATING_SYSTEM,
        ProjectType.CRYPTOGRAPHY,
        ProjectType.DATABASE,
        ProjectType.MACHINE_LEARNING,
        ProjectType.FRAMEWORK,
        ProjectType.NETWORKING,
        ProjectType.EMBEDDED,
        ProjectType.GRAPHICS,
        ProjectType.SCIENTIFIC,
        ProjectType.DEVTOOLS,
        ProjectType.SCRIPT,
    ]

    matched_keywords = []
    for project_type in priority_order:
        patterns = PROJECT_TYPE_PATTERNS.get(project_type, [])
        for pattern in patterns:
            if pattern in search_text:
                matched_keywords.append(pattern)
                detection_details = {
                    "project_type": project_type.value,
                    "matched_keywords": matched_keywords,
                    "confidence": "high" if len(matched_keywords) > 0 else "low",
                    "method": "keyword_matching",
                }
                return project_type, detection_details

    # Default to library if no patterns match
    detection_details = {
        "project_type": ProjectType.LIBRARY.value,
        "matched_keywords": [],
        "confidence": "default",
        "method": "default",
    }
    return ProjectType.LIBRARY, detection_details

