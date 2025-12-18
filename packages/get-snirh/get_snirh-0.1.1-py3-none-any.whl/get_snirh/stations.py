import os
import logging
import pandas as pd
from typing import List, Optional
from .client import SnirhClient
from .constants import SnirhUrls
from .utils import clean_station_name, extract_station_code
from .exceptions import SnirhParsingError

logger = logging.getLogger(__name__)

class StationFetcher:
    """
    Fetches and filters station metadata.
    """

    NETWORK_FILES = {
        "piezometria": {
            "metadata": "rede_Piezometria.csv",
            "stations": "station_list_piez.csv"
        },
        "meteorologica": {
            "metadata": "rede_Meteorologica.csv",
            "stations": "station_list_meteo.csv"
        },
        "qualidade": {
            "metadata": "rede_Qualidadeaguassubterraneas.csv",
            "stations": "station_list_quality.csv"
        },
        "hidrometrica": {
            "metadata": "rede_seleccao_Hidrometrica.csv",
            "stations": "station_list_sw_hidrometrica.csv"
        },
        "qualidade_superficial": {
            "metadata": "rede_seleccao_Qualidade.csv",
            "stations": "station_list_sw_quality.csv"
        }
    }

    def __init__(self, client: SnirhClient, network: str = "piezometria"):
        self.client = client
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        if network not in self.NETWORK_FILES:
             logger.warning("Unknown network '%s'. Defaulting to 'piezometria'.", network)
             network = "piezometria"
        
        self.network = network
        files = self.NETWORK_FILES[network]
        
        self._default_station_list = os.path.join(self._data_dir, files["stations"])
        self._default_metadata = os.path.join(self._data_dir, files["metadata"])
        
        logger.debug("StationFetcher initialized. Network: %s, Data dir: %s", network, self._data_dir)

    def get_all_stations(self, s_cover: str = "100290946", local_file: Optional[str] = None, use_web: bool = False) -> pd.DataFrame:
        """
        Fetches the master list of stations.
        
        Args:
            s_cover: The coverage parameter for the station list. 
                     Default is "100290946" (as seen in 2025 notebook).
            local_file: Path to local CSV file to use instead of fetching.
            use_web: If True, force fetch from web (ignoring local defaults).
                     
        Returns:
            pd.DataFrame: Cleaned dataframe of stations.
        """
        logger.info("Getting all stations (s_cover=%s, use_web=%s)", s_cover, use_web)
        try:
            if not use_web:
                # Use provided local file or default bundled file
                file_path = local_file if local_file else self._default_metadata
                if os.path.exists(file_path):
                    logger.info("Reading station metadata from local file: %s", file_path)
                    
                    # Helper to normalize columns
                    def normalize_cols(d):
                        return d.rename(columns={'CDIGO': 'CÓDIGO', 'SISTEMA AQUFERO': 'SISTEMA AQUÍFERO'})

                    # Read from local file
                    # Try reading as standard CSV first (clean format)
                    try:
                        df = pd.read_csv(file_path, encoding='ISO-8859-1', dtype={'CÓDIGO': str, 'CDIGO': str})
                        df = normalize_cols(df)
                        if 'BACIA' in df.columns:
                             logger.debug("Successfully read clean CSV")
                             return df
                    except Exception:
                        pass

                    # Fallback to SNIRH format (skiprows=3 or 4)
                    logger.debug("Attempting to read as raw SNIRH CSV")
                    
                    # Try skiprows=4 first (common in local files)
                    try:
                        df = pd.read_csv(file_path, sep=',', skiprows=4, index_col=False, encoding='ISO-8859-1', dtype={'CÓDIGO': str, 'CDIGO': str})
                        df = normalize_cols(df)
                        if 'CÓDIGO' in df.columns:
                             pass
                        else:
                             raise ValueError("Header not found at row 4")
                    except Exception:
                        # Try skiprows=3
                        logger.debug("Fallback to skiprows=3")
                        df = pd.read_csv(file_path, sep=',', skiprows=3, index_col=False, encoding='ISO-8859-1', dtype={'CÓDIGO': str, 'CDIGO': str})
                        df = normalize_cols(df)
                    
                    # Clean up potential garbage rows (e.g. footer text appearing as data)
                    if 'BACIA' in df.columns:
                        df = df.dropna(subset=['BACIA'])
                    return df
            
            # Fallback to web or if use_web is True
            logger.info("Fetching station metadata from web URL")
            url = f"{SnirhUrls.STATION_LIST_CSV}?obj_janela=INFO_ESTACOES&s_cover={s_cover}&tp_lista=&completa=1&formato=csv"
            csv_buffer = self.client.fetch_csv(url)
            # Skip initial rows as per notebook
            df = pd.read_csv(csv_buffer, sep=',', skiprows=3, index_col=False, dtype={'CÓDIGO': str, 'CDIGO': str})
            
            # Clean up potential garbage rows (e.g. footer text appearing as data)
            if 'BACIA' in df.columns:
                df = df.dropna(subset=['BACIA'])
            
            return df
            
        except Exception as e:
            logger.error("Failed to parse station list: %s", str(e))
            raise SnirhParsingError(f"Failed to parse station list: {str(e)}") from e

    def get_station_codes(self, local_file: Optional[str] = None, use_web: bool = False) -> pd.DataFrame:
        """
        Fetches the station codes (marker sites).
        If local_file is provided, reads from there.
        Otherwise tries to fetch from the XML endpoint.
        """
        logger.info("Getting station codes (use_web=%s)", use_web)
        try:
            if not use_web:
                file_path = local_file if local_file else self._default_station_list
                if os.path.exists(file_path):
                    logger.info("Reading station codes from local file: %s", file_path)
                    # Try reading as standard CSV first (clean format)
                    try:
                        df_clean = pd.read_csv(file_path, encoding='ISO-8859-1')
                        if 'marker_site' in df_clean.columns:
                            logger.debug("Successfully read clean CSV with 'marker_site'")
                            if 'code' not in df_clean.columns:
                                if 'codigo' in df_clean.columns:
                                     df_clean['code'] = df_clean['codigo']
                                else:
                                     df_clean['code'] = extract_station_code(df_clean['estacao'])
                            return df_clean
                        elif 'marker site' in df_clean.columns:
                            logger.debug("Successfully read clean CSV with 'marker site'")
                            df_clean = df_clean.rename(columns={'marker site': 'marker_site'})
                            if 'code' not in df_clean.columns:
                                if 'codigo' in df_clean.columns:
                                     df_clean['code'] = df_clean['codigo']
                                else:
                                     df_clean['code'] = extract_station_code(df_clean['estacao'])
                            return df_clean
                    except Exception:
                        pass # Fallback to raw parsing

                    logger.debug("Attempting to read as raw SNIRH CSV (sep='|')")
                    df = pd.read_csv(file_path, encoding='ISO-8859-1', sep='|', engine='python', quoting=3)
                else:
                     # If default file missing and no local file provided, force web?
                     # Or raise error?
                     # Let's try web if file missing
                     logger.warning("Local station file not found at %s. Falling back to web.", file_path)
                     use_web = True

            if use_web:
                # This URL is mentioned in the markdown of the notebook
                logger.info("Fetching station codes from web URL")
                url = "https://snirh.apambiente.pt/snirh/_dadosbase/site/xml/xml_listaestacoes.php"
                csv_buffer = self.client.fetch_csv(url)
                df = pd.read_csv(csv_buffer, encoding='ISO-8859-1', sep='|', engine='python', quoting=3)
            
            if df.empty:
                raise SnirhParsingError("Station list dataframe is empty.")

            # Logic from notebook to split the weird string
            # df_station = df_station["<markers>"].str.split('"', expand = True)
            # But here we read it without header, so it's likely in column 0
            
            # The notebook reads `input/station_list.csv`.
            # Let's assume the response from that URL is what was saved to that file.
            
            # If the file starts with <markers>, pandas might read it weirdly.
            # Let's try to replicate the notebook logic exactly.
            # df_station = pd.read_csv('input/station_list.csv',encoding='ISO-8859-1')
            # df_station = df_station["<markers>"].str.split('"', expand = True)
            
            # So the column name is "<markers>".
            # This implies the first line of the file is `<markers>`.
            
            if "<markers>" not in df.columns:
                # Fallback if the header isn't exactly <markers>
                # Maybe it's a single column dataframe
                col_name = df.columns[0]
                split_df = df[col_name].str.split('"', expand=True)
            else:
                split_df = df["<markers>"].str.split('"', expand=True)

            # cols to drop from notebook
            # cols_drop = [0,2,3,4,5,6,8,10,11,12,14,16,17,18,19,20]
            # Instead of dropping, let's select the columns we expect based on the notebook logic
            # Expected indices based on debug output:
            # 3 (marker site), 15 (lat), 19 (lng), 27 (estacao3), 31 (estacao)
            
            target_indices = [3, 15, 19, 27, 31]
            
                        # Check if we have enough columns
            if split_df.shape[1] <= max(target_indices):
                 logger.error("Not enough columns after split. Got %d, needed > %d", split_df.shape[1], max(target_indices))
                 raise SnirhParsingError(f"Not enough columns after split. Got {split_df.shape[1]}, needed > {max(target_indices)}")

            split_df = split_df.iloc[:, target_indices]
            split_df.columns = ['marker_site', 'latitude', 'longitude', 'estacao3', 'estacao']

            # Change the column names
            # Note: The notebook assumes specific structure. This is fragile but requested.
            split_df.columns = ['marker_site', 'latitude', 'longitude', 'estacao3', 'estacao']
            
            # Clean data
            split_df['estacao3'] = clean_station_name(split_df['estacao3'])
            split_df['estacao'] = clean_station_name(split_df['estacao'])
            
            # Extract code
            split_df['code'] = extract_station_code(split_df['estacao'])
            
            return split_df

        except Exception as e:
            logger.error("Failed to parse station codes: %s", str(e))
            raise SnirhParsingError(f"Failed to parse station codes: {str(e)}") from e

    def get_stations_with_metadata(self, basin_filter: Optional[List[str]] = None, local_station_file: Optional[str] = None, local_metadata_file: Optional[str] = None, use_web: bool = False) -> pd.DataFrame:
        """
        Combines station codes with metadata and optionally filters by basin.
        
        Args:
            basin_filter: List of basins to filter by.
            local_station_file: Path to local station list CSV (fallback for XML endpoint).
            local_metadata_file: Path to local metadata CSV (fallback for CSV endpoint).
            use_web: If True, force fetch from web (ignoring local defaults).
        """
        logger.info("Combining station codes with metadata (basin_filter=%s)", basin_filter)
        # 1. Get Codes (marker sites)
        df_codes = self.get_station_codes(local_file=local_station_file, use_web=use_web)
        
        # 2. Get Metadata (Bacia, etc.)
        df_meta = self.get_all_stations(local_file=local_metadata_file, use_web=use_web)
        
        # Ensure CÓDIGO is string for merging
        if 'CÓDIGO' in df_meta.columns:
            df_meta['CÓDIGO'] = df_meta['CÓDIGO'].astype(str)
        
        # 3. Merge
        # Notebook: left_on='CÓDIGO', right_on='estacao' (or 'code' which we extracted)
        # In the notebook, 'estacao' column in df_codes was used for merge, but it contained the name/code string.
        # We extracted 'code' which should match 'CÓDIGO'.
        
        # Let's check notebook logic:
        # df_station['codigo'] = df_station['estacao'].str[-9:] ...
        # df_stations = pd.merge(df2, df_station, left_on='CÓDIGO', right_on='codigo', ...)
        
        # So we merge df_meta['CÓDIGO'] with df_codes['code']
        
        merged = pd.merge(
            df_meta, 
            df_codes, 
            left_on='CÓDIGO', 
            right_on='code', 
            how='inner'
        )
        
        logger.info("Merged %d stations", len(merged))

        # Filter by Basin
        if basin_filter:
            merged = merged[merged['BACIA'].isin(basin_filter)]
            logger.info("Filtered to %d stations in basins: %s", len(merged), basin_filter)
            
        return merged

    def update_local_database(self, output_dir: str, s_cover: str = "100290946") -> None:
        """
        Fetches the latest station metadata from the SNIRH website and saves it to the specified directory.
        This allows users to update the local database when the bundled data becomes stale.
        
        Args:
            output_dir: Directory to save the CSV files.
            s_cover: Coverage parameter for the station list.
        """
        logger.info("Updating local database in %s", output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 1. Fetch and save station list (XML/CSV hybrid)
        print("Fetching station list from web...")
        logger.info("Fetching station list from web...")
        # Actually, let's reuse get_station_codes with use_web=True to get the dataframe, then save it.
        df_codes = self.get_station_codes(use_web=True)
        stations_file = os.path.join(output_dir, 'station_list.csv')
        df_codes.to_csv(stations_file, index=False, encoding='ISO-8859-1')
        print(f"Saved station list to {stations_file}")
        logger.info("Saved station list to %s", stations_file)
        
        # 2. Fetch and save metadata (rede_Piezometria)
        print("Fetching station metadata from web...")
        logger.info("Fetching station metadata from web...")
        # We reuse get_all_stations with use_web=True
        df_meta = self.get_all_stations(s_cover=s_cover, use_web=True)
        meta_file = os.path.join(output_dir, 'rede_Piezometria.csv')
        
        df_meta.to_csv(meta_file, index=False, encoding='ISO-8859-1')
        print(f"Saved metadata to {meta_file}")
        logger.info("Saved metadata to %s", meta_file)
        
        print("Update complete. You can now use these files by passing 'local_station_file' and 'local_metadata_file' to get_stations_with_metadata.")

    def get_stations_with_metadata(self, basin_filter: Optional[List[str]] = None, local_station_file: Optional[str] = None, local_metadata_file: Optional[str] = None, use_web: bool = False) -> pd.DataFrame:
        """
        Combines station codes with metadata and optionally filters by basin.
        
        Args:
            basin_filter: List of basins to filter by.
            local_station_file: Path to local station list CSV (fallback for XML endpoint).
            local_metadata_file: Path to local metadata CSV (fallback for CSV endpoint).
            use_web: If True, force fetch from web (ignoring local defaults).
        """
        # 1. Get Codes (marker sites)
        df_codes = self.get_station_codes(local_file=local_station_file, use_web=use_web)
        
        # 2. Get Metadata (Bacia, etc.)
        df_meta = self.get_all_stations(local_file=local_metadata_file, use_web=use_web)
        
        # Ensure CÓDIGO is string for merging
        if 'CÓDIGO' in df_meta.columns:
            df_meta['CÓDIGO'] = df_meta['CÓDIGO'].astype(str)
        
        # 3. Merge
        # Notebook: left_on='CÓDIGO', right_on='estacao' (or 'code' which we extracted)
        # In the notebook, 'estacao' column in df_codes was used for merge, but it contained the name/code string.
        # We extracted 'code' which should match 'CÓDIGO'.
        
        # Let's check notebook logic:
        # df_station['codigo'] = df_station['estacao'].str[-9:] ...
        # df_stations = pd.merge(df2, df_station, left_on='CÓDIGO', right_on='codigo', ...)
        
        # So we merge df_meta['CÓDIGO'] with df_codes['code']
        
        # Ensure code is string for merging
        if 'code' in df_codes.columns:
            df_codes['code'] = df_codes['code'].astype(str)

        merged = pd.merge(
            df_meta, 
            df_codes, 
            left_on='CÓDIGO', 
            right_on='code', 
            how='inner'
        )
        
        logger.info("Merged %d stations", len(merged))

        # Filter by Basin
        if basin_filter:
            merged = merged[merged['BACIA'].isin(basin_filter)]
            logger.info("Filtered to %d stations in basins: %s", len(merged), basin_filter)
            
        return merged

    def update_local_database(self, output_dir: str, s_cover: str = "100290946") -> None:
        """
        Fetches the latest station metadata from the SNIRH website and saves it to the specified directory.
        This allows users to update the local database when the bundled data becomes stale.
        
        Args:
            output_dir: Directory to save the CSV files.
            s_cover: Coverage parameter for the station list.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 1. Fetch and save station list (XML/CSV hybrid)
        print("Fetching station list from web...")
        url_stations = "https://snirh.apambiente.pt/snirh/_dadosbase/site/xml/xml_listaestacoes.php"
        csv_buffer_stations = self.client.fetch_csv(url_stations)
        
        # We save the raw content because our parser expects the weird format
        # Or we could parse and save clean. Let's save clean to make future reads easier.
        # But get_station_codes handles both. Let's save clean.
        
        # Actually, let's reuse get_station_codes with use_web=True to get the dataframe, then save it.
        df_codes = self.get_station_codes(use_web=True)
        stations_file = os.path.join(output_dir, 'station_list.csv')
        df_codes.to_csv(stations_file, index=False, encoding='ISO-8859-1')
        print(f"Saved station list to {stations_file}")
        
        # 2. Fetch and save metadata (rede_Piezometria)
        print("Fetching station metadata from web...")
        # We reuse get_all_stations with use_web=True
        df_meta = self.get_all_stations(s_cover=s_cover, use_web=True)
        meta_file = os.path.join(output_dir, 'rede_Piezometria.csv')
        # We need to save it in a format that get_all_stations expects (skiprows=3)
        # Or we can just save it as a standard CSV and update get_all_stations to handle standard CSVs too.
        # get_all_stations currently expects skiprows=3 for local files too.
        # Let's save it as standard CSV and update get_all_stations to be smarter.
        
        # But wait, get_all_stations implementation:
        # if local_file: df = pd.read_csv(..., skiprows=3, ...)
        # So if we save a clean CSV, we need to make sure get_all_stations can read it.
        
        # Let's write a header to mimic the SNIRH format so we don't break the reader logic
        # Or better, update the reader logic to handle clean CSVs.
        
        df_meta.to_csv(meta_file, index=False, encoding='ISO-8859-1')
        print(f"Saved metadata to {meta_file}")
        
        print("Update complete. You can now use these files by passing 'local_station_file' and 'local_metadata_file' to get_stations_with_metadata.")
