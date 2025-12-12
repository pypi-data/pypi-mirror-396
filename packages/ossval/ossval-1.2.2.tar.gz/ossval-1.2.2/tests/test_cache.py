"""Tests for caching system."""

from ossval.cache import AnalysisCache


def test_cache_creation():
    """Test cache creation."""
    cache = AnalysisCache()
    assert cache.cache_dir.exists()


def test_cache_get_set():
    """Test cache get/set operations."""
    cache = AnalysisCache()
    
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    
    assert value == "test_value"


def test_cache_info():
    """Test cache info."""
    cache = AnalysisCache()
    info = cache.info()
    
    assert "cache_dir" in info
    assert "size" in info
    assert "count" in info


def test_cache_clear():
    """Test cache clearing."""
    cache = AnalysisCache()
    
    cache.set("test_key", "test_value")
    cache.clear()
    
    value = cache.get("test_key")
    assert value is None

