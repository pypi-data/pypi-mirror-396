import unittest
from unittest.mock import Mock, MagicMock
import io
import pandas as pd
from get_snirh import Snirh, Parameters

class TestIntegrationWorkflow(unittest.TestCase):
    def test_full_workflow(self):
        """
        Simulates the workflow from examples/example_gwl_algarve.ipynb
        """
        snirh = Snirh()
        
        # 1. Mock Station Fetching
        # We need to mock the client responses for get_station_codes and get_all_stations
        
        # Response for get_station_codes (marker sites)
        # Needs enough fields to match the parsing logic (indices 3, 15, 19, 27, 31)
        # List indices: 1, 7, 9, 13, 15
        
        def make_row(site, lat, lon, name, code_str):
            r = ['"x"'] * 32
            r[1] = f'"{site}"'
            r[7] = f'"{lat}"'
            r[9] = f'"{lon}"'
            r[13] = f'"{name}"'
            r[15] = f'"{name} ({code_str})"'
            return ",".join(r)

        codes_csv = "<markers>\n" + \
                    make_row("site_A", "37.0", "-8.0", "Station A", "1000001") + "\n" + \
                    make_row("site_B", "37.1", "-8.1", "Station B", "1000002") + "\n" + \
                    make_row("site_C", "37.2", "-8.2", "Station C", "1000003") + "\n"
        
        # Response for get_all_stations (metadata)
        meta_csv = """Header1
Header2
Header3
CÓDIGO,BACIA,RIO
1000001,RIBEIRAS DO ALGARVE,River A
1000002,GUADIANA,River B
1000003,TEJO,River C
"""

        # Response for Data Fetching
        data_csv = """Header1
Header2
Header3
Date,Value
01/01/2023,15.5
Footer
"""

        # Setup the side_effect for fetch_csv to return the correct content based on URL
        def fetch_side_effect(url):
            if "xml_listaestacoes.php" in url:
                return io.StringIO(codes_csv)
            elif "lista_csv.php" in url:
                return io.StringIO(meta_csv)
            elif "dados_csv.php" in url:
                return io.StringIO(data_csv)
            else:
                raise ValueError(f"Unexpected URL: {url}")

        snirh.client.fetch_csv = Mock(side_effect=fetch_side_effect)

        # --- Workflow Execution ---

        # 2. Fetch and Filter Stations
        algarve_basins = ['RIBEIRAS DO ALGARVE', 'GUADIANA']
        stations = snirh.stations.get_stations_with_metadata(basin_filter=algarve_basins, use_web=True)
        # Expecting Station A (Algarve) and Station B (Guadiana). Station C is Tejo.
        self.assertEqual(len(stations), 2)
        self.assertIn('1000001', stations['code'].values) # Note: code is string '1000001'
        # Wait, in test_stations.py I noted potential type mismatch.
        # If meta_csv parses CÓDIGO as int 1001, and code is string "1001", merge might fail.
        # Let's see if pandas handles it. If not, we might need to fix the implementation.
        
        # 3. Extract Codes
        # 3. Extract Codes
        station_codes = stations['marker_site'].tolist()
        self.assertIn('site_A', station_codes)
        self.assertIn('site_B', station_codes)

        # 4. Fetch Data
        df_gwl = snirh.data.get_timeseries(
            station_codes=station_codes,
            parameter=Parameters.GWL_DEPTH,
            start_date='01/01/2023',
            end_date='31/12/2023'
        )

        # We expect data for both stations (2 rows total, 1 per station)
        self.assertEqual(len(df_gwl), 2)
        self.assertEqual(set(df_gwl['site_name']), {'site_A', 'site_B'})
        self.assertEqual(df_gwl.iloc[0]['value'], 15.5)

if __name__ == '__main__':
    unittest.main()
