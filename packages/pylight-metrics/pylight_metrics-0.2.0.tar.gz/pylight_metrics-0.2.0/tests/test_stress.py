import unittest
import threading
import time
from pylight_metrics.aggregator import LockFreeMetricsAggregator, MetricType

class TestConcurrency(unittest.TestCase):
    def setUp(self):
        """
        Clean setup for every test.
        """
        self.agg = LockFreeMetricsAggregator()
        
        # 1. Clear the final stats
        self.agg._aggregated_stats.clear()
        
        # 2. Clear the global buffer
        with self.agg._global_lock:
            self.agg._global_buffer.clear()
            
        # 3. Clear any lingering thread buffers
        self.agg._thread_buffers.clear()

    def test_high_concurrency_counting(self):
        """
        The Ultimate Test:
        Launch 50 threads. Each thread adds 100 metrics.
        Total should be exactly 5000.
        """
        THREADS = 50
        UPDATES_PER_THREAD = 100
        EXPECTED_TOTAL = THREADS * UPDATES_PER_THREAD

        # Define the worker function
        def worker():
            for _ in range(UPDATES_PER_THREAD):
                self.agg.add_metric("stress.test", 1, metric_type=MetricType.COUNTER)
            
            # CRITICAL FIX: Flush BEFORE thread death!
            # Once this function ends, the thread dies and TLS is erased.
            # We must save the data to Global state now.
            self.agg.flush()

        threads = []
        print(f"\nStarting Stress Test: {THREADS} Threads x {UPDATES_PER_THREAD} Ops...")
        
        # Launch Threads
        for _ in range(THREADS):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()

        # Final check (Safe to flush again, though workers already did it)
        stats = self.agg.flush()

        # Debug Print
        if "stress.test" in stats:
            actual_count = stats["stress.test"].count
            print(f"✅ Success! Expected: {EXPECTED_TOTAL}, Actual: {actual_count}")
        else:
            print("❌ Failed: Metric still missing.")
            actual_count = 0

        # Assertions
        self.assertIn("stress.test", stats, "Metric stress.test was not recorded!")
        self.assertEqual(actual_count, EXPECTED_TOTAL, 
                         f"Race condition detected! Expected {EXPECTED_TOTAL}, Got {actual_count}")

if __name__ == '__main__':
    unittest.main()
