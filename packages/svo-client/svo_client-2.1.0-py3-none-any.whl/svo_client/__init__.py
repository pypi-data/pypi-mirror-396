"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

SVO Client - Async client for SVO semantic chunker microservice.
"""

from svo_client.chunker_client import ChunkerClient
from svo_client.errors import (
    SVOConnectionError,
    SVOEmbeddingError,
    SVOHTTPError,
    SVOJSONRPCError,
    SVOServerError,
    SVOTimeoutError,
)

__all__ = [
    "ChunkerClient",
    "SVOServerError",
    "SVOJSONRPCError",
    "SVOHTTPError",
    "SVOConnectionError",
    "SVOTimeoutError",
    "SVOEmbeddingError",
]

__version__ = "2.1.0"
