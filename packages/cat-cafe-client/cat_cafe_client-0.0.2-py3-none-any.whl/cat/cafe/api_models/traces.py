"""API request/response models for trace endpoints (SDK/shared surface)."""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_serializer

from cat.cafe.annotation import AnnotationSummary


#######################################################
# Span Models
#######################################################


class SpanEventAttribute(BaseModel):
    """An attribute for a span event."""

    key: str
    value: Any


class SpanEvent(BaseModel):
    """An event within a span."""

    timeUnixNano: str
    name: str
    attributes: Dict[str, Any] = Field(default_factory=dict)


class SpanStatus(BaseModel):
    """Status information for a span."""

    code: str  # Status code can be a string like 'STATUS_CODE_OK' or numeric string
    message: str = ""

    model_config = {
        "populate_by_name": True,
        # Allow string representation of integers
        "coerce_numbers_to_str": True,
    }


class Span(BaseModel):
    """Model for a span within a trace."""

    spanID: str
    traceID: str
    parentSpanID: str | None = None
    name: str
    serviceName: str | None = None
    kind: int | str | None = None
    startTimeUnixNano: str
    endTimeUnixNano: str
    durationMs: float | None = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    events: List[SpanEvent] | None = None
    status: SpanStatus | None = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


#######################################################
# API Models - Format exposed through FastAPI
#######################################################


class Trace(BaseModel):
    """Model for a trace returned to API clients."""

    trace_id: Annotated[str, Field(alias="traceID")]
    root_service_name: Annotated[str | None, Field(alias="rootServiceName")] = None
    root_trace_name: Annotated[str | None, Field(alias="rootTraceName")] = None
    start_time_unix_nano: Annotated[str | None, Field(alias="startTimeUnixNano")] = None
    duration_ms: Annotated[int | None, Field(alias="durationMs")] = None
    # Spans are not always included in search results
    spans: List[Span] | None = None
    # Annotation summary
    annotation_summary: Optional["AnnotationSummary"] = Field(None, alias="annotationSummary")
    # Raw backend data (previously tempo_data)
    backend_data: Optional[Dict[str, Any]] = Field(None, alias="backendData")
    # Flag to control whether to include raw data
    include_raw_data: bool = Field(False, exclude=True)  # This won't appear in JSON output

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "alias_generator": None,  # Disable automatic aliasing
        "from_attributes": True,  # Enable attribute-based deserialization
    }

    @field_serializer("backend_data")
    def serialize_backend_data(self, backend_data: Optional[Dict[str, Any]], _info):
        # By default, exclude the raw backend data to keep responses small
        # Include it only when explicitly requested
        if self.include_raw_data and backend_data is not None:
            return backend_data
        return None


class TraceResponse(BaseModel):
    """Model for trace query response with pagination support."""

    traces: Annotated[List[Trace], Field(default_factory=list)]
    next_cursor: str | None = None
    has_more: bool = False
    errors: List[str] | None = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "from_attributes": True,  # Enable attribute-based deserialization
    }


#######################################################
# ToolCall wrapper
#######################################################


class ToolCall(BaseModel):
    """Tool/function call information with compatibility helpers."""

    id: str
    name: str
    arguments: Optional[Dict[str, Any]] = None
    type: str = "function"

    @property
    def args(self) -> Optional[Dict[str, Any]]:
        """Backwards-compatible accessor for function arguments."""
        return self.arguments

    @args.setter
    def args(self, value: Optional[Dict[str, Any]]) -> None:
        """Allow setting args while keeping underlying arguments field."""
        self.arguments = value

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCall":
        """Create from dict supporting both args and arguments keys."""
        arguments = data.get("arguments", data.get("args"))
        payload = {**data, "arguments": arguments}
        return cls(**payload)


# Resolve forward refs for runtime usage
Trace.model_rebuild()
TraceResponse.model_rebuild()

__all__ = [
    "Span",
    "SpanEvent",
    "SpanEventAttribute",
    "SpanStatus",
    "Trace",
    "TraceResponse",
    "ToolCall",
]
