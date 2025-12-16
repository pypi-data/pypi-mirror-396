"""Dataclasses that mirror the ChatAds FastAPI request/response models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

FUNCTION_ITEM_OPTIONAL_FIELDS = (
    "ip",
    "country",
    "message_analysis",
    "fill_priority",
    "min_intent",
    "skip_message_analysis",
)

_CAMELCASE_ALIASES = {
    "messageanalysis": "message_analysis",
    "fillpriority": "fill_priority",
    "minintent": "min_intent",
    "skipmessageanalysis": "skip_message_analysis",
}

FUNCTION_ITEM_FIELD_ALIASES = {
    **{field: field for field in FUNCTION_ITEM_OPTIONAL_FIELDS},
    **_CAMELCASE_ALIASES,
}

_FIELD_TO_PAYLOAD_KEY = {
    "ip": "ip",
    "country": "country",
    "message_analysis": "message_analysis",
    "fill_priority": "fill_priority",
    "min_intent": "min_intent",
    "skip_message_analysis": "skip_message_analysis",
}

RESERVED_PAYLOAD_KEYS = frozenset({"message", *(_FIELD_TO_PAYLOAD_KEY.values())})


@dataclass
class ChatAdsAd:
    """Ad object returned when a product match is found."""
    product: str
    link: str
    message: str
    category: str

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ChatAdsAd"]:
        if not data:
            return None
        return cls(
            product=data.get("product", ""),
            link=data.get("link", ""),
            message=data.get("message", ""),
            category=data.get("category", ""),
        )


@dataclass
class ChatAdsData:
    """Data object containing match results and optional ad."""
    matched: bool
    filled: bool = False
    ad: Optional[ChatAdsAd] = None
    keyword: Optional[str] = None
    reason: Optional[str] = None
    intent_score: Optional[float] = None
    intent_level: Optional[str] = None
    min_intent_required: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ChatAdsData"]:
        if not data:
            return None
        return cls(
            matched=bool(data.get("matched", False)),
            filled=bool(data.get("filled", False)),
            ad=ChatAdsAd.from_dict(data.get("ad")),
            keyword=data.get("keyword"),
            reason=data.get("reason"),
            intent_score=data.get("intent_score"),
            intent_level=data.get("intent_level"),
            min_intent_required=data.get("min_intent_required"),
        )


@dataclass
class ChatAdsError:
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ChatAdsError"]:
        if not data:
            return None
        return cls(
            code=data.get("code", "UNKNOWN"),
            message=data.get("message", ""),
            details=data.get("details") or {},
        )


@dataclass
class UsageInfo:
    """Usage information returned in API responses."""
    monthly_requests: int
    is_free_tier: bool
    free_tier_limit: Optional[int] = None
    free_tier_remaining: Optional[int] = None
    daily_requests: Optional[int] = None
    daily_limit: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["UsageInfo"]:
        if not data:
            return None
        return cls(
            monthly_requests=int(data.get("monthly_requests") or 0),
            is_free_tier=bool(data.get("is_free_tier", False)),
            free_tier_limit=_maybe_int(data.get("free_tier_limit")),
            free_tier_remaining=_maybe_int(data.get("free_tier_remaining")),
            daily_requests=_maybe_int(data.get("daily_requests")),
            daily_limit=_maybe_int(data.get("daily_limit")),
        )


@dataclass
class ChatAdsMeta:
    """Metadata about the API request and response."""
    request_id: str
    country: Optional[str] = None
    language: Optional[str] = None
    extraction_method: Optional[str] = None
    message_analysis_used: Optional[str] = None
    fill_priority_used: Optional[str] = None
    min_intent_used: Optional[str] = None
    usage: Optional[UsageInfo] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ChatAdsMeta":
        data = data or {}
        return cls(
            request_id=data.get("request_id", ""),
            country=data.get("country"),
            language=data.get("language"),
            extraction_method=data.get("extraction_method"),
            message_analysis_used=data.get("message_analysis_used"),
            fill_priority_used=data.get("fill_priority_used"),
            min_intent_used=data.get("min_intent_used"),
            usage=UsageInfo.from_dict(data.get("usage")),
            raw=data,
        )


@dataclass
class ChatAdsResponse:
    success: bool
    meta: ChatAdsMeta
    data: Optional[ChatAdsData] = None
    error: Optional[ChatAdsError] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatAdsResponse":
        data = data or {}
        return cls(
            success=bool(data.get("success", False)),
            data=ChatAdsData.from_dict(data.get("data")),
            error=ChatAdsError.from_dict(data.get("error")),
            meta=ChatAdsMeta.from_dict(data.get("meta")),
            raw=data,
        )


@dataclass
class FunctionItemPayload:
    """Subset of the server's FunctionItem pydantic model."""

    message: str
    ip: Optional[str] = None
    country: Optional[str] = None
    message_analysis: Optional[str] = None
    fill_priority: Optional[str] = None
    min_intent: Optional[str] = None
    skip_message_analysis: Optional[bool] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        payload = {"message": self.message}
        for field_name, payload_key in _FIELD_TO_PAYLOAD_KEY.items():
            value = getattr(self, field_name)
            if value is not None:
                payload[payload_key] = value

        conflicts = RESERVED_PAYLOAD_KEYS.intersection(self.extra_fields.keys())
        if conflicts:
            conflict_list = ", ".join(sorted(conflicts))
            raise ValueError(
                f"extra_fields contains reserved keys that would override core payload data: {conflict_list}"
            )
        payload.update(self.extra_fields)
        return payload


def _maybe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
