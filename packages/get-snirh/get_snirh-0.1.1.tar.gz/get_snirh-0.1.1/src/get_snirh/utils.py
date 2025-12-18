import pandas as pd

def clean_station_name(series: pd.Series) -> pd.Series:
    """
    Cleans the station name column.
    Removes HTML entities and special characters.
    """
    s = series.copy()
    s = s.str.replace('&amp;#9632; ', '', regex=False)
    s = s.str.replace('■ ', '', regex=False)
    # Handle mojibake from UTF-8 read as ISO-8859-1
    s = s.str.replace('â\x96\xa0 ', '', regex=False)
    s = s.str.replace('â\x80\x93 ', '', regex=False) # Another common one
    s = s.str.replace('?', '', regex=False)
    s = s.str.strip()
    return s

def extract_station_code(series: pd.Series) -> pd.Series:
    """
    Extracts the station code from the station name string.
    If format is "Name (Code)", extracts Code.
    Otherwise returns the string as is (stripped).
    """
    s = series.str.strip()
    # Try to extract content inside the last set of parentheses
    extracted = s.str.extract(r'\(([^)]+)\)$', expand=False)
    # Use extracted code if found, otherwise use the original string
    return extracted.fillna(s)
