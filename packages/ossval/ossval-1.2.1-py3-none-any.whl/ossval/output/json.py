"""JSON formatter for analysis results."""

import json
from typing import Optional

from ossval.models import AnalysisResult


def format_json(result: AnalysisResult, output_file: Optional[str] = None) -> str:
    """
    Format analysis results as JSON.

    Args:
        result: AnalysisResult to format
        output_file: Optional file path to write to

    Returns:
        JSON string
    """
    # Convert to dict with proper serialization
    data = result.model_dump(mode="json")
    json_str = json.dumps(data, indent=2, default=str)

    if output_file:
        with open(output_file, "w") as f:
            f.write(json_str)

    return json_str

