import unittest
import os
from get_snirh import Snirh, Parameters

@unittest.skipUnless(os.getenv('RUN_LIVE_TESTS'), "Skipping live tests. Set RUN_LIVE_TESTS=1 to run.")
class TestLiveIntegration(unittest.TestCase):
    """
    These tests hit the actual SNIRH servers.
    They are skipped by default to prevent network dependency in standard test runs.
    """

    def test_fetch_stations_all_networks(self):
        """Test fetching station lists for all supported networks."""
        networks = [
            'piezometria', 
            'meteorologica', 
            'qualidade', 
            'hidrometrica', 
            'qualidade_superficial'
        ]
        
        for network in networks:
            with self.subTest(network=network):
                print(f"\n[Live] Testing network station fetch: {network}")
                snirh = Snirh(network=network)
                # Fetch stations (limit to a small basin to be faster if possible)
                # Using 'RIBEIRAS DO ALGARVE' as it's usually smaller than 'TEJO' or 'DOURO'
                stations = snirh.stations.get_stations_with_metadata(basin_filter=['RIBEIRAS DO ALGARVE'])
                
                self.assertGreater(len(stations), 0, f"Should find stations for {network}")
                print(f"Found {len(stations)} stations for {network}")

    def test_fetch_data_meteorologica(self):
        """Test fetching data for Meteorologica network (Precipitation)."""
        print("\n[Live] Testing data fetch: meteorologica")
        snirh = Snirh(network='meteorologica')
        stations = snirh.stations.get_stations_with_metadata(basin_filter=['RIBEIRAS DO ALGARVE'])
        
        # Try a few stations to increase chance of finding data
        target_stations = stations.head(5)
        
        df = snirh.data.get_timeseries(
            station_codes=target_stations,
            parameter=Parameters.PRECIPITATION_DAILY,
            start_date='01/01/2023',
            end_date='31/01/2023'
        )
        
        self.assertIsNotNone(df)
        print(f"Fetched {len(df)} rows for meteorologica.")
        
        if not df.empty:
            self.assertIn('site_name', df.columns)
            self.assertIn('value', df.columns)
            self.assertEqual(df['parameter'].iloc[0], 'PRECIPITATION_DAILY')

    def test_fetch_data_piezometria(self):
        """Test fetching data for Piezometria network (Groundwater Level)."""
        print("\n[Live] Testing data fetch: piezometria")
        snirh = Snirh(network='piezometria')
        stations = snirh.stations.get_stations_with_metadata(basin_filter=['RIBEIRAS DO ALGARVE'])
        
        target_stations = stations.head(5)
        
        df = snirh.data.get_timeseries(
            station_codes=target_stations,
            parameter=Parameters.GWL_DEPTH,
            start_date='01/01/2023',
            end_date='31/01/2023'
        )
        
        self.assertIsNotNone(df)
        print(f"Fetched {len(df)} rows for piezometria.")
        
        if not df.empty:
            self.assertIn('site_name', df.columns)
            self.assertIn('value', df.columns)
            self.assertEqual(df['parameter'].iloc[0], 'GWL_DEPTH')
