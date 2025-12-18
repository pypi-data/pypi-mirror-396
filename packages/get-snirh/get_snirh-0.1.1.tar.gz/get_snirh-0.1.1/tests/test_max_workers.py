import unittest
from unittest.mock import MagicMock, patch
from get_snirh.data import DataFetcher
from get_snirh.client import SnirhClient

class TestMaxWorkers(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=SnirhClient)
        self.fetcher = DataFetcher(self.client)

    @patch('get_snirh.data.as_completed')
    @patch('get_snirh.data.ThreadPoolExecutor')
    def test_max_workers_default(self, mock_executor, mock_as_completed):
        # Mock the context manager
        mock_executor.return_value.__enter__.return_value = MagicMock()
        # Mock as_completed to return immediately
        mock_as_completed.return_value = []
        
        # Test with 5 stations -> should use 5 workers
        stations = {f"s{i}": f"Station {i}" for i in range(5)}
        self.fetcher.get_timeseries(stations, "123", "01/01/2020", "01/01/2021")
        mock_executor.assert_called_with(max_workers=5)

    @patch('get_snirh.data.as_completed')
    @patch('get_snirh.data.ThreadPoolExecutor')
    def test_max_workers_capped(self, mock_executor, mock_as_completed):
        # Mock the context manager
        mock_executor.return_value.__enter__.return_value = MagicMock()
        # Mock as_completed to return immediately
        mock_as_completed.return_value = []

        # Test with 20 stations -> should cap at 10 workers
        stations = {f"s{i}": f"Station {i}" for i in range(20)}
        self.fetcher.get_timeseries(stations, "123", "01/01/2020", "01/01/2021")
        mock_executor.assert_called_with(max_workers=10)

    @patch('get_snirh.data.as_completed')
    @patch('get_snirh.data.ThreadPoolExecutor')
    def test_max_workers_explicit(self, mock_executor, mock_as_completed):
        # Mock the context manager
        mock_executor.return_value.__enter__.return_value = MagicMock()
        # Mock as_completed to return immediately
        mock_as_completed.return_value = []

        # Test with explicit max_workers=2
        stations = {f"s{i}": f"Station {i}" for i in range(20)}
        self.fetcher.get_timeseries(stations, "123", "01/01/2020", "01/01/2021", max_workers=2)
        mock_executor.assert_called_with(max_workers=2)

if __name__ == '__main__':
    unittest.main()
