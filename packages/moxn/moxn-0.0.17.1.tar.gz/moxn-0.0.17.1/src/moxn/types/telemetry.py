from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from itertools import count
from typing import TYPE_CHECKING, Any, Generic, Literal, Optional, Protocol, TypeVar
from uuid import UUID, uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from moxn.types.base import MessageBase, RenderableModel
from moxn.types.content import Provider
from moxn.types.dto import MessageDTO
from moxn.types.response import ParsedResponseModelBase

# Import at runtime (not TYPE_CHECKING) since these are used in LLMEventModelBase fields
# Import will be deferred via string annotations to avoid circular dependency
if TYPE_CHECKING:
    from moxn.types.request_config import RequestConfig, SchemaDefinition


# Core Domain Types
class ResponseType(str, Enum):
    """Classification of LLM response types for observability and UI rendering."""

    TEXT = "text"  # Pure text completion, no tools/structure
    TOOL_CALLS = "tool_calls"  # One or more tool calls, no text
    TEXT_WITH_TOOLS = "text_with_tools"  # Text + tool calls mixed
    STRUCTURED = "structured"  # Structured generation (JSON schema output)
    STRUCTURED_WITH_TOOLS = "structured_with_tools"  # Structured + tools
    # Thinking-aware types (extended thinking / reasoning models)
    THINKING = "thinking"  # Pure thinking output (Claude extended thinking)
    TEXT_WITH_THINKING = "text_with_thinking"  # Text + thinking blocks
    THINKING_WITH_TOOLS = "thinking_with_tools"  # Thinking + tool calls


# Event type constants (simple strings, not enums)
# These are used as the primary event classification
EVENT_TYPE_SPAN_START = "span_start"
EVENT_TYPE_SPAN_END = "span_end"
EVENT_TYPE_SPAN_ERROR = "span_error"
EVENT_TYPE_LLM_CALL = "llm_call"
EVENT_TYPE_TOOL_CALL = "tool_call"
EVENT_TYPE_VALIDATION = "validation"
EVENT_TYPE_CUSTOM = "custom"


# =============================================================================
# W3C Trace Context Types (OTEL Compatible)
# =============================================================================


@dataclass(frozen=True)
class TraceContext:
    """W3C Trace Context - immutable identity for a trace.

    This represents the trace identity that flows across service boundaries.
    The trace_id is a 128-bit identifier encoded as 32 lowercase hex characters.
    """

    trace_id: str  # 32 hex chars (128-bit)
    trace_flags: int = 0x01  # 0x01 = sampled
    trace_state: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate trace_id format."""
        if len(self.trace_id) != 32:
            raise ValueError(f"trace_id must be 32 hex chars, got {len(self.trace_id)}")
        if not all(c in "0123456789abcdef" for c in self.trace_id.lower()):
            raise ValueError("trace_id must be lowercase hex characters")

    @classmethod
    def generate(cls) -> TraceContext:
        """Generate a new random trace context."""
        return cls(trace_id=secrets.token_hex(16))

    @classmethod
    def from_traceparent(
        cls, traceparent: str, tracestate: str | None = None
    ) -> TraceContext:
        """Parse W3C traceparent header.

        Format: {version}-{trace_id}-{parent_span_id}-{flags}
        Example: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
        """
        parts = traceparent.split("-")
        if len(parts) != 4:
            raise ValueError(f"Invalid traceparent format: {traceparent}")
        version, trace_id, _span_id, flags = parts
        if version != "00":
            raise ValueError(f"Unsupported traceparent version: {version}")
        if len(trace_id) != 32:
            raise ValueError(f"Invalid trace_id length: {len(trace_id)}")

        state: dict[str, str] = {}
        if tracestate:
            for item in tracestate.split(","):
                if "=" in item:
                    k, v = item.strip().split("=", 1)
                    state[k] = v

        return cls(
            trace_id=trace_id.lower(),
            trace_flags=int(flags, 16),
            trace_state=state,
        )

    @property
    def is_sampled(self) -> bool:
        """Check if this trace should be recorded."""
        return bool(self.trace_flags & 0x01)

    def with_state(self, key: str, value: str) -> TraceContext:
        """Return new context with added state."""
        new_state = dict(self.trace_state)
        new_state[key] = value
        return TraceContext(self.trace_id, self.trace_flags, new_state)


@dataclass(frozen=True)
class SpanContext:
    """Immutable reference to a span, suitable for propagation.

    Contains the trace identity plus a specific span_id.
    The span_id is a 64-bit identifier encoded as 16 lowercase hex characters.
    """

    trace_context: TraceContext
    span_id: str  # 16 hex chars (64-bit)
    is_remote: bool = False  # True if received from external service

    def __post_init__(self) -> None:
        """Validate span_id format."""
        if len(self.span_id) != 16:
            raise ValueError(f"span_id must be 16 hex chars, got {len(self.span_id)}")
        if not all(c in "0123456789abcdef" for c in self.span_id.lower()):
            raise ValueError("span_id must be lowercase hex characters")

    @classmethod
    def create_root(cls, trace_context: TraceContext | None = None) -> SpanContext:
        """Create a root span context (start of a new trace or continuation)."""
        return cls(
            trace_context=trace_context or TraceContext.generate(),
            span_id=secrets.token_hex(8),
            is_remote=False,
        )

    @classmethod
    def create_child(cls, parent: SpanContext) -> SpanContext:
        """Create a child span context inheriting the trace."""
        return cls(
            trace_context=parent.trace_context,
            span_id=secrets.token_hex(8),
            is_remote=False,
        )

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> SpanContext | None:
        """Extract from W3C headers. Returns None if not present."""
        traceparent = headers.get("traceparent") or headers.get("Traceparent")
        if not traceparent:
            return None

        tracestate = headers.get("tracestate") or headers.get("Tracestate")

        try:
            trace_ctx = TraceContext.from_traceparent(traceparent, tracestate)
            # Extract span_id from traceparent (position 2)
            parent_span_id = traceparent.split("-")[2]
            return cls(
                trace_context=trace_ctx,
                span_id=parent_span_id.lower(),
                is_remote=True,
            )
        except ValueError:
            return None

    @property
    def trace_id(self) -> str:
        """Convenience accessor for trace_id."""
        return self.trace_context.trace_id

    def to_traceparent(self) -> str:
        """Generate W3C traceparent header value."""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_context.trace_flags:02x}"

    def to_tracestate(self) -> str:
        """Generate W3C tracestate header value."""
        return ",".join(f"{k}={v}" for k, v in self.trace_context.trace_state.items())

    def to_headers(self) -> dict[str, str]:
        """Generate W3C headers for propagation."""
        headers = {"traceparent": self.to_traceparent()}
        if self.trace_context.trace_state:
            headers["tracestate"] = self.to_tracestate()
        return headers


class SpanStatus(str, Enum):
    """Span completion status."""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanEvent:
    """An event occurring during span execution."""

    name: str
    timestamp: datetime
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Link to another span (for async/batch/fan-out patterns)."""

    context: SpanContext
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Mutable span for tracking execution within a trace.

    Unlike SpanContext, this is NOT propagatable - it represents
    active execution state that only exists within one service.
    """

    context: SpanContext
    name: str
    parent_span_id: str | None  # 16 hex chars or None
    start_time: datetime

    # Moxn-specific context (Entity IDs stay as UUID)
    prompt_id: UUID
    prompt_name: str
    task_id: UUID
    commit_id: UUID | None = None
    branch_id: UUID | None = None

    # Mutable state
    end_time: datetime | None = None
    status: SpanStatus = SpanStatus.UNSET
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)
    links: list[SpanLink] = field(default_factory=list)
    _sequence: count = field(default_factory=lambda: count(1))

    @property
    def span_id(self) -> str:
        """This span's ID (16 hex chars)."""
        return self.context.span_id

    @property
    def trace_id(self) -> str:
        """The trace ID (32 hex chars)."""
        return self.context.trace_id

    @property
    def duration_ms(self) -> float | None:
        """Duration in milliseconds, or None if not ended."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute (searchable metadata)."""
        self.attributes[key] = value

    def add_event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        """Record an event during span execution."""
        self.events.append(
            SpanEvent(
                name=name,
                timestamp=timestamp or datetime.now(timezone.utc),
                attributes=attributes or {},
            )
        )

    def add_link(
        self,
        linked_context: SpanContext,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Link this span to another span (for async patterns)."""
        self.links.append(
            SpanLink(
                context=linked_context,
                attributes=attributes or {},
            )
        )

    def next_sequence(self) -> int:
        """Get next sequence number for event ordering."""
        return next(self._sequence)

    def record_exception(self, exc: Exception) -> None:
        """Record an exception and set error status."""
        self.status = SpanStatus.ERROR
        self.set_attribute("error.type", type(exc).__name__)
        self.set_attribute("error.message", str(exc))
        self.add_event(
            "exception",
            {
                "exception.type": type(exc).__name__,
                "exception.message": str(exc),
            },
        )

    def end(self, status: SpanStatus | None = None) -> None:
        """Mark span as ended."""
        self.end_time = datetime.now(timezone.utc)
        if status:
            self.status = status
        elif self.status == SpanStatus.UNSET:
            self.status = SpanStatus.OK

    def extract_carrier(self) -> MoxnTraceCarrier:
        """Extract a carrier for propagation to other services."""
        return MoxnTraceCarrier(
            span_context=self.context,
            prompt_id=self.prompt_id,
            prompt_name=self.prompt_name,
            task_id=self.task_id,
            commit_id=self.commit_id,
            branch_id=self.branch_id,
        )


@dataclass(frozen=True)
class MoxnTraceCarrier:
    """Moxn-specific context bundled with W3C trace context.

    This combines the W3C SpanContext with Moxn's prompt/task metadata
    for crossing async boundaries (message queues, callbacks, etc.).
    """

    span_context: SpanContext
    prompt_id: UUID  # Entity IDs stay as UUID
    prompt_name: str
    task_id: UUID
    commit_id: UUID | None
    branch_id: UUID | None
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def trace_id(self) -> str:
        """The trace ID (32 hex chars)."""
        return self.span_context.trace_id

    @property
    def span_id(self) -> str:
        """The span ID to parent from (16 hex chars)."""
        return self.span_context.span_id

    def to_dict(self) -> dict[str, Any]:
        """Serialize for message queues."""
        return {
            "traceparent": self.span_context.to_traceparent(),
            "tracestate": self.span_context.to_tracestate(),
            "prompt_id": str(self.prompt_id),
            "prompt_name": self.prompt_name,
            "task_id": str(self.task_id),
            "commit_id": str(self.commit_id) if self.commit_id else None,
            "branch_id": str(self.branch_id) if self.branch_id else None,
            "extracted_at": self.extracted_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MoxnTraceCarrier:
        """Deserialize from message queue."""
        span_ctx = SpanContext.from_headers(
            {
                "traceparent": data["traceparent"],
                "tracestate": data.get("tracestate", ""),
            }
        )
        if span_ctx is None:
            raise ValueError("Invalid traceparent in carrier data")

        return cls(
            span_context=span_ctx,
            prompt_id=UUID(data["prompt_id"]),
            prompt_name=data["prompt_name"],
            task_id=UUID(data["task_id"]),
            commit_id=UUID(data["commit_id"]) if data.get("commit_id") else None,
            branch_id=UUID(data["branch_id"]) if data.get("branch_id") else None,
            extracted_at=(
                datetime.fromisoformat(data["extracted_at"])
                if data.get("extracted_at")
                else datetime.now(timezone.utc)
            ),
        )

    def to_headers(self) -> dict[str, str]:
        """Generate headers including Moxn context in tracestate."""
        # Encode Moxn context in tracestate vendor key
        moxn_state = f"pid:{self.prompt_id},tid:{self.task_id}"
        if self.commit_id:
            moxn_state += f",cid:{self.commit_id}"
        if self.branch_id:
            moxn_state += f",bid:{self.branch_id}"

        headers = self.span_context.to_headers()
        # Add/update moxn key in tracestate
        existing_state = headers.get("tracestate", "")
        if existing_state:
            headers["tracestate"] = f"moxn={moxn_state},{existing_state}"
        else:
            headers["tracestate"] = f"moxn={moxn_state}"

        return headers


# =============================================================================
# Telemetry Request/Response Models
# =============================================================================


class TelemetryLogRequest(BaseModel):
    """Unified telemetry log request matching backend telemetry_events table schema.

    Updated for W3C Trace Context compatibility:
    - trace_id: 32 hex chars (was root_span_id as UUID)
    - span_id: 16 hex chars (was UUID)
    - parent_span_id: 16 hex chars or None (was UUID)
    """

    # Core identifiers (event ID stays as UUID)
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Event classification
    event_type: str  # "span_start", "span_end", "llm_call", etc.

    # W3C-compatible trace IDs (hex strings)
    trace_id: str = Field(
        ..., description="32 hex char trace identifier (was root_span_id)"
    )
    span_id: str = Field(..., description="16 hex char span identifier")
    parent_span_id: str | None = Field(
        default=None, description="16 hex char parent span ID"
    )
    sequence_number: int | None = None

    # Context - Entity IDs stay as UUID
    tenant_id: UUID | None = None  # Gateway enriches from request.state
    prompt_id: UUID
    task_id: UUID  # SDK gets from prompt.task_id
    commit_id: UUID | None = None  # One of commit_id or branch_id must be set
    branch_id: UUID | None = None

    # Metadata (always in Postgres, searchable)
    system_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Moxn-generated system metadata"
    )
    user_metadata: dict[str, Any] = Field(
        default_factory=dict, description="User-provided searchable metadata"
    )

    # Content (can be delegated to storage if large)
    content: dict[str, Any] | None = None
    content_stored: bool = False
    content_storage_key: str | None = None

    @field_validator("trace_id")
    @classmethod
    def validate_trace_id(cls, v: str) -> str:
        """Validate trace_id is 32 lowercase hex characters."""
        if len(v) != 32:
            raise ValueError(f"trace_id must be 32 hex chars, got {len(v)}")
        if not all(c in "0123456789abcdef" for c in v.lower()):
            raise ValueError("trace_id must be hex characters")
        return v.lower()

    @field_validator("span_id")
    @classmethod
    def validate_span_id(cls, v: str) -> str:
        """Validate span_id is 16 lowercase hex characters."""
        if len(v) != 16:
            raise ValueError(f"span_id must be 16 hex chars, got {len(v)}")
        if not all(c in "0123456789abcdef" for c in v.lower()):
            raise ValueError("span_id must be hex characters")
        return v.lower()

    @field_validator("parent_span_id")
    @classmethod
    def validate_parent_span_id(cls, v: str | None) -> str | None:
        """Validate parent_span_id is 16 lowercase hex characters if provided."""
        if v is None:
            return v
        if len(v) != 16:
            raise ValueError(f"parent_span_id must be 16 hex chars, got {len(v)}")
        if not all(c in "0123456789abcdef" for c in v.lower()):
            raise ValueError("parent_span_id must be hex characters")
        return v.lower()

    @model_validator(mode="after")
    def validate_version_identifier(self):
        """Ensure exactly one of commit_id or branch_id is provided."""
        if not (bool(self.commit_id) ^ bool(self.branch_id)):
            raise ValueError(
                "Exactly one of commit_id or branch_id must be provided for telemetry"
            )
        return self


class TelemetryLogResponse(BaseModel):
    """Response from telemetry log endpoint"""

    id: UUID
    timestamp: datetime
    status: str = "success"


class ErrorResponse(BaseModel):
    """API error response model - standalone to avoid telemetry validation constraints"""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "error"
    error_message: str
    details: dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    entity_type: str
    entity_id: UUID
    entity_version_id: UUID | None = None


class SignedURLRequest(BaseModel):
    """Request to get a signed URL for storing large payload data"""

    id: UUID = Field(default_factory=uuid4)
    file_path: str
    entity: Entity | None = None
    log_request: TelemetryLogRequest
    media_type: Literal[
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "application/json",
    ]


class SignedURLResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: str
    file_path: str
    expiration: datetime
    message: str = "Signed URL generated successfully"


MAX_INLINE_CONTENT_SIZE = 10 * 1024  # 10KB threshold for inline content


# Transport Protocol
class TelemetryTransport(Protocol):
    """Protocol for sending telemetry data"""

    async def send_log(self, log_request: TelemetryLogRequest) -> TelemetryLogResponse:
        """Send a telemetry log event"""
        ...

    async def send_telemetry_log_and_get_signed_url(
        self, log_request: SignedURLRequest
    ) -> SignedURLResponse:
        """Get a signed URL for storing large payload data"""
        ...


ParsedResponseT = TypeVar("ParsedResponseT", bound=ParsedResponseModelBase)
MessageT = TypeVar("MessageT", bound=MessageBase)


class LLMEventModelBase(BaseModel, Generic[ParsedResponseT, MessageT]):
    """Domain model for LLM interactions"""

    prompt_id: UUID = Field(..., alias="promptId")
    prompt_name: str = Field(..., alias="promptName")
    task_id: UUID = Field(..., alias="taskId")
    branch_id: UUID | None = Field(..., alias="branchId")
    commit_id: UUID | None = Field(
        ..., alias="commitId"
    )  # Changed from prompt_commit_id
    messages: list[MessageT] = Field(..., alias="messages")
    provider: Provider | None = Field(default=None, alias="provider")
    raw_response: dict[str, Any] = Field(..., alias="rawResponse")
    parsed_response: ParsedResponseT = Field(..., alias="parsedResponse")
    session_data: RenderableModel | None = Field(default=None, alias="sessionData")
    rendered_input: Optional[dict[str, Any]] = Field(
        default=None, alias="renderedInput"
    )
    attributes: Optional[dict[str, Any]] = Field(default=None, alias="attributes")
    is_uncommitted: bool = Field(
        default=False,
        alias="isUncommitted",
        description="True when prompt is from branch working state (commit_id is None)",
    )

    # Enhanced telemetry fields for function calling and structured generation
    response_type: ResponseType = Field(
        default=ResponseType.TEXT,
        alias="responseType",
        description="Classification of response type for observability",
    )
    request_config: Optional["RequestConfig"] = Field(
        default=None,
        alias="requestConfig",
        description="Provider-specific request configuration (tools, schemas, etc.)",
    )
    schema_definition: Optional["SchemaDefinition"] = Field(
        default=None,
        alias="schemaDefinition",
        description="Schema or tool definitions used in the request",
    )
    tool_calls_count: int = Field(
        default=0,
        alias="toolCallsCount",
        description="Number of parallel tool calls in the response",
    )
    validation_errors: Optional[list[str]] = Field(
        default=None,
        alias="validationErrors",
        description="Schema validation errors if any occurred",
    )

    @field_serializer("request_config", when_used="json")
    def serialize_request_config(
        self, value: Optional["RequestConfig"]
    ) -> Optional[dict[str, Any]]:
        """Serialize RequestConfig subclasses with all their provider-specific fields.

        Without this, Pydantic only serializes base RequestConfig fields,
        losing provider-specific fields like response_format, tools, etc.
        """
        if value is None:
            return None
        # Call model_dump on the actual subclass instance to get all fields
        return value.model_dump(mode="json", by_alias=True)

    @field_serializer("schema_definition", when_used="json")
    def serialize_schema_definition(
        self, value: Optional["SchemaDefinition"]
    ) -> Optional[dict[str, Any]]:
        """Serialize SchemaDefinition with proper field serializers applied."""
        if value is None:
            return None
        return value.model_dump(mode="json", by_alias=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class LLMEventModel(LLMEventModelBase[ParsedResponseModelBase, MessageDTO]):
    """Domain model for LLM interactions"""

    messages: list[MessageDTO] = Field(..., alias="messages")
    parsed_response: ParsedResponseModelBase = Field(..., alias="parsedResponse")
