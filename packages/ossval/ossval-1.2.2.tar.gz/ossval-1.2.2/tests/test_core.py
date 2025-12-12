"""Tests for core analysis functionality."""

import asyncio
import tempfile
from pathlib import Path

import pytest

from ossval.core import analyze, quick_estimate
from ossval.models import AnalysisConfig, Region, ProjectType


def test_quick_estimate():
    """Test quick estimate function."""
    result = quick_estimate(sloc=50000, region=Region.US_SF, project_type=ProjectType.COMPILER)
    
    assert "cost_usd" in result
    assert result["cost_usd"] > 0
    assert result["effort_person_months"] > 0
    assert result["methodology"] == "COCOMO II"


@pytest.mark.asyncio
async def test_analyze_requirements_txt(sample_requirements_txt):
    """Test analyzing a requirements.txt file."""
    config = AnalysisConfig(
        region=Region.GLOBAL_AVERAGE,
        clone_repos=False,  # Don't clone for testing
        use_cache=False,
    )
    
    result = await analyze(sample_requirements_txt, config)
    
    assert result.summary["total_packages"] == 3
    assert len(result.packages) == 3
    assert result.meta["source_type"] == "requirements"


@pytest.mark.asyncio
async def test_analyze_package_list():
    """Test analyzing a list of packages directly."""
    from ossval.models import Package
    
    packages = [
        Package(name="requests", version="2.31.0", ecosystem="pypi"),
        Package(name="numpy", version="1.24.0", ecosystem="pypi"),
    ]
    
    config = AnalysisConfig(
        region=Region.GLOBAL_AVERAGE,
        clone_repos=False,
        use_cache=False,
    )
    
    result = await analyze(packages, config)
    
    assert len(result.packages) == 2
    assert result.packages[0].name == "requests"

