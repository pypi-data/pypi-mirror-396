import unittest
from unittest.mock import Mock
import pandas as pd
import io
from get_snirh.data import DataFetcher
from get_snirh.client import SnirhClient
from get_snirh.constants import Parameters

class TestDataFetcher(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock(spec=SnirhClient)
        self.fetcher = DataFetcher(self.mock_client)

    def test_get_timeseries(self):
        # Mock CSV response for a station
        # Skips 3 rows, reads Date and Value
        csv_content = """Header1
Header2
Header3
Date,Value
01/01/2023,10.5
02/01/2023,12.0
Footer
"""
        self.mock_client.fetch_csv.return_value = io.StringIO(csv_content)

        station_codes = ['site_123']
        parameter = Parameters.PRECIPITATION_DAILY
        start_date = '01/01/2023'
        end_date = '02/01/2023'

        df = self.fetcher.get_timeseries(station_codes, parameter, start_date, end_date)

        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['site_name'], 'site_123')
        self.assertEqual(df.iloc[0]['value'], 10.5)
        # Check date parsing
        # Date is returned as string in current implementation
        self.assertEqual(df.iloc[0]['date'], '01/01/2023')

    def test_get_timeseries_multiple_stations(self):
        # Mock CSV response
        csv_content = """Header1
Header2
Header3
Date,Value
01/01/2023,10.0
Footer
"""
        # Use side_effect to return a NEW StringIO object each time
        self.mock_client.fetch_csv.side_effect = lambda url: io.StringIO(csv_content)

        station_codes = ['site_123', 'site_456']
        df = self.fetcher.get_timeseries(station_codes, 'some_param', '01/01/2023', '01/01/2023')

        self.assertEqual(len(df), 2)
        self.assertEqual(set(df['site_name']), {'site_123', 'site_456'})

    def test_get_timeseries_error_handling(self):
        # Simulate one station failing and one succeeding
        
        def side_effect(url):
            if 'site_fail' in url:
                raise Exception("Network Error")
            return io.StringIO("""Header1
Header2
Header3
Date,Value
01/01/2023,5.0
Footer
""")

        self.mock_client.fetch_csv.side_effect = side_effect

        station_codes = ['site_fail', 'site_ok']
        df = self.fetcher.get_timeseries(station_codes, 'some_param', '01/01/2023', '01/01/2023')

        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['site_name'], 'site_ok')

if __name__ == '__main__':
    unittest.main()
