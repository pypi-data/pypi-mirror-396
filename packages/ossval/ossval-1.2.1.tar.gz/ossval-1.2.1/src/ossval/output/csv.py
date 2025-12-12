"""CSV formatter for analysis results."""

from pathlib import Path
from typing import Dict, Optional

from ossval.models import AnalysisResult


def format_csv(result: AnalysisResult, output_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Format analysis results as CSV files.

    Args:
        result: AnalysisResult to format
        output_dir: Optional output directory (default: current directory)

    Returns:
        Dictionary with paths to generated CSV files
    """
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    # Use the built-in to_csv method
    return result.to_csv(str(output_path))

