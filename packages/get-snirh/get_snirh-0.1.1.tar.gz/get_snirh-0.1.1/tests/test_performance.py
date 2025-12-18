import unittest
import os
import time
import logging
from get_snirh import Snirh, Parameters

# Configure logging to see the output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@unittest.skipUnless(os.getenv('RUN_LIVE_TESTS'), "Skipping live tests. Set RUN_LIVE_TESTS=1 to run.")
class TestPerformance(unittest.TestCase):
    """
    Benchmarks performance with different worker counts.
    """

    def setUp(self):
        self.snirh = Snirh(network="piezometria", verbose=True)
        # Fetch a list of stations first (Algarve basin for a reasonable size)
        self.stations = self.snirh.stations.get_stations_with_metadata(
            basin_filter=['RIBEIRAS DO ALGARVE']
        )
        # Limit to first 20 stations to be polite but significant enough
        self.stations = self.stations.head(20)
        logger.info(f"Benchmarking with {len(self.stations)} stations.")

    def test_concurrency_speedup(self):
        """
        Verifies that using multiple workers is faster than a single worker.
        """
        # 1. Run with 1 worker (Sequential)
        start_time = time.time()
        df_1 = self.snirh.data.get_timeseries(
            station_codes=self.stations,
            parameter=Parameters.GWL_DEPTH,
            start_date='01/01/2024',
            end_date='01/02/2024',
            max_workers=1
        )
        duration_1 = time.time() - start_time
        logger.info(f"Duration with 1 worker: {duration_1:.2f}s")
        
        # Ensure we actually got data, otherwise the test is meaningless
        self.assertFalse(df_1.empty, "Sequential fetch returned no data. Check network/server status.")

        # 2. Run with 10 workers (Concurrent)
        start_time = time.time()
        df_10 = self.snirh.data.get_timeseries(
            station_codes=self.stations,
            parameter=Parameters.GWL_DEPTH,
            start_date='01/01/2024',
            end_date='01/02/2024',
            max_workers=10
        )
        duration_10 = time.time() - start_time
        logger.info(f"Duration with 10 workers: {duration_10:.2f}s")
        
        # Ensure we actually got data
        self.assertFalse(df_10.empty, "Concurrent fetch returned no data. Check network/server status.")

        # Assert speedup
        # We expect at least 2x speedup (conservative estimate due to overhead/network latency)
        self.assertLess(duration_10, duration_1, "Concurrent execution should be faster")
        speedup = duration_1 / duration_10
        logger.info(f"Speedup factor: {speedup:.2f}x")
        
        if speedup < 1.5:
            logger.warning("Speedup was less than 1.5x. Network latency or server rate limiting might be a factor.")

if __name__ == '__main__':
    unittest.main()
