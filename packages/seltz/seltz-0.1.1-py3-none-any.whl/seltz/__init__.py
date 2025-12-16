"""Seltz Python SDK for interacting with the Seltz API."""

from .exceptions import (
    SeltzAPIError,
    SeltzAuthenticationError,
    SeltzConfigurationError,
    SeltzConnectionError,
    SeltzError,
    SeltzRateLimitError,
    SeltzTimeoutError,
)
from .seltz import Seltz

__all__ = [
    "Seltz",
    "SeltzError",
    "SeltzConfigurationError",
    "SeltzAuthenticationError",
    "SeltzConnectionError",
    "SeltzAPIError",
    "SeltzTimeoutError",
    "SeltzRateLimitError",
]
