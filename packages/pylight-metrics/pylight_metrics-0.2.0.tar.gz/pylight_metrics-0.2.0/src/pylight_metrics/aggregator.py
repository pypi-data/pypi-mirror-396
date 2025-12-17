import threading
import time
import atexit
import statistics
from typing import Dict, List, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

# CONSTANTS
SHARD_COUNT = 64 

class MetricType(Enum):
    COUNTER = "counter"
    TIMER = "timer"

@dataclass
class AggregatedStats:
    name: str
    count: int = 0
    total: float = 0.0
    min: float = float('inf')
    max: float = float('-inf')
    avg: float = 0.0
    p50: Optional[float] = None
    p90: Optional[float] = None
    p99: Optional[float] = None

class LockFreeMetricsAggregator:
    _instance: Optional['LockFreeMetricsAggregator'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # 64 Shards. Each shard holds a dict of LISTS now (for timers)
        # Structure: shards[i] = { "metric_name": [val1, val2, val3] }
        self._shards = [defaultdict(list) for _ in range(SHARD_COUNT)]
        self._shard_locks = [threading.Lock() for _ in range(SHARD_COUNT)]
        self._running = True
        atexit.register(self.shutdown)

    def add_metric(self, name: str, value: float, metric_type: MetricType = MetricType.COUNTER):
        """
        Fast Write Path:
        1. Map to Shard
        2. Append to list (O(1) operation)
        """
        shard_idx = threading.get_ident() % SHARD_COUNT
        with self._shard_locks[shard_idx]:
            self._shards[shard_idx][name].append(value)

    def flush(self) -> Dict[str, AggregatedStats]:
        """
        Heavy Read Path (Isolated):
        Merges lists and calculates math stats.
        """
        # 1. Collect all raw data from shards
        merged_data: Dict[str, List[float]] = defaultdict(list)
        
        for i in range(SHARD_COUNT):
            with self._shard_locks[i]:
                if not self._shards[i]: continue
                # Move data out of shard (Reset)
                for name, values in self._shards[i].items():
                    merged_data[name].extend(values)
                self._shards[i].clear()
        
        # 2. Calculate Stats (Expensive part happens here, not in add_metric)
        results = {}
        for name, values in merged_data.items():
            if not values: continue
            
            # Basic Stats
            count = len(values)
            total = sum(values)
            stats = AggregatedStats(name=name, count=count, total=total)
            stats.min = min(values)
            stats.max = max(values)
            stats.avg = total / count
            
            # Percentiles (The heavy sorting)
            values.sort()
            stats.p50 = values[int(count * 0.50)]
            stats.p90 = values[int(count * 0.90)]
            stats.p99 = values[int(count * 0.99)]
            
            results[name] = stats
            
        return results

    def shutdown(self):
        self._running = False
        self.flush()
        
    # Stubs for compatibility
    def export_prometheus(self): return ""
    def export_csv(self): return ""
