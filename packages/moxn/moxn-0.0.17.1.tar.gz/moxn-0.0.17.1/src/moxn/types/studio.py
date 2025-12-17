"""DTOs for Prompt Studio LLM invocation feature.

This module defines request/response types for the studio invocation endpoint,
enabling the backend to execute LLM invocations through the API gateway for
counterfactual testing (testing prompt changes against historical observations).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from moxn.types.content import Provider
from moxn.types.dto import MessageDTO, SchemaDTO
from moxn.types.request_config import CompletionConfig, RequestConfig, SchemaDefinition
from moxn.types.telemetry import ResponseType
from moxn.types.tool import SdkTool


class LLMErrorCode(str, Enum):
    """Error codes for LLM invocation failures."""

    INVALID_API_KEY = "INVALID_API_KEY"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    RATE_LIMITED = "RATE_LIMITED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    INVALID_MODEL = "INVALID_MODEL"
    CONTENT_FILTERED = "CONTENT_FILTERED"
    CONTEXT_LENGTH_EXCEEDED = "CONTEXT_LENGTH_EXCEEDED"
    VARIABLE_MISSING = "VARIABLE_MISSING"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


# =============================================================================
# Request Types
# =============================================================================


class StudioObservation(BaseModel):
    """Single observation for LLM invocation.

    An observation represents a historical invocation with its messages and
    rendered input values. Messages may include conversation context (previous
    LLM responses, tool calls) merged with template messages.
    """

    id: UUID = Field(
        default_factory=uuid4, description="Unique ID for this observation"
    )
    rendered_input: dict[str, Any] = Field(
        ...,
        alias="renderedInput",
        description="Flat key-value pairs matching prompt variable names",
    )
    messages: Sequence[MessageDTO] = Field(
        ...,
        description="Messages for this observation (with variable blocks to hydrate)",
    )

    model_config = ConfigDict(populate_by_name=True)


class StudioExecutionMetadata(BaseModel):
    """Tracking metadata from backend - echoed in response.

    The backend can include any fields needed for tracking; they are
    echoed back in the response without modification.
    """

    execution_id: UUID = Field(..., alias="executionId")

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class StudioPromptDTO(BaseModel):
    """Prompt DTO for studio invocations - messages are per-observation.

    This type contains prompt metadata and configuration but excludes messages,
    which are now provided per-observation to support multi-turn conversations.
    """

    id: UUID
    name: str
    description: str | None = None
    task_id: UUID = Field(..., alias="taskId")
    input_schema: SchemaDTO = Field(..., alias="inputSchema")
    completion_config: CompletionConfig | None = Field(None, alias="completionConfig")
    tools: Sequence[SdkTool] | None = Field(
        None,
        description="Tools attached to this prompt for function calling or structured output.",
    )

    model_config = ConfigDict(populate_by_name=True)


class StudioInvocationRequest(BaseModel):
    """Request to execute LLM invocations for Prompt Studio.

    Enables counterfactual testing: execute a (potentially modified) prompt
    against historical observations to see how the output would change.

    Messages are now per-observation to support multi-turn conversations where
    each observation may have different conversation context.
    """

    # Prompt definition (without messages - messages are per-observation)
    prompt: StudioPromptDTO = Field(..., description="Prompt metadata and configuration")

    # Version context
    task_id: UUID = Field(..., alias="taskId")
    branch_id: UUID | None = Field(None, alias="branchId")
    commit_id: str | None = Field(None, alias="commitId")

    # Observations to process (1-10)
    observations: Sequence[StudioObservation] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="1-10 observations to evaluate against the prompt",
    )

    # Provider configuration
    completion_config: CompletionConfig = Field(..., alias="completionConfig")
    provider_api_key: SecretStr = Field(
        ...,
        alias="providerApiKey",
        description="Provider API key (passed per-request, not stored)",
    )

    # Tracking metadata (echoed back in response)
    execution_metadata: StudioExecutionMetadata = Field(..., alias="executionMetadata")

    model_config = ConfigDict(populate_by_name=True)


# =============================================================================
# Response Types - Aligned with LLMEventModelBase
# =============================================================================


class StudioObservationResult(BaseModel):
    """Result for a single observation - mirrors LLMEventModelBase fields.

    Contains both the LLM response data (aligned with telemetry events)
    and studio-specific fields like latency and error details.
    """

    # Observation identification
    observation_id: UUID = Field(..., alias="observationId")

    # LLMEventModelBase-aligned fields
    prompt_id: UUID = Field(..., alias="promptId")
    prompt_name: str = Field(..., alias="promptName")
    branch_id: UUID | None = Field(None, alias="branchId")
    commit_id: str | None = Field(None, alias="commitId")
    messages: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Messages used in the invocation (serialized with blocks)",
    )
    provider: Provider
    raw_response: dict[str, Any] | None = Field(
        None,
        alias="rawResponse",
        description="Raw response from the LLM provider",
    )
    parsed_response: dict[str, Any] | None = Field(
        None,
        alias="parsedResponse",
        description="Normalized response with content blocks (pre-serialized dict)",
    )
    rendered_input: dict[str, Any] = Field(
        ...,
        alias="renderedInput",
        description="The observation's rendered input (echoed back)",
    )
    response_type: ResponseType | None = Field(
        None,
        alias="responseType",
        description="Classification of response type (text, tool_calls, etc.)",
    )
    request_config: RequestConfig | None = Field(
        None,
        alias="requestConfig",
        description="Provider-specific request configuration used",
    )
    schema_definition: SchemaDefinition | None = Field(
        None,
        alias="schemaDefinition",
        description="Schema or tool definitions used in the request",
    )
    validation_errors: list[str] | None = Field(
        None,
        alias="validationErrors",
        description="Schema validation errors if any occurred",
    )
    tool_calls_count: int = Field(
        0,
        alias="toolCallsCount",
        description="Number of tool calls in the response",
    )
    attributes: dict[str, Any] | None = Field(
        None,
        description="Observation attributes (provider, responseType, etc.)",
    )

    # Studio-specific fields
    status: Literal["success", "error"] = Field(
        ...,
        description="Whether the invocation succeeded or failed",
    )
    latency_ms: float = Field(
        ...,
        alias="latencyMs",
        description="Execution time in milliseconds",
    )
    error_code: LLMErrorCode | None = Field(
        None,
        alias="errorCode",
        description="Error code if status is 'error'",
    )
    error_message: str | None = Field(
        None,
        alias="errorMessage",
        description="Human-readable error message if status is 'error'",
    )

    model_config = ConfigDict(populate_by_name=True)


class StudioInvocationResponse(BaseModel):
    """Response from studio invocation endpoint.

    Contains results for all observations plus aggregate statistics.
    Partial failures are supported - some observations may succeed while others fail.
    """

    # Echoed tracking metadata
    execution_metadata: StudioExecutionMetadata = Field(..., alias="executionMetadata")

    # Per-observation results
    results: Sequence[StudioObservationResult]

    # Aggregate statistics
    total_observations: int = Field(..., alias="totalObservations")
    successful_count: int = Field(..., alias="successfulCount")
    failed_count: int = Field(..., alias="failedCount")

    model_config = ConfigDict(populate_by_name=True)
