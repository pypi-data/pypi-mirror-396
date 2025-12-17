import time
import threading
import statistics
import json
import weakref
import atexit
import logging
from typing import Dict, List, Optional, Any, Callable, DefaultDict
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    TIMER = "timer"
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"

@dataclass
class MetricData:
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.TIMER
    thread_id: int = field(default_factory=lambda: threading.get_ident())
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['metric_type'] = self.metric_type.value
        return data

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
    p95: Optional[float] = None
    p99: Optional[float] = None
    std_dev: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.min = min(self.min, value)
        self.max = max(self.max, value)
        self.avg = self.total / self.count
        self.last_updated = datetime.now()
    
    def finalize(self, all_values: Optional[List[float]] = None) -> None:
        if self.count == 0:
            return
        self.avg = self.total / self.count
        if all_values and len(all_values) > 1:
            sorted_values = sorted(all_values)
            self.p50 = self._percentile(sorted_values, 50)
            self.p90 = self._percentile(sorted_values, 90)
            self.p95 = self._percentile(sorted_values, 95)
            self.p99 = self._percentile(sorted_values, 99)
            if len(all_values) >= 2:
                try:
                    self.std_dev = statistics.stdev(all_values)
                except statistics.StatisticsError:
                    self.std_dev = 0.0
    
    @staticmethod
    def _percentile(sorted_values: List[float], percentile: float) -> float:
        if not sorted_values: return 0.0
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = lower + 1
        if upper >= len(sorted_values): return sorted_values[lower]
        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name, 'count': self.count, 'total': self.total,
            'min': self.min if self.min != float('inf') else 0.0,
            'max': self.max if self.max != float('-inf') else 0.0,
            'avg': self.avg, 'p50': self.p50, 'p90': self.p90,
            'p95': self.p95, 'p99': self.p99, 'std_dev': self.std_dev,
            'last_updated': self.last_updated.isoformat(),
        }

class ThreadLocalBuffer:
    def __init__(self, aggregator: 'LockFreeMetricsAggregator', max_size: int = 10):
        self.aggregator = aggregator
        self.max_size = max_size
        self.buffer: List[MetricData] = []
        self.last_flush_time = datetime.now()
        self.aggregator._register_thread_buffer(self)
    
    def add(self, metric: MetricData) -> None:
        self.buffer.append(metric)
        if len(self.buffer) >= self.max_size:
            self.flush()
        elif (datetime.now() - self.last_flush_time) >= self.aggregator.flush_interval:
            self.flush()
    
    def flush(self) -> None:
        if not self.buffer: return
        buffer_copy = list(self.buffer)
        self.buffer.clear()
        self.last_flush_time = datetime.now()
        self.aggregator._merge_thread_buffer(buffer_copy)
    
    def __del__(self):
        try:
            if self.buffer: self.flush()
        except: pass

class LockFreeMetricsAggregator:
    _instance: Optional['LockFreeMetricsAggregator'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'LockFreeMetricsAggregator':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self._thread_local = threading.local()
        self._global_lock = threading.RLock()
        self._global_buffer: DefaultDict[str, List[MetricData]] = defaultdict(list)
        self._aggregated_stats: Dict[str, AggregatedStats] = {}
        self._thread_buffers: weakref.WeakSet[ThreadLocalBuffer] = weakref.WeakSet()
        self.thread_buffer_size = 10
        self.global_buffer_size = 1000
        self.flush_interval = timedelta(seconds=60)
        self.last_global_flush_time = datetime.now()
        self._report_callbacks: List[Callable] = []
        self._running = True
        self._flusher_thread = threading.Thread(target=self._background_flusher, daemon=True)
        self._flusher_thread.start()
        atexit.register(self.shutdown)

    def _get_thread_buffer(self) -> ThreadLocalBuffer:
        if not hasattr(self._thread_local, 'buffer'):
            self._thread_local.buffer = ThreadLocalBuffer(self, self.thread_buffer_size)
        return self._thread_local.buffer
    
    def _register_thread_buffer(self, buffer: ThreadLocalBuffer) -> None:
        with self._global_lock:
            self._thread_buffers.add(buffer)
    
    def _merge_thread_buffer(self, metrics: List[MetricData]) -> None:
        with self._global_lock:
            for metric in metrics:
                self._global_buffer[metric.name].append(metric)
            total = sum(len(v) for v in self._global_buffer.values())
            if total >= self.global_buffer_size or (datetime.now() - self.last_global_flush_time) >= self.flush_interval:
                self._flush_global_buffer()

    def add_metric(self, name: str, value: float, metric_type: MetricType = MetricType.TIMER, tags: Optional[Dict[str, str]] = None) -> None:
        metric = MetricData(name=name, value=value, metric_type=metric_type, tags=tags or {})
        self._get_thread_buffer().add(metric)

    def _flush_global_buffer(self) -> Dict[str, AggregatedStats]:
        with self._global_lock:
            if not self._global_buffer: return {}
            values_by_name = {name: [m.value for m in metrics] for name, metrics in self._global_buffer.items()}
            
            for name, values in values_by_name.items():
                if name not in self._aggregated_stats:
                    self._aggregated_stats[name] = AggregatedStats(name=name)
                for value in values:
                    self._aggregated_stats[name].update(value)
                self._aggregated_stats[name].finalize(values)
            
            self._global_buffer.clear()
            self.last_global_flush_time = datetime.now()
            
            stats_copy = {k: v for k, v in self._aggregated_stats.items()}
            for cb in self._report_callbacks:
                try: cb(stats_copy)
                except Exception as e: logger.error(f"Callback failed: {e}")
            return stats_copy

    def flush(self) -> Dict[str, AggregatedStats]:
        with self._global_lock:
            buffers = list(self._thread_buffers)
        for buf in buffers:
            try: buf.flush()
            except: pass
        return self._flush_global_buffer()

    def _background_flusher(self) -> None:
        while self._running:
            time.sleep(1.0)
            current_time = datetime.now()
            with self._global_lock:
                buffers = list(self._thread_buffers)
            for buf in buffers:
                try:
                    if (current_time - buf.last_flush_time) >= self.flush_interval:
                        buf.flush()
                except: pass

    def shutdown(self) -> None:
        self._running = False
        if self._flusher_thread.is_alive():
            self._flusher_thread.join(timeout=1.0)
        self.flush()

    def register_reporter(self, callback: Callable) -> None:
        with self._global_lock: self._report_callbacks.append(callback)
    
    def export_json(self) -> str:
        with self._global_lock:
            return json.dumps({k: v.to_dict() for k, v in self._aggregated_stats.items()}, indent=2)
    def export_prometheus(self) -> str:
        """
        Converts all aggregated metrics into Prometheus text format.
        Compatible with Prometheus 'Summary' type.
        """
        # 1. Force flush to get the latest data
        self.flush()
        
        lines = []
        
        for name, stats in self._aggregated_stats.items():
            # Prometheus allows underscores, but not dots.
            safe_name = name.replace(".", "_")
            
            # Header info
            lines.append(f"# HELP {safe_name} Metric for {name}")
            lines.append(f"# TYPE {safe_name} summary")
            
            # Base Stats (Count and Sum are standard for Summaries)
            lines.append(f'{safe_name}_count {stats.count}')
            lines.append(f'{safe_name}_sum {stats.total}')
            
            # Quantiles (P50, P90, P99)
            if stats.p50 is not None:
                lines.append(f'{safe_name}{{quantile="0.5"}} {stats.p50}')
            if stats.p90 is not None:
                lines.append(f'{safe_name}{{quantile="0.9"}} {stats.p90}')
            if stats.p95 is not None:
                lines.append(f'{safe_name}{{quantile="0.95"}} {stats.p95}')
            if stats.p99 is not None:
                lines.append(f'{safe_name}{{quantile="0.99"}} {stats.p99}')
                
        return "\n".join(lines)

    def export_csv(self) -> str:
        """
        Exports metrics as a CSV string compatible with Excel/Pandas.
        Columns: name, count, total, min, max, avg, p50, p90, p95, p99, std_dev
        """
        self.flush()
        
        # Define the header
        header = "name,count,total,min,max,avg,p50,p90,p95,p99,std_dev"
        lines = [header]
        
        for name, stats in self._aggregated_stats.items():
            # Helper to safely format None as empty string
            def fmt(val): 
                return str(val) if val is not None else ""
            
            row = [
                name,
                str(stats.count),
                str(stats.total),
                fmt(stats.min),
                fmt(stats.max),
                fmt(stats.avg),
                fmt(stats.p50),
                fmt(stats.p90),
                fmt(stats.p95),
                fmt(stats.p99),
                fmt(stats.std_dev)
            ]
            lines.append(",".join(row))
            
        return "\n".join(lines)
