"""Service layer with centralized protobuf imports for API version management."""

# Centralized protobuf imports - update these when API version changes
from seltz_public_api.proto.v1.seltz_pb2 import (
    Document,
    Includes,
    SearchRequest,
    SearchResponse,
)
from seltz_public_api.proto.v1.seltz_pb2_grpc import SeltzServiceStub

__all__ = [
    "SeltzServiceStub",
    "SearchRequest",
    "SearchResponse",
    "Includes",
    "Document",
]
