from __future__ import annotations

from typing import Any, Optional


class SkribbleError(Exception):
    """Base exception for all Skribble SDK errors."""


class SkribbleAuthError(SkribbleError):
    """Authentication / authorization related errors."""


class SkribbleHTTPError(SkribbleError):
    """
    Raised when the Skribble API returns a non-2xx HTTP status code.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        response_json: Optional[Any] = None,
        response_text: Optional[str] = None,
    ) -> None:
        super().__init__(f"Skribble API error {status_code}: {message}")
        self.status_code = status_code
        self.response_json = response_json
        self.response_text = response_text
