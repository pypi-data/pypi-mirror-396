import grpc

from ..exceptions import (
    SeltzAPIError,
    SeltzAuthenticationError,
    SeltzConnectionError,
    SeltzRateLimitError,
    SeltzTimeoutError,
)
from . import Includes, SearchRequest, SearchResponse, SeltzServiceStub


class SearchService:
    """Service for performing search operations via gRPC."""

    def __init__(self, channel: grpc.Channel, api_key: str | None):
        """Initialize the search service.

        Args:
            channel: gRPC channel for communication
            api_key: API key for authentication
        """
        self._stub = SeltzServiceStub(channel)
        self._api_key = api_key

    def search(self, query: str, max_documents: int = 10) -> SearchResponse:
        """Perform a search query.

        Args:
            query: The search query string
            max_documents: Maximum number of documents to return (default: 10)

        Returns:
            SearchResponse containing the search results

        Raises:
            grpc.RpcError: If the gRPC call fails
        """
        includes = Includes(max_documents=max_documents)
        req = SearchRequest(query=query, includes=includes)

        metadata = []
        if self._api_key:
            metadata.append(("authorization", f"Bearer {self._api_key}"))

        try:
            return self._stub.Search(req, metadata=metadata, timeout=30)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                raise SeltzAuthenticationError(
                    f"Authentication failed: {e.details()}"
                ) from e
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise SeltzConnectionError(f"Connection failed: {e.details()}") from e
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise SeltzTimeoutError(f"Request timed out: {e.details()}") from e
            elif e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
                raise SeltzRateLimitError(f"Rate limit exceeded: {e.details()}") from e
            else:
                raise SeltzAPIError(
                    f"API error: {e.details()}", e.code(), e.details()
                ) from e
