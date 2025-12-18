import logging

# Add NullHandler to prevent "No handler found" warnings
logging.getLogger(__name__).addHandler(logging.NullHandler())

from .client import SnirhClient
from .stations import StationFetcher
from .data import DataFetcher
from .constants import Parameters
from .exceptions import SnirhError, SnirhNetworkError, SnirhParsingError

class Snirh:
    """
    Main entry point for the SNIRH package.
    """
    def __init__(self, network: str = "piezometria", verbose: bool = False):
        if verbose:
            logger = logging.getLogger(__name__)
            # Only add handler if one doesn't exist to avoid duplicates
            if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)

        self.client = SnirhClient()
        self.stations = StationFetcher(self.client, network=network)
        self.data = DataFetcher(self.client)

__all__ = [
    'Snirh',
    'SnirhClient',
    'StationFetcher',
    'DataFetcher',
    'Parameters',
    'SnirhError',
    'SnirhNetworkError',
    'SnirhParsingError'
]
