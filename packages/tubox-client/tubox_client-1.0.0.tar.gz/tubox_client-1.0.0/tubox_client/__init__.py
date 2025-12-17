"""Tubox Client - Python client library for Tubox database."""

__version__ = "1.0.0"
__author__ = "Tubox"
__license__ = "MIT"

# Use the new API-based client
from tubox_client.api_client import (
    TuboxClient,
    SyncSession,
    SyncTransaction,
)
from tubox_client.exceptions import (
    TuboxException,
    AuthenticationError,
    UnauthorizedError,
    QuotaExceededError,
    RateLimitExceededError,
    NotFoundError,
)
from tubox_client.config import ClientConfig

__all__ = [
    "TuboxClient",
    "SyncSession",
    "SyncTransaction",
    "TuboxException",
    "AuthenticationError",
    "UnauthorizedError",
    "QuotaExceededError",
    "RateLimitExceededError",
    "NotFoundError",
    "ClientConfig",
]
