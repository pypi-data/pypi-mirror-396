import unittest
from pylight_metrics.aggregator import LockFreeMetricsAggregator, MetricType

class TestMetricsAggregator(unittest.TestCase):
    def setUp(self):
        """Runs before EVERY test."""
        self.agg = LockFreeMetricsAggregator()
        # FORCE RESET: Since it's a Singleton, we must wipe old data manually
        self.agg._aggregated_stats = {}
        self.agg._global_buffer.clear()

    def test_counter_increment(self):
        """Test if basic counting works."""
        self.agg.add_metric("user.login", 1, metric_type=MetricType.COUNTER)
        self.agg.add_metric("user.login", 1, metric_type=MetricType.COUNTER)
        
        # 'flush' merges data and returns the stats dictionary
        stats = self.agg.flush()
        
        # Expecting: count=2, total=2
        self.assertIn("user.login", stats)
        self.assertEqual(stats["user.login"].count, 2)
        self.assertEqual(stats["user.login"].total, 2.0)

    def test_timer_accuracy(self):
        """Test if timer records roughly correct duration."""
        self.agg.add_metric("db.query", 0.100, metric_type=MetricType.TIMER)
        self.agg.add_metric("db.query", 0.200, metric_type=MetricType.TIMER)
        
        stats = self.agg.flush()
        
        # Average should be 0.150
        self.assertAlmostEqual(stats["db.query"].avg, 0.150, places=3)
        # Max should be 0.200
        self.assertEqual(stats["db.query"].max, 0.200)

    def test_prometheus_format(self):
        """Test if the text output looks like Prometheus format."""
        self.agg.add_metric("api.requests", 1, metric_type=MetricType.COUNTER)
        
        output = self.agg.export_prometheus()
        
        # Check for Prometheus lines
        self.assertIn("# TYPE api_requests summary", output)
        self.assertIn("api_requests_count 1", output)

if __name__ == '__main__':
    unittest.main()
