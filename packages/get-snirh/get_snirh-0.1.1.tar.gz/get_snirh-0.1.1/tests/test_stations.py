import unittest
from unittest.mock import Mock, MagicMock
import pandas as pd
import io
from get_snirh.stations import StationFetcher
from get_snirh.client import SnirhClient

class TestStationFetcher(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock(spec=SnirhClient)
        self.fetcher = StationFetcher(self.mock_client)

    def test_get_station_codes(self):
        # Mock the CSV response for station codes (marker sites)
        # The format expected is a CSV where the first column is named "<markers>"
        # and contains quoted strings separated by something (the split logic uses ")
        # We need enough fields to satisfy the column dropping logic (indices 3, 15, 19, 27, 31 kept)
        # We use 7-digit codes so that "(1234567)" is 9 chars, matching the extraction logic
        
        # Create a row with enough columns (32 columns, indices 0-31)
        # Split indices: 3, 15, 19, 27, 31
        # List indices = (Split index - 1) / 2
        # List indices: 1, 7, 9, 13, 15
        row1 = ['"x"'] * 32
        row1[1] = '"site_123"'
        row1[7] = '"37.0"'
        row1[9] = '"-8.0"'
        row1[13] = '"Station A"'
        row1[15] = '"Station A (1234567)"'
        
        row2 = ['"x"'] * 32
        row2[1] = '"site_456"'
        row2[7] = '"37.1"'
        row2[9] = '"-8.1"'
        row2[13] = '"Station B"'
        row2[15] = '"Station B (7654321)"'

        csv_content = "<markers>\n" + ",".join(row1) + "\n" + ",".join(row2) + "\n"
        self.mock_client.fetch_csv.return_value = io.StringIO(csv_content)

        df = self.fetcher.get_station_codes(use_web=True)

        self.assertEqual(len(df), 2)
        self.assertIn('marker_site', df.columns)
        self.assertIn('code', df.columns)
        self.assertEqual(df.iloc[0]['marker_site'], 'site_123')
        self.assertEqual(df.iloc[0]['code'], '1234567')

    def test_get_all_stations(self):
        # Mock the CSV response for station metadata
        # Skips 3 rows
        csv_content = """Header1
Header2
Header3
CÓDIGO,BACIA,RIO
123,RIBEIRAS DO ALGARVE,River A
456,TEJO,River B
"""
        self.mock_client.fetch_csv.return_value = io.StringIO(csv_content)

        df = self.fetcher.get_all_stations(use_web=True)

        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]['CÓDIGO'], '123')
        self.assertEqual(df.iloc[0]['BACIA'], 'RIBEIRAS DO ALGARVE')

    def test_get_stations_with_metadata_filtered(self):
        # Mock get_station_codes
        codes_df = pd.DataFrame({
            'marker_site': ['site_123', 'site_456'],
            'code': ['123', '456'], # Note: code is string in one, int in other? 
                                     # In stations.py: extract_station_code returns string.
                                     # In get_all_stations mock above, pandas reads int.
                                     # The merge might fail if types don't match.
                                     # Let's check stations.py merge: left_on='CÓDIGO', right_on='code'
        })
        
        # Mock get_all_stations
        # We need to ensure types match for merge. 
        # If 'code' is string '123', 'CÓDIGO' should probably be cast or be string.
        # In real pandas read_csv, if it looks like int, it becomes int.
        # Let's assume we need to handle type mismatch in the implementation or mock.
        # For this test, I'll make CÓDIGO strings to be safe, or rely on pandas smarts.
        meta_df = pd.DataFrame({
            'CÓDIGO': ['123', '456'], # Strings to match codes_df
            'BACIA': ['RIBEIRAS DO ALGARVE', 'TEJO']
        })

        # We mock the methods of the fetcher itself to isolate the merge logic
        # But get_stations_with_metadata calls self.get_station_codes() and self.get_all_stations()
        # So we can mock those methods on the instance.
        
        self.fetcher.get_station_codes = Mock(return_value=codes_df)
        self.fetcher.get_all_stations = Mock(return_value=meta_df)

        # Test filtering
        result = self.fetcher.get_stations_with_metadata(basin_filter=['RIBEIRAS DO ALGARVE'])

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['code'], '123')
        self.assertEqual(result.iloc[0]['BACIA'], 'RIBEIRAS DO ALGARVE')

if __name__ == '__main__':
    unittest.main()
