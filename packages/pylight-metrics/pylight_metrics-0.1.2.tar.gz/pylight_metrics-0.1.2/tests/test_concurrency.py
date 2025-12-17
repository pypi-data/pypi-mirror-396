import unittest
import threading
import time
import random
from pylight_metrics.aggregator import LockFreeMetricsAggregator, MetricType

class TestConcurrency(unittest.TestCase):
    def setUp(self):
        # Reset the aggregator before each test so we start clean
        self.aggregator = LockFreeMetricsAggregator()
        self.aggregator._aggregated_stats.clear()
        self.aggregator._global_buffer.clear()

    def test_heavy_concurrency(self):
        """
        The Fire Test: 50 Threads x 1000 Ops = 50,000 Total Metrics.
        """
        print("\nStarting Fire Test: 50 Threads x 1000 Ops...")
        
        def worker():
            for _ in range(1000):
                # Simulate a tiny random delay to make threads fight for resources
                val = random.uniform(0.1, 0.5)
                self.aggregator.add_metric(
                    "request_latency", 
                    val, 
                    MetricType.TIMER
                )
        
        threads = []
        start_time = time.time()
        
        # 1. Spawn 50 threads
        for _ in range(50):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
            
        # 2. Wait for all threads to finish
        for t in threads:
            t.join()
            
        print(f"Threads finished in {time.time() - start_time:.4f}s. Flushing buffers...")
        
        # 3. Force flush all thread-local data to the main storage
        self.aggregator.shutdown()
        
        # 4. Check results
        stats = self.aggregator._aggregated_stats.get("request_latency")
        
        self.assertIsNotNone(stats, "Metric 'request_latency' should exist")
        print(f"Total Count Captured: {stats.count}")
        
        # CRITICAL PROOF: Did we lose any data?
        self.assertEqual(stats.count, 50000, "Data Loss Detected! Thread safety failed.")
        print("✅ SUCCESS: 50,000/50,000 metrics captured safely.")

if __name__ == '__main__':
    unittest.main()
