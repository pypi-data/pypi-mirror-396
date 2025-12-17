"""SDK-specific exception hierarchy."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .models import ChatAdsResponse


class ChatAdsSDKError(Exception):
    """Base class for local SDK issues (serialization, transport, etc.)."""


class ChatAdsAPIError(ChatAdsSDKError):
    """Raised for non-2xx responses returned by the ChatAds API."""

    def __init__(
        self,
        status_code: int,
        payload: Optional[Dict[str, Any]] = None,
        response: Optional[ChatAdsResponse] = None,
        headers: Optional[Dict[str, str]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        url: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.payload = payload or {}
        self.response = response
        self.headers = headers or {}
        self.request_body = request_body or {}
        self.url = url
        message = self._build_message()
        super().__init__(message)

    def _build_message(self) -> str:
        if self.response and self.response.error:
            return (
                f"ChatAds API error {self.status_code}: "
                f"{self.response.error.code} - {self.response.error.message}"
            )
        return f"ChatAds API error {self.status_code}"

    @property
    def retry_after(self) -> Optional[str]:
        """Expose Retry-After header when rate limits are hit."""
        for key, value in self.headers.items():
            if key.lower() == "retry-after":
                return value
        return None
