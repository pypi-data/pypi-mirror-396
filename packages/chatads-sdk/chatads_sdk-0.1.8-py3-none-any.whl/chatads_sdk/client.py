"""HTTP clients for interacting with the ChatAds API."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Iterable, Optional, Set
from urllib.parse import urlparse

import httpx

from .exceptions import ChatAdsAPIError, ChatAdsSDKError
from .models import (
    ChatAdsResponse,
    FunctionItemPayload,
    FUNCTION_ITEM_FIELD_ALIASES,
    FUNCTION_ITEM_OPTIONAL_FIELDS,
)

_DEFAULT_ENDPOINT = "/v1/chatads/messages"
_DEFAULT_RETRY_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
_FUNCTION_ITEM_OPTIONAL_FIELDS = set(FUNCTION_ITEM_OPTIONAL_FIELDS)
_FIELD_ALIAS_LOOKUP = {alias.lower(): field for alias, field in FUNCTION_ITEM_FIELD_ALIASES.items()}


class ChatAdsClient:
    """Synchronous ChatAds API client."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        *,
        endpoint: str = _DEFAULT_ENDPOINT,
        timeout: float = 10.0,
        http_client: Optional[httpx.Client] = None,
        raise_on_failure: bool = False,
        max_retries: int = 0,
        retry_backoff_factor: float = 0.5,
        retry_statuses: Optional[Iterable[int]] = None,
        logger: Optional[logging.Logger] = None,
        debug: bool = False,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self._api_key = api_key
        self._base_url = _validate_base_url(base_url)
        self._endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        self._timeout = timeout
        self._client = http_client or httpx.Client(timeout=timeout)
        self._owns_client = http_client is None
        self._raise_on_failure = raise_on_failure
        self._max_retries = max(0, int(max_retries))
        self._retry_backoff_factor = max(0.0, float(retry_backoff_factor))
        self._retry_statuses: Set[int] = (
            set(retry_statuses) if retry_statuses is not None else set(_DEFAULT_RETRY_STATUSES)
        )
        self._logger = logger or logging.getLogger("chatads_sdk")
        self._debug = debug

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "ChatAdsClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()

    def analyze(
        self,
        payload: FunctionItemPayload,
        *,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ChatAdsResponse:
        """Send a FunctionItem payload to the ChatAds endpoint."""
        body = payload.to_payload()
        return self._post(body, timeout=timeout, headers=headers)

    def analyze_message(
        self,
        message: str,
        *,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        **extra_fields: Any,
    ) -> ChatAdsResponse:
        """
        Convenience wrapper taking only the message plus optional FunctionItem fields.
        """
        payload = _build_payload_from_kwargs(message, extra_fields)
        return self.analyze(payload, timeout=timeout, headers=headers)

    def _post(
        self,
        body: Dict[str, Any],
        *,
        timeout: Optional[float],
        headers: Optional[Dict[str, str]],
    ) -> ChatAdsResponse:
        request_headers = {"x-api-key": self._api_key, **(headers or {})}
        url = f"{self._base_url}{self._endpoint}"
        attempt = 0
        while True:
            try:
                self._log_request(url, request_headers, body)
                response = self._client.post(
                    url,
                    json=body,
                    headers=request_headers,
                    timeout=timeout or self._timeout,
                )
            except httpx.RequestError as exc:
                if attempt >= self._max_retries:
                    raise ChatAdsSDKError(f"Transport error while calling ChatAds: {exc}") from exc
                _sleep_sync(
                    _compute_retry_delay(attempt, self._retry_backoff_factor, None)
                )
                attempt += 1
                continue

            parsed = _parse_response(response)
            self._log_response(response, parsed)
            is_error = response.is_error or (self._raise_on_failure and not parsed.success)
            if not is_error:
                return parsed

            api_error = ChatAdsAPIError(
                status_code=response.status_code,
                payload=parsed.raw,
                response=parsed,
                headers=dict(response.headers),
                request_body=body,
                url=url,
            )
            if attempt < self._max_retries and self._should_retry_status(response.status_code):
                _sleep_sync(
                    _compute_retry_delay(attempt, self._retry_backoff_factor, api_error.retry_after)
                )
                attempt += 1
                continue
            raise api_error

    def _should_retry_status(self, status_code: int) -> bool:
        return status_code in self._retry_statuses

    def _log_request(self, url: str, headers: Dict[str, str], body: Dict[str, Any]) -> None:
        if not self._debug:
            return
        safe_headers = {k: v for k, v in headers.items() if k.lower() != "x-api-key"}
        self._logger.info("ChatAds request -> %s", url)
        self._logger.info("Headers: %s", safe_headers)
        self._logger.info("Body (sanitized): %s", json.dumps(_sanitize_payload(body), indent=2))

    def _log_response(self, response: httpx.Response, parsed: ChatAdsResponse) -> None:
        if not self._debug:
            return
        self._logger.info(
            "ChatAds response <- %s %s (status=%s)",
            response.request.method if response.request else "POST",
            response.request.url if response.request else "<unknown>",
            response.status_code,
        )
        self._logger.info("Payload: %s", json.dumps(parsed.raw, indent=2))


class AsyncChatAdsClient:
    """Asynchronous version backed by httpx.AsyncClient."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        *,
        endpoint: str = _DEFAULT_ENDPOINT,
        timeout: float = 10.0,
        http_client: Optional[httpx.AsyncClient] = None,
        raise_on_failure: bool = False,
        max_retries: int = 0,
        retry_backoff_factor: float = 0.5,
        retry_statuses: Optional[Iterable[int]] = None,
        logger: Optional[logging.Logger] = None,
        debug: bool = False,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")

        self._api_key = api_key
        self._base_url = _validate_base_url(base_url)
        self._endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        self._timeout = timeout
        self._client = http_client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = http_client is None
        self._raise_on_failure = raise_on_failure
        self._max_retries = max(0, int(max_retries))
        self._retry_backoff_factor = max(0.0, float(retry_backoff_factor))
        self._retry_statuses: Set[int] = (
            set(retry_statuses) if retry_statuses is not None else set(_DEFAULT_RETRY_STATUSES)
        )
        self._logger = logger or logging.getLogger("chatads_sdk")
        self._debug = debug

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncChatAdsClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.aclose()

    async def analyze(
        self,
        payload: FunctionItemPayload,
        *,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ChatAdsResponse:
        body = payload.to_payload()
        return await self._post(body, timeout=timeout, headers=headers)

    async def analyze_message(
        self,
        message: str,
        *,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
        **extra_fields: Any,
    ) -> ChatAdsResponse:
        payload = _build_payload_from_kwargs(message, extra_fields)
        return await self.analyze(payload, timeout=timeout, headers=headers)

    async def _post(
        self,
        body: Dict[str, Any],
        *,
        timeout: Optional[float],
        headers: Optional[Dict[str, str]],
    ) -> ChatAdsResponse:
        request_headers = {"x-api-key": self._api_key, **(headers or {})}
        url = f"{self._base_url}{self._endpoint}"
        attempt = 0
        while True:
            try:
                self._log_request(url, request_headers, body)
                response = await self._client.post(
                    url,
                    json=body,
                    headers=request_headers,
                    timeout=timeout or self._timeout,
                )
            except httpx.RequestError as exc:
                if attempt >= self._max_retries:
                    raise ChatAdsSDKError(f"Transport error while calling ChatAds: {exc}") from exc
                await _sleep_async(
                    _compute_retry_delay(attempt, self._retry_backoff_factor, None)
                )
                attempt += 1
                continue

            parsed = _parse_response(response)
            self._log_response(response, parsed)
            is_error = response.is_error or (self._raise_on_failure and not parsed.success)
            if not is_error:
                return parsed

            api_error = ChatAdsAPIError(
                status_code=response.status_code,
                payload=parsed.raw,
                response=parsed,
                headers=dict(response.headers),
                request_body=body,
                url=url,
            )
            if attempt < self._max_retries and self._should_retry_status(response.status_code):
                await _sleep_async(
                    _compute_retry_delay(attempt, self._retry_backoff_factor, api_error.retry_after)
                )
                attempt += 1
                continue
            raise api_error

    def _should_retry_status(self, status_code: int) -> bool:
        return status_code in self._retry_statuses

    def _log_request(self, url: str, headers: Dict[str, str], body: Dict[str, Any]) -> None:
        if not self._debug:
            return
        safe_headers = {k: v for k, v in headers.items() if k.lower() != "x-api-key"}
        self._logger.info("ChatAds request -> %s", url)
        self._logger.info("Headers: %s", safe_headers)
        self._logger.info("Body (sanitized): %s", json.dumps(_sanitize_payload(body), indent=2))

    def _log_response(self, response: httpx.Response, parsed: ChatAdsResponse) -> None:
        if not self._debug:
            return
        self._logger.info(
            "ChatAds response <- %s %s (status=%s)",
            response.request.method if response.request else "POST",
            response.request.url if response.request else "<unknown>",
            response.status_code,
        )
        self._logger.info("Payload: %s", json.dumps(parsed.raw, indent=2))


def _parse_response(response: httpx.Response) -> ChatAdsResponse:
    try:
        payload = response.json()
    except ValueError as exc:
        raise ChatAdsSDKError("ChatAds returned a non-JSON response") from exc
    return ChatAdsResponse.from_dict(payload)


def _build_payload_from_kwargs(message: str, kwargs: Dict[str, Any]) -> FunctionItemPayload:
    known: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}
    for key, value in kwargs.items():
        normalized = _normalize_field_name(key)
        if normalized:
            known[normalized] = value
        else:
            extra[key] = value
    return FunctionItemPayload(message=message, extra_fields=extra, **known)


def _normalize_field_name(field: str) -> Optional[str]:
    if field in _FUNCTION_ITEM_OPTIONAL_FIELDS:
        return field
    return _FIELD_ALIAS_LOOKUP.get(field.lower())


def _compute_retry_delay(
    attempt: int,
    backoff_factor: float,
    retry_after_header: Optional[str],
) -> float:
    header_delay = _parse_retry_after(retry_after_header)
    if header_delay is not None:
        return header_delay
    if backoff_factor <= 0:
        return 0.0
    return backoff_factor * (2 ** attempt)


def _parse_retry_after(header_value: Optional[str]) -> Optional[float]:
    if header_value is None:
        return None
    header_value = header_value.strip()
    if not header_value:
        return None
    try:
        return max(0.0, float(header_value))
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(header_value)
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        seconds = (dt - datetime.now(timezone.utc)).total_seconds()
        return max(0.0, seconds)
    except (TypeError, ValueError, OverflowError):
        return None


def _sleep_sync(delay: float) -> None:
    if delay > 0:
        time.sleep(delay)


async def _sleep_async(delay: float) -> None:
    if delay > 0:
        await asyncio.sleep(delay)


def _validate_base_url(raw: str) -> str:
    cleaned = (raw or "").rstrip("/")
    if not cleaned:
        raise ValueError("base_url is required")
    parsed = urlparse(cleaned)
    if parsed.scheme.lower() != "https":
        raise ValueError("base_url must start with https://")
    if not parsed.netloc:
        raise ValueError("base_url must include a hostname")
    return cleaned


def _sanitize_payload(body: Dict[str, Any]) -> Dict[str, str]:
    return {key: "<redacted>" for key in body.keys()}
