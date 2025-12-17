import time
import threading
import random
from prometheus_client import Summary
from pylight_metrics.aggregator import LockFreeMetricsAggregator, MetricType

# --- CONFIGURATION ---
THREADS = 50
OPS_PER_THREAD = 20_000 # Calculating percentiles is heavy, so fewer ops
TOTAL_OPS = THREADS * OPS_PER_THREAD

print(f"⏱️ TIMER BENCHMARK: {THREADS} Threads x {OPS_PER_THREAD} Ops = {TOTAL_OPS:,} Total Ops")
print("-" * 60)

# --- SETUP COMPETITOR ---
# Prometheus Summary calculates quantiles
p_summary = Summary('bench_timer_p', 'Benchmark Timer')

# --- SETUP PYLIGHT ---
LockFreeMetricsAggregator._instance = None
py_agg = LockFreeMetricsAggregator()

# --- RUN FUNCTIONS ---

def run_prometheus():
    def worker():
        for _ in range(OPS_PER_THREAD):
            # Observe a fake duration (0.01 to 0.1s)
            p_summary.observe(random.random() * 0.1)
    
    start = time.time()
    threads = [threading.Thread(target=worker) for _ in range(THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()
    end = time.time()
    return end - start

def run_pylight():
    def worker():
        for _ in range(OPS_PER_THREAD):
            py_agg.add_metric("bench.timer", random.random() * 0.1, metric_type=MetricType.TIMER)
    
    start = time.time()
    threads = [threading.Thread(target=worker) for _ in range(THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    # NOTE: We do NOT include flush() time here. 
    # Why? Because your value proposition is "Low Latency for the Application".
    # The application thread shouldn't care how long flush takes later.
    end = time.time() 
    return end - start

# --- RUNNING TESTS ---

print("Running prometheus_client Summary...")
p_time = run_prometheus()
p_ops = TOTAL_OPS / p_time
print(f"⏱️ Time: {p_time:.4f}s | ⚡ Write Throughput: {p_ops:,.0f} ops/sec")

print("\nRunning pylight-metrics Timer...")
py_time = run_pylight()
py_ops = TOTAL_OPS / py_time
print(f"⏱️ Time: {py_time:.4f}s | ⚡ Write Throughput: {py_ops:,.0f} ops/sec")

# --- VERDICT ---
print("-" * 60)
ratio = py_ops / p_ops
if ratio > 1.0:
    print(f"✅ WINNER: Pylight Writes are {ratio:.2f}x FASTER")
else:
    print(f"❌ SLOWER: Pylight Writes are {ratio:.2f}x slower")
# --- FLUSH COST TEST ---

print("-" * 60)
print("Testing Flush Cost (Calculating Percentiles for 1M items)...")
start_flush = time.time()
stats = py_agg.flush() # This triggers the heavy sort
end_flush = time.time()

flush_duration = end_flush - start_flush
print(f"🧹 Flush Duration: {flush_duration:.4f}s")
print(f"📊 Stats Calculated: {len(stats)} metrics")
