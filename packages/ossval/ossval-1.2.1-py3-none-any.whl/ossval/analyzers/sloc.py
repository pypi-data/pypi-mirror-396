"""Source lines of code (SLOC) counting."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional

from pygount import SourceAnalysis, SourceScanner

from ossval.models import SLOCMetrics

# Patterns to ignore (production code only, exclude tests and generated files)
IGNORE_PATTERNS = [
    "__pycache__",
    "node_modules",
    "target",
    "dist",
    "build",
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.dll",
    "*.dylib",
    "tests",
    "__tests__",
    "test",
    "spec",
    "testsuite",
    "*.test.*",
    ".git",
    ".svn",
    ".hg",
    "vendor",
    ".venv",
    "venv",
    "env",
    ".env",
]


async def analyze_sloc(
    repository_url: str, cache_dir: Optional[str] = None, use_cache: bool = True
) -> Optional[SLOCMetrics]:
    """
    Analyze SLOC for a repository by cloning it.

    Args:
        repository_url: Git repository URL
        cache_dir: Optional cache directory
        use_cache: Whether to use cache

    Returns:
        SLOCMetrics if successful, None otherwise
    """
    if not repository_url:
        return None

    # Check cache first
    if use_cache and cache_dir:
        cache_path = Path(cache_dir) / "sloc" / _get_cache_key(repository_url)
        if cache_path.exists():
            try:
                return _load_sloc_from_cache(cache_path)
            except Exception:
                pass

    # Clone repository
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="ossval_")
        repo_path = Path(temp_dir) / "repo"

        # Shallow clone
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repository_url, str(repo_path)],
            capture_output=True,
            timeout=60,
        )

        if result.returncode != 0:
            # Log error for debugging
            error_msg = result.stderr.decode("utf-8", errors="ignore") if result.stderr else "Unknown error"
            # Check if it's a timeout or network issue
            if "timeout" in error_msg.lower() or "fatal" in error_msg.lower():
                # Return None - will be handled as warning
                return None
            return None

        # Count SLOC using pygount
        sloc_data = _count_sloc_with_pygount(repo_path)

        # Save to cache
        if use_cache and cache_dir and sloc_data:
            cache_path = Path(cache_dir) / "sloc" / _get_cache_key(repository_url)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            _save_sloc_to_cache(cache_path, sloc_data)

        return sloc_data

    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None
    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def _count_sloc_with_pygount(repo_path: Path) -> Optional[SLOCMetrics]:
    """Count SLOC using pygount library."""
    total_code = 0
    total_comment = 0
    total_blank = 0
    by_language: Dict[str, int] = {}

    try:
        from pygount.analysis import SourceAnalysis
        import sys
        from io import StringIO
        
        # Suppress encoding warnings from pygount for the entire analysis
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        try:
            # Walk the directory manually to avoid permission issues
            skip_dirs = {
                "__pycache__", "node_modules", "target", "dist", "build",
                ".git", ".svn", ".hg", "vendor", ".venv", "venv", "env",
                "tests", "__tests__", "test", "spec", "testsuite"
            }
            skip_extensions = {".pyc", ".pyo", ".so", ".dll", ".dylib"}
            
            # Walk through the repository
            for file_path in repo_path.rglob("*"):
                # Skip directories
                if file_path.is_dir():
                    continue
                
                # Skip if in a directory we want to ignore
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                
                # Skip binary files
                if file_path.suffix in skip_extensions:
                    continue
                
                # Skip test files
                if "test" in file_path.name.lower() or "test" in str(file_path):
                    continue
                
                try:
                    # Analyze the file - SourceAnalysis.from_file requires group parameter
                    analysis = SourceAnalysis.from_file(str(file_path), group='')
                    
                    if analysis:
                        lang = analysis.language or "unknown"
                        total_code += analysis.code_count
                        total_comment += analysis.documentation_count
                        total_blank += analysis.empty_count
                        by_language[lang] = (
                            by_language.get(lang, 0) + analysis.code_count
                        )
                except Exception:
                    # Skip files that can't be analyzed (encoding errors, etc.)
                    continue
        finally:
            # Restore stderr
            sys.stderr = old_stderr

        if total_code == 0 and total_comment == 0 and total_blank == 0:
            return None

        return SLOCMetrics(
            total=total_code + total_comment + total_blank,
            code_lines=total_code,
            comment_lines=total_comment,
            blank_lines=total_blank,
            by_language=by_language,
        )

    except Exception:
        # Return None on any error
        return None


def _should_ignore(path: Path | str) -> bool:
    """Check if path should be ignored."""
    path_str = str(path)
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def _should_ignore_file(file_path: Path, repo_root: Path) -> bool:
    """Check if file should be ignored."""
    # Get relative path
    try:
        rel_path = file_path.relative_to(repo_root)
    except ValueError:
        return True

    path_str = str(rel_path).replace("\\", "/")

    # Check patterns
    for pattern in IGNORE_PATTERNS:
        if pattern in path_str:
            return True
        # Check if it's a test file
        if "/test" in path_str or "/tests" in path_str or path_str.startswith("test"):
            return True

    return False


def _get_cache_key(repository_url: str) -> str:
    """Generate cache key from repository URL."""
    import hashlib

    return hashlib.md5(repository_url.encode()).hexdigest()


def _save_sloc_to_cache(cache_path: Path, sloc_data: SLOCMetrics) -> None:
    """Save SLOC data to cache."""
    import json

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(sloc_data.model_dump(), f)


def _load_sloc_from_cache(cache_path: Path) -> Optional[SLOCMetrics]:
    """Load SLOC data from cache."""
    import json

    if not cache_path.exists():
        return None

    with open(cache_path, "r") as f:
        data = json.load(f)
        return SLOCMetrics(**data)

