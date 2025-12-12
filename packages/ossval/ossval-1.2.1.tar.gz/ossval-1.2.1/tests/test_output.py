"""Tests for output formatters."""

import json
import tempfile
from pathlib import Path

from ossval.models import AnalysisResult, CostEstimate, Package, ProjectType, Region, SLOCMetrics
from ossval.output import format_csv, format_json, format_text


def test_format_json(tmp_path):
    """Test JSON formatter."""
    result = AnalysisResult(
        summary={"total_packages": 5},
        packages=[],
    )
    
    output_file = tmp_path / "output.json"
    format_json(result, str(output_file))
    
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert data["summary"]["total_packages"] == 5


def test_format_csv(tmp_path):
    """Test CSV formatter."""
    from ossval.models import CostEstimate, Package, Region, SLOCMetrics
    
    package = Package(
        name="test",
        version="1.0.0",
        cost_estimate=CostEstimate(
            effort_person_months=10.0,
            effort_person_years=0.83,
            cost_usd=50000.0,
            cost_usd_low=35000.0,
            cost_usd_high=75000.0,
            methodology="COCOMO II",
            confidence=0.8,
            region=Region.US_SF,
            project_type=ProjectType.LIBRARY,
            complexity_multiplier=1.0,
            project_type_multiplier=1.0,
        ),
        sloc=SLOCMetrics(
            total=5000,
            code_lines=4000,
            comment_lines=800,
            blank_lines=200,
            by_language={},
        ),
    )
    
    result = AnalysisResult(
        summary={"total_packages": 1},
        packages=[package],
    )
    
    csv_files = format_csv(result, str(tmp_path))
    
    assert "summary.csv" in csv_files["summary"]
    assert "packages.csv" in csv_files["packages"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "packages.csv").exists()


def test_format_text():
    """Test text formatter (basic check)."""
    result = AnalysisResult(
        summary={
            "total_cost_usd": 1000000,
            "total_packages": 10,
            "analyzed_packages": 10,
        },
        packages=[],
    )
    
    # Should not raise
    format_text(result)

