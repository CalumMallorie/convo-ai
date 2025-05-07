"""Tests for the benchmarking module."""

import json
import time
from pathlib import Path
import pytest
from src.benchmarks import PerformanceMetrics, benchmark, get_system_metrics

@pytest.fixture
def temp_metrics_file(tmp_path):
    """Create a temporary metrics file."""
    return str(tmp_path / "test_metrics.json")

def test_performance_metrics_initialization(temp_metrics_file):
    """Test PerformanceMetrics initialization."""
    metrics = PerformanceMetrics(temp_metrics_file)
    assert isinstance(metrics.metrics, dict)
    assert Path(metrics.metrics_file).exists()

def test_record_metric(temp_metrics_file):
    """Test recording a metric."""
    metrics = PerformanceMetrics(temp_metrics_file)
    metrics.record_metric("test_category", 1.23, {"test_meta": "value"})
    
    # Verify metric was saved
    with open(temp_metrics_file, 'r') as f:
        saved_metrics = json.load(f)
    
    assert "test_category" in saved_metrics
    assert len(saved_metrics["test_category"]) == 1
    assert saved_metrics["test_category"][0]["value"] == 1.23
    assert saved_metrics["test_category"][0]["test_meta"] == "value"

def test_benchmark_decorator(temp_metrics_file):
    """Test the benchmark decorator."""
    
    @benchmark("test_func")
    def test_function(sleep_time: float = 0.1) -> None:
        time.sleep(sleep_time)
    
    test_function()
    
    metrics = PerformanceMetrics(temp_metrics_file)
    assert "test_func_time" in metrics.metrics
    assert "test_func_memory" in metrics.metrics
    
    # Verify timing is reasonable
    time_metric = metrics.metrics["test_func_time"][0]
    assert 0.1 <= time_metric["value"] <= 0.2  # Allow some overhead
    assert time_metric["function"] == "test_function"

def test_get_system_metrics():
    """Test getting system metrics."""
    metrics = get_system_metrics()
    
    assert isinstance(metrics, dict)
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "memory_mb" in metrics
    assert "num_threads" in metrics
    
    # Basic sanity checks
    assert 0 <= metrics["cpu_percent"] <= 100
    assert metrics["memory_mb"] > 0
    assert metrics["num_threads"] > 0

def test_metrics_file_corruption_handling(temp_metrics_file):
    """Test handling of corrupted metrics file."""
    # Create corrupted JSON file
    with open(temp_metrics_file, 'w') as f:
        f.write("invalid json content")
    
    metrics = PerformanceMetrics(temp_metrics_file)
    assert metrics.metrics == {} 