import requests
import io
import logging
import threading
from typing import Optional, Dict, Any
from .constants import SnirhHeaders
from .exceptions import SnirhNetworkError

logger = logging.getLogger(__name__)

class SnirhClient:
    """
    Client for interacting with SNIRH API.
    Handles session management and encoding.
    """

    def __init__(self, headers: Optional[Dict[str, str]] = None):
        self._headers = headers or SnirhHeaders.DEFAULT
        self._local = threading.local()
        logger.debug("SnirhClient initialized with headers: %s", self._headers)

    @property
    def session(self) -> requests.Session:
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session()
            self._local.session.headers.update(self._headers)
        return self._local.session

    def fetch_csv(self, url: str) -> io.StringIO:
        """
        Fetches CSV data from a URL and returns a StringIO object.
        Handles ISO-8859-1 encoding.
        
        Args:
            url: The URL to fetch.
            
        Returns:
            io.StringIO: The content of the response.
            
        Raises:
            SnirhNetworkError: If the request fails.
        """
        logger.info("Fetching CSV from URL: %s", url)
        try:
            response = self.session.get(url, allow_redirects=True)
            response.raise_for_status()
            
            # SNIRH uses ISO-8859-1 encoding
            content = response.content.decode('ISO-8859-1')
            logger.debug("Successfully fetched %d bytes", len(content))
            return io.StringIO(content)
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch data from %s: %s", url, str(e))
            raise SnirhNetworkError(f"Failed to fetch data from {url}: {str(e)}") from e
