"""Tests for data models."""

from ossval.models import (
    AnalysisResult,
    CostEstimate,
    Package,
    ProjectType,
    Region,
    SLOCMetrics,
)


def test_package_model():
    """Test Package model creation."""
    package = Package(
        name="test-package",
        version="1.0.0",
        ecosystem="pypi",
    )
    
    assert package.name == "test-package"
    assert package.version == "1.0.0"
    assert package.ecosystem == "pypi"
    assert package.is_critical is False


def test_sloc_metrics():
    """Test SLOCMetrics model."""
    sloc = SLOCMetrics(
        total=10000,
        code_lines=8000,
        comment_lines=1500,
        blank_lines=500,
        by_language={"python": 8000},
    )
    
    assert sloc.total == 10000
    assert sloc.code_lines == 8000
    assert "python" in sloc.by_language


def test_cost_estimate():
    """Test CostEstimate model."""
    estimate = CostEstimate(
        effort_person_months=12.0,
        effort_person_years=1.0,
        cost_usd=100000.0,
        cost_usd_low=70000.0,
        cost_usd_high=150000.0,
        methodology="COCOMO II",
        confidence=0.8,
        region=Region.US_SF,
        project_type=ProjectType.LIBRARY,
        complexity_multiplier=1.0,
        project_type_multiplier=1.0,
    )
    
    assert estimate.effort_person_months == 12.0
    assert estimate.cost_usd == 100000.0
    assert estimate.confidence == 0.8


def test_analysis_result_to_json():
    """Test AnalysisResult JSON export."""
    result = AnalysisResult(
        summary={"total_packages": 10},
        packages=[],
    )
    
    json_str = result.to_json()
    assert "total_packages" in json_str
    assert "10" in json_str


def test_analysis_result_to_csv(tmp_path):
    """Test AnalysisResult CSV export."""
    from ossval.models import CostEstimate, SLOCMetrics
    
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
    
    csv_files = result.to_csv(str(tmp_path))
    
    assert "summary.csv" in csv_files["summary"]
    assert "packages.csv" in csv_files["packages"]
    
    # Check files exist
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "packages.csv").exists()

