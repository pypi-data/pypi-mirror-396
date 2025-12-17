import time
import functools
from typing import Optional, Dict, Callable
from contextlib import ContextDecorator
from .aggregator import LockFreeMetricsAggregator, MetricType

class ZeroContentionTimer(ContextDecorator):
    """
    Timer that sends metrics to the lock-free aggregator.
    Each timing operation uses thread-local storage to avoid contention.
    """
    
    def __init__(
        self,
        name: str,
        aggregator: Optional[LockFreeMetricsAggregator] = None,
        tags: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> None:
        self.name = name
        self.aggregator = aggregator or LockFreeMetricsAggregator()
        self.tags = tags or {}
        self.enabled = enabled
        self._start_time: Optional[float] = None
    
    def __enter__(self) -> 'ZeroContentionTimer':
        if self.enabled:
            self._start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.enabled and self._start_time is not None:
            elapsed = time.perf_counter() - self._start_time
            final_tags = {**self.tags, 'error': 'true' if exc_type else 'false'}
            
            self.aggregator.add_metric(
                name=self.name,
                value=elapsed,
                metric_type=MetricType.TIMER,
                tags=final_tags
            )
        return False

def fast_timer(name: str, **kwargs) -> ZeroContentionTimer:
    """Factory function for creating zero-contention timers."""
    return ZeroContentionTimer(name, **kwargs)

import time
import functools
from typing import Optional, Dict, Callable
from contextlib import ContextDecorator
# ENSURE THIS IMPORT HAS MetricType
from .aggregator import LockFreeMetricsAggregator, MetricType 

# ... (Keep existing ZeroContentionTimer code here) ...

# === ADD THIS NEW CODE BELOW ===

def increment(name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
    """
    Directly increments a counter metric.
    Usage: increment("login.failed", 1)
    """
    agg = LockFreeMetricsAggregator()
    agg.add_metric(name, value, MetricType.COUNTER, tags)

class ZeroContentionCounter(ContextDecorator):
    """
    Decorator/Context Manager that counts executions.
    """
    def __init__(
        self,
        name: str,
        value: float = 1.0,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        self.name = name
        self.value = value
        self.tags = tags or {}
        self.aggregator = LockFreeMetricsAggregator()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Add error tag if the function crashed
        final_tags = self.tags.copy()
        if exc_type:
            final_tags['error'] = 'true'
            
        self.aggregator.add_metric(
            self.name, 
            self.value, 
            MetricType.COUNTER, 
            final_tags
        )
        return False

def count_calls(name: str, value: float = 1.0, **kwargs) -> ZeroContentionCounter:
    """
    Decorator to count how many times a function is called.
    Usage: @count_calls("my_function_runs")
    """
    return ZeroContentionCounter(name, value, **kwargs)
