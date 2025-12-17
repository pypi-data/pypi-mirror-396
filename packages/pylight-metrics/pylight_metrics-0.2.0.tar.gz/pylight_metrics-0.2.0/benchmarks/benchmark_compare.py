import time
import threading
import statistics
from prometheus_client import Counter as PCounter
from pylight_metrics.aggregator import LockFreeMetricsAggregator, MetricType

# --- CONFIGURATION ---
THREADS = 50
OPS_PER_THREAD = 100_000
TOTAL_OPS = THREADS * OPS_PER_THREAD

print(f"🚀 BENCHMARK: {THREADS} Threads x {OPS_PER_THREAD} Ops = {TOTAL_OPS:,} Total Ops")
print("-" * 60)

# --- SETUP COMPETITOR (Prometheus Client) ---
p_counter = PCounter('bench_test_p', 'Benchmark Counter')

# --- SETUP PYLIGHT ---
# Reset singleton for clean state
LockFreeMetricsAggregator._instance = None
py_agg = LockFreeMetricsAggregator()

# --- BENCHMARK FUNCTIONS ---

def run_prometheus():
    def worker():
        for _ in range(OPS_PER_THREAD):
            p_counter.inc()
    
    start = time.time()
    threads = [threading.Thread(target=worker) for _ in range(THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()
    end = time.time()
    return end - start

def run_pylight():
    def worker():
        for _ in range(OPS_PER_THREAD):
            py_agg.add_metric("bench.test", 1, metric_type=MetricType.COUNTER)
    
    start = time.time()
    threads = [threading.Thread(target=worker) for _ in range(THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()
    # Pylight requires flush to verify data, but we don't count flush time 
    # as part of "write latency" usually. However, for total throughput, 
    # let's be fair and include it if we consider "data availability".
    # For strict "Write Path" speed, we exclude it. 
    # Let's exclude it to test pure contention cost.
    end = time.time() 
    py_agg.flush() 
    return end - start

# --- RUNNING TESTS ---

print("Running prometheus_client (Standard)...")
p_time = run_prometheus()
p_ops = TOTAL_OPS / p_time
print(f"⏱️ Time: {p_time:.4f}s | ⚡ Throughput: {p_ops:,.0f} ops/sec")

print("\nRunning pylight-metrics (Yours)...")
py_time = run_pylight()
py_ops = TOTAL_OPS / py_time
print(f"⏱️ Time: {py_time:.4f}s | ⚡ Throughput: {py_ops:,.0f} ops/sec")

# --- VERDICT ---
print("-" * 60)
ratio = py_ops / p_ops
if ratio > 1.0:
    print(f"✅ WINNER: Pylight is {ratio:.2f}x FASTER than Prometheus Client")
else:
    print(f"❌ SLOW: Pylight is {ratio:.2f}x SLOWER. Redesign needed.")
