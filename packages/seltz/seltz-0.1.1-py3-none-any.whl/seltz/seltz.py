import os

from .client import SeltzClient
from .exceptions import SeltzConfigurationError
from .services import SearchResponse
from .services.search_service import SearchService


class Seltz:
    """Main Seltz SDK client for interacting with the Seltz API."""

    _ENDPOINT: str = "api.seltz.ai"

    def __init__(
        self,
        api_key: str | None = os.environ.get("SELTZ_API_KEY"),
        endpoint: str = _ENDPOINT,
        insecure: bool = False,
    ):
        """Initialize the Seltz client.

        Args:
            api_key: API key for authentication. If None, will try to read from SELTZ_API_KEY environment variable
            endpoint: The API endpoint to connect to (default: api.seltz.ai)
            insecure: Whether to use insecure connection (default: False)

        Returns:
            Seltz: A new Seltz client instance

        Raises:
            SeltzConfigurationError: If no API key is provided
        """
        if api_key is None:
            raise SeltzConfigurationError("No API key provided")
        self._client = SeltzClient(endpoint=endpoint, api_key=api_key, insecure=insecure)
        self._search = SearchService(self._client.channel, self._client.api_key)

    def search(self, text: str, max_documents: int = 10) -> SearchResponse:
        """Perform a search query.

        Args:
            text: The search query text
            max_documents: Maximum number of documents to return (default: 10)

        Returns:
            SearchResponse: The search results
        """
        return self._search.search(text, max_documents=max_documents)
