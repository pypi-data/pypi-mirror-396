from moxn.types import exceptions, schema, utils
from moxn.types.auth import TenantAuth
from moxn.types.sentinel import NOT_GIVEN, BaseModelWithOptionalFields, NotGivenOr
from moxn.types.base import (
    VersionRef,
    GitTrackedEntity,
    Branch,
    Commit,
    BranchHeadResponse,
    CommitInfoResponse,
)
from moxn.types.tool import SdkTool, SdkSchema

# Rebuild models that have forward references to SdkTool
# This resolves the TYPE_CHECKING import in base.py
from moxn.types.base import BasePrompt

BasePrompt.model_rebuild()

from moxn.types.dto import (
    MessageDTO,
    PromptDTO,
    TaskDTO,
    SchemaDTO,
)

# Rebuild DTO models that inherit from BasePrompt
PromptDTO.model_rebuild()
from moxn.types.responses import (
    PromptAtCommit,
    MessageAtCommit,
    TaskSnapshot,
    EntityResponse,
)
from moxn.types.telemetry import (
    # W3C Trace Context types
    TraceContext,
    SpanContext,
    SpanStatus,
    SpanEvent,
    SpanLink,
    Span,
    MoxnTraceCarrier,
    # Request/Response models
    TelemetryLogRequest,
    TelemetryLogResponse,
    TelemetryTransport,
    ResponseType,
    # Event type constants
    EVENT_TYPE_SPAN_START,
    EVENT_TYPE_SPAN_END,
    EVENT_TYPE_SPAN_ERROR,
    EVENT_TYPE_LLM_CALL,
    EVENT_TYPE_TOOL_CALL,
    EVENT_TYPE_VALIDATION,
    EVENT_TYPE_CUSTOM,
)
from moxn.types.requests import (
    TaskCreateRequest,
    MessageData,
    PromptCreateRequest,
)
from moxn.types.request_config import CompletionConfig
from moxn.types.studio import (
    LLMErrorCode,
    StudioObservation,
    StudioExecutionMetadata,
    StudioPromptDTO,
    StudioInvocationRequest,
    StudioObservationResult,
    StudioInvocationResponse,
)

__all__ = [
    "exceptions",
    "utils",
    "schema",
    "TenantAuth",
    "NOT_GIVEN",
    "NotGivenOr",
    "BaseModelWithOptionalFields",
    # W3C Trace Context types
    "TraceContext",
    "SpanContext",
    "SpanStatus",
    "SpanEvent",
    "SpanLink",
    "Span",
    "MoxnTraceCarrier",
    # Telemetry request/response
    "TelemetryLogRequest",
    "TelemetryLogResponse",
    "TelemetryTransport",
    "ResponseType",
    # Event type constants
    "EVENT_TYPE_SPAN_START",
    "EVENT_TYPE_SPAN_END",
    "EVENT_TYPE_SPAN_ERROR",
    "EVENT_TYPE_LLM_CALL",
    "EVENT_TYPE_TOOL_CALL",
    "EVENT_TYPE_VALIDATION",
    "EVENT_TYPE_CUSTOM",
    # Git-based models
    "VersionRef",
    "GitTrackedEntity",
    "Branch",
    "Commit",
    "BranchHeadResponse",
    "CommitInfoResponse",
    # Tool types
    "SdkTool",
    "SdkSchema",
    # DTOs
    "MessageDTO",
    "PromptDTO",
    "TaskDTO",
    "SchemaDTO",
    # Response types
    "PromptAtCommit",
    "MessageAtCommit",
    "TaskSnapshot",
    "EntityResponse",
    # Request types
    "TaskCreateRequest",
    "MessageData",
    "PromptCreateRequest",
    # Config types
    "CompletionConfig",
    # Studio types
    "LLMErrorCode",
    "StudioObservation",
    "StudioExecutionMetadata",
    "StudioPromptDTO",
    "StudioInvocationRequest",
    "StudioObservationResult",
    "StudioInvocationResponse",
]
