"""Performance benchmarking utilities for Convo-AI."""

from typing import Any, Callable, Dict, Optional, TypeVar
import time
import psutil
import functools
import json
from pathlib import Path
import logging
from datetime import datetime

# Type variable for generic function decoration
F = TypeVar('F', bound=Callable[..., Any])

class PerformanceMetrics:
    """Tracks and stores performance metrics for the application."""
    
    def __init__(self, metrics_file: str = "output/performance_metrics.json"):
        """Initialize the performance metrics tracker.
        
        Args:
            metrics_file: Path to store the metrics data
        """
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, list] = self._load_metrics()
        self._save_metrics()  # Ensure file exists after initialization

    def _load_metrics(self) -> Dict[str, list]:
        """Load existing metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                self.logger.warning("Could not load metrics file, starting fresh")
        return {}

    def _save_metrics(self) -> None:
        """Save metrics to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    def record_metric(self, category: str, value: float, metadata: Optional[Dict] = None) -> None:
        """Record a new metric value.
        
        Args:
            category: The type of metric (e.g., 'response_time', 'memory_usage')
            value: The metric value
            metadata: Additional contextual information
        """
        if category not in self.metrics:
            self.metrics[category] = []
            
        metric_data = {
            'timestamp': datetime.now().isoformat(),
            'value': value,
            **(metadata or {})
        }
        
        self.metrics[category].append(metric_data)
        self._save_metrics()

def benchmark(category: str) -> Callable[[F], F]:
    """Decorator to benchmark function execution.
    
    Args:
        category: The type of metric to record
        
    Returns:
        Decorated function that includes performance tracking
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            metrics = PerformanceMetrics()
            
            # Record memory before
            mem_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Time the function
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            
            # Record memory after
            mem_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            mem_diff = mem_after - mem_before
            
            # Record metrics
            metrics.record_metric(
                f"{category}_time",
                execution_time,
                {'function': func.__name__}
            )
            
            metrics.record_metric(
                f"{category}_memory",
                mem_diff,
                {'function': func.__name__}
            )
            
            return result
        return wrapper  # type: ignore
        
    return decorator

def get_system_metrics() -> Dict[str, float]:
    """Get current system performance metrics.
    
    Returns:
        Dictionary containing CPU usage, memory usage, etc.
    """
    process = psutil.Process()
    
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': process.memory_percent(),
        'memory_mb': process.memory_info().rss / 1024 / 1024,
        'num_threads': process.num_threads()
    } 