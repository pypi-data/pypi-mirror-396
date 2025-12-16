"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Shared exception types for SVO client.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class SVOServerError(Exception):
    """Raised when the SVO server returns an application-level error."""

    def __init__(
        self,
        code: str,
        message: str,
        chunk_error: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.chunk_error = chunk_error or {}
        super().__init__(f"SVO server error [{code}]: {message}")


class SVOJSONRPCError(Exception):
    """Raised when the SVO server returns a JSON-RPC error response."""

    def __init__(
        self,
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(f"JSON-RPC error [{code}]: {message}")


class SVOHTTPError(Exception):
    """Raised when the SVO server returns an HTTP error or invalid response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_text: str = "",
    ):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        super().__init__(f"HTTP error [{status_code}]: {message}")


class SVOConnectionError(Exception):
    """Raised when there are network/connection issues with the SVO server."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class SVOTimeoutError(Exception):
    """Raised when request to SVO server times out."""

    def __init__(
        self,
        message: str,
        timeout_value: Optional[float] = None,
    ):
        self.message = message
        self.timeout_value = timeout_value
        super().__init__(f"Timeout error: {message}")


class SVOEmbeddingError(Exception):
    """Raised when embedding service returns an error or invalid payload."""
