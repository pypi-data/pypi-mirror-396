import json
import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Literal, cast, overload
from uuid import UUID

import httpx
from moxn.types.base import BranchHeadResponse, RenderableModel, VersionRef
from moxn.types.content import Provider
from moxn.types.requests import MessageData, PromptCreateRequest, TaskCreateRequest
from moxn.types.responses import DatamodelCodegenResponse
from moxn.types.telemetry import (
    MoxnTraceCarrier,
    Span,
    SpanContext,
    TelemetryLogRequest,
    TelemetryLogResponse,
    TraceContext,
)
from moxn.types.type_aliases.anthropic import AnthropicMessage
from moxn.types.type_aliases.google import GoogleGenerateContentResponse
from moxn.types.type_aliases.openai_chat import OpenAIChatCompletion

from moxn.base_models.blocks.signed import (
    SignedURLContent,
    SignedURLImageContent,
    SignedURLPDFContent,
)
from moxn.content.client import ContentClient
from moxn.models.prompt import PromptSession, PromptTemplate
from moxn.models.response import LLMEvent
from moxn.models.task import Task
from moxn.settings import MoxnSettings
from moxn.storage.storage import InMemoryStorage
from moxn.telemetry.client import TelemetryClient

logger = logging.getLogger(__name__)


class MoxnClient:
    """
    Moxn API client for interacting with the Moxn platform.

    Example:
        ```python
        # Automatically uses MOXN_API_KEY from environment
        async with MoxnClient() as client:
            session = await client.create_prompt_session(
                prompt_id=f"{uuid}",
                branch_name="main"  # or commit_id="{commit_id}"
            )
        ```
    """

    def __init__(self) -> None:
        self.settings = MoxnSettings()  # type: ignore
        self._client: httpx.AsyncClient | None = None
        self.storage = InMemoryStorage()
        self._context_depth = 0  # Track nested context usage
        self._registered_file_paths: set[str] = set()  # Track registered signed content

        self.telemetry_client = TelemetryClient.from_settings(self.settings)
        self.content_client = ContentClient.from_settings(self.settings)

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, creating it if necessary."""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> httpx.AsyncClient:
        """Creates an authenticated httpx client."""
        return httpx.AsyncClient(
            base_url=str(self.settings.base_api_route),
            timeout=self.settings.timeout,
            headers=self.get_headers(),
        )

    def get_headers(self, _: bool = True) -> dict:
        return _get_headers(self.settings, _)

    async def __aenter__(self) -> "MoxnClient":
        self._context_depth += 1
        if self._client is None:
            self._client = self._create_client()
        await self.telemetry_client.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._context_depth -= 1
        if self._context_depth == 0:
            await self.telemetry_client.stop()
            # Polling removed - no cleanup needed
            await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def get_telemetry_diagnostics(self) -> dict:
        """Get diagnostic information from telemetry system."""
        dispatcher_diag = {}
        if (
            hasattr(self.telemetry_client, "_dispatcher")
            and self.telemetry_client._dispatcher
        ):
            dispatcher_diag = self.telemetry_client._dispatcher.get_diagnostics()

        return {
            "dispatcher": dispatcher_diag,
            "telemetry_started": getattr(self.telemetry_client, "_started", False),
        }

    async def verify_access(self) -> dict:
        """Verify API access and return authenticated identity information.

        This method calls the gateway's /debug/whoami endpoint to verify that:
        - The API key is valid
        - Authentication is working correctly
        - The gateway can communicate with the backend

        Returns:
            dict: Authentication information including:
                - authenticated: bool
                - tenant_id: str
                - message: str

        Raises:
            httpx.HTTPStatusError: If authentication fails
        """
        response = await self.get("/debug/whoami")
        response.raise_for_status()
        return response.json()

    def _sanitize_module_name(self, filename: str) -> str:
        """
        Sanitize filename to ensure it's a valid Python module name.

        Args:
            filename: Original filename (e.g., "sdk-test_models.py")

        Returns:
            Sanitized filename (e.g., "sdk_test_models.py")
        """
        # Remove .py extension if present
        name = filename[:-3] if filename.endswith(".py") else filename

        # Replace hyphens with underscores
        name = name.replace("-", "_")

        # Replace spaces with underscores
        name = name.replace(" ", "_")

        # Remove any characters that aren't alphanumeric or underscore
        name = re.sub(r"[^a-zA-Z0-9_]", "", name)

        # Ensure it doesn't start with a digit
        if name and name[0].isdigit():
            name = f"_{name}"

        # Add .py extension back
        return f"{name}.py" if filename.endswith(".py") else name

    async def get(self, path: str, **kwargs) -> httpx.Response:
        """Perform a GET request."""
        return await self.client.get(path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response:
        """Perform a POST request."""
        return await self.client.post(path, **kwargs)

    async def put(self, path: str, **kwargs) -> httpx.Response:
        """Perform a PUT request."""
        return await self.client.put(path, **kwargs)

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """Perform a DELETE request."""
        return await self.client.delete(path, **kwargs)

    def _unwrap_gateway_response(self, response_data: dict) -> dict:
        """
        Unwrap the gateway's standardized APIResponse format.

        Expected format: {"success": bool, "data": {...}, "error": null}
        Returns the "data" field if successful, raises ValueError if not.
        """
        if not response_data.get("success"):
            error_msg = response_data.get("error", "Unknown error")
            raise ValueError(f"Gateway returned error: {error_msg}")

        return response_data["data"]

    async def get_branch_head(
        self, task_id: str, branch_name: str = "main"
    ) -> BranchHeadResponse:
        """
        Get the head commit for a branch.

        Use this during development to get the latest commit on a branch.
        In production, use explicit commit IDs.
        """
        params = {"task_id": task_id}  # Fixed: use snake_case for FastAPI endpoint
        response = await self.get(f"/branches/{branch_name}/head", params=params)
        response.raise_for_status()

        response_data = self._unwrap_gateway_response(response.json())
        return BranchHeadResponse.model_validate(response_data)

    async def _register_signed_content_in_messages(self, messages: list) -> None:
        """Register all signed content blocks for automatic URL refresh.

        Recursively scans message blocks and registers any SignedURL content
        with the content client's refresh engine. Uses file_path-based deduplication
        to prevent duplicate heap entries for the same storage file.

        Args:
            messages: List of messages to scan for signed content
        """

        for message in messages:
            for block_group in message.blocks:
                for block in block_group:
                    # Check for base SignedURLContent and all subclasses
                    if isinstance(
                        block,
                        (SignedURLContent, SignedURLImageContent, SignedURLPDFContent),
                    ):
                        # Only register if we haven't seen this file_path yet
                        if block.file_path not in self._registered_file_paths:
                            await self.content_client.register_content(block)
                            self._registered_file_paths.add(block.file_path)

    async def fetch_task(self, task_id: str, version: VersionRef) -> Task:
        """
        Fetch a task from the gateway API. Always fetches directly from API.
        """
        params = {}
        if version.branch_name:
            params["branch_name"] = version.branch_name
        else:
            assert version.commit_id is not None
            params["commit_id"] = version.commit_id

        response = await self.get(f"/tasks/{task_id}", params=params)
        response.raise_for_status()

        task_data = self._unwrap_gateway_response(response.json())
        task = Task.model_validate(task_data)

        # Register signed content for auto-refresh from all prompts in task
        for prompt in task.prompts:
            await self._register_signed_content_in_messages(prompt.messages)

        return task

    async def fetch_prompt(self, prompt_id: str, version: VersionRef) -> PromptTemplate:
        """
        Fetch a prompt from the gateway API. Always fetches directly from API.
        """
        params = {}
        if version.branch_name:
            params["branch_name"] = version.branch_name
        else:
            assert version.commit_id is not None
            params["commit_id"] = version.commit_id

        response = await self.get(f"/prompts/{prompt_id}", params=params)
        response.raise_for_status()

        prompt_data = self._unwrap_gateway_response(response.json())
        prompt = PromptTemplate.model_validate(prompt_data)

        # Register signed content for auto-refresh
        await self._register_signed_content_in_messages(prompt.messages)

        return prompt

    async def get_prompt(
        self,
        prompt_id: UUID | str,
        branch_name: str | None = None,
        commit_id: str | None = None,
    ) -> PromptTemplate:
        """
        Get a prompt with caching. Commits are cached (immutable), branches always fetch latest.

        Args:
            prompt_id: The prompt ID
            branch_name: Branch name (mutually exclusive with commit_id)
            commit_id: Commit ID (mutually exclusive with branch_name)
        """
        if not isinstance(prompt_id, str):
            prompt_id = str(prompt_id)

        version = VersionRef(branch_name=branch_name, commit_id=commit_id)

        # Only cache commits (immutable), always fetch branches (latest)
        if version.commit_id:
            try:
                return await self.storage.get_prompt_by_commit(
                    prompt_id, version.commit_id
                )
            except KeyError:
                pass

            prompt = await self.fetch_prompt(prompt_id, version)
            await self.storage.store_prompt(prompt, commit_id=version.commit_id)
            return prompt
        else:
            # Always fetch branches to get latest
            return await self.fetch_prompt(prompt_id, version)

    async def get_task(
        self,
        task_id: str,
        branch_name: str | None = None,
        commit_id: str | None = None,
    ) -> Task:
        """
        Get a task with caching. Commits are cached (immutable), branches always fetch latest.

        Args:
            task_id: The task ID
            branch_name: Branch name (mutually exclusive with commit_id)
            commit_id: Commit ID (mutually exclusive with branch_name)
        """

        version = VersionRef(branch_name=branch_name, commit_id=commit_id)

        # Only cache commits (immutable), always fetch branches (latest)
        if version.commit_id:
            try:
                return await self.storage.get_task_by_commit(task_id, version.commit_id)
            except KeyError:
                pass

            task = await self.fetch_task(task_id, version)
            await self.storage.store_task(task, commit_id=version.commit_id)
            return task
        else:
            # Always fetch branches to get latest
            return await self.fetch_task(task_id, version)

    async def generate_task_models(
        self,
        task_id: str | UUID,
        branch_name: str | None = None,
        commit_id: str | None = None,
        output_dir: Path | str | None = None,
    ) -> DatamodelCodegenResponse:
        """
        Generate Python models from all schemas in a task using the new task-based endpoint.

        Args:
            task_id: The task ID to generate models from
            branch_name: Branch name (mutually exclusive with commit_id, defaults to "main")
            commit_id: Commit ID (mutually exclusive with branch_name)
            output_dir: Optional directory to write the generated code to

        Returns:
            DatamodelCodegenResponse object containing the generated code

        Raises:
            RuntimeError: If the generation request fails
            IOError: If file operations fail
        """
        version = VersionRef(branch_name=branch_name, commit_id=commit_id)

        task_id_str = str(task_id) if isinstance(task_id, UUID) else task_id
        logger.info(
            f"Generating task models for task {task_id_str} on {version.model_dump_json()}"
        )

        try:
            # Make POST request to the new task-based endpoint
            params = {}
            if version.branch_name:
                params["branch_name"] = version.branch_name
            else:
                assert version.commit_id is not None
                params["commit_id"] = version.commit_id

            response = await self.post(
                f"/tasks/{task_id_str}/generate-models",
                params=params,
            )

            if response.status_code != 200:
                logger.error(f"Task model generation failed: {response.status_code}")
                logger.error(f"Response content: {response.text}")

                try:
                    error_detail = response.json()
                    error_message = error_detail.get("message", response.text)
                except json.JSONDecodeError:
                    error_message = response.text or f"HTTP {response.status_code}"

                raise RuntimeError(f"Task model generation failed: {error_message}")

            # Parse response
            response_data = self._unwrap_gateway_response(response.json())
            codegen_response = DatamodelCodegenResponse.model_validate(response_data)
            logger.info(f"Generated code for {codegen_response.filename}")

            # Validate generated code
            if not codegen_response.generated_code.strip():
                raise ValueError("Generated code is empty")

            # Optionally write to files
            if output_dir is not None:
                output_path = (
                    Path(output_dir) if isinstance(output_dir, str) else output_dir
                )
                output_path.mkdir(parents=True, exist_ok=True)

                # Sanitize filename to ensure valid Python module name
                sanitized_filename = self._sanitize_module_name(
                    codegen_response.filename
                )
                file_path = output_path / sanitized_filename
                file_path.write_text(codegen_response.generated_code)
                logger.info(f"Saved generated code to {file_path}")

            return codegen_response

        except httpx.TimeoutException as e:
            logger.error(f"Task model generation timed out: {e}")
            raise RuntimeError("Task model generation timed out") from e
        except Exception as e:
            logger.error(f"Task model generation failed: {e}", exc_info=True)
            raise RuntimeError("Task model generation failed") from e

    async def create_task(
        self,
        name: str,
        description: str | None = None,
        branch_name: str = "main",
    ) -> Task:
        """
        Create a new task.

        Args:
            name: Task name (1-255 chars)
            description: Optional description (max 1000 chars)
            branch_name: Branch to create on (defaults to "main")

        Returns:
            The created Task with generated IDs and default branch

        Example:
            task = await client.create_task("Customer Support Bot")
        """
        request = TaskCreateRequest(
            name=name,
            description=description,
            branchName=branch_name,
        )

        response = await self.post(
            "/tasks",
            json=request.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        response.raise_for_status()

        task_data = self._unwrap_gateway_response(response.json())
        return Task.model_validate(task_data)

    async def create_prompt(
        self,
        task_id: str | UUID,
        name: str,
        messages: list[MessageData | dict],
        description: str | None = None,
        branch_name: str = "main",
    ) -> PromptTemplate:
        """
        Create a new prompt with messages.

        Args:
            task_id: Parent task ID
            name: Prompt name
            messages: List of MessageData objects or dicts
            description: Optional description
            branch_name: Branch to create on (defaults to "main")

        Returns:
            The created PromptTemplate with auto-generated input schema

        Example:
            from moxn.types.requests import MessageData
            from moxn.types.content import MessageRole
            from moxn.types.blocks.text import TextContentModel
            from moxn.types.blocks.variable import TextVariableModel, VariableFormat

            messages = [
                MessageData(
                    name="System",
                    role=MessageRole.SYSTEM,
                    blocks=[[TextContentModel(text="You are helpful.")]]
                ),
                MessageData(
                    name="User Query",
                    role=MessageRole.USER,
                    blocks=[[TextVariableModel(
                        name="query",
                        format=VariableFormat.INLINE,
                        description="User's question",
                        required=True
                    )]]
                )
            ]
            prompt = await client.create_prompt(task.id, "Q&A", messages)
        """
        task_id = UUID(task_id) if isinstance(task_id, str) else task_id

        # Convert dicts to MessageData if needed
        message_data = [
            MessageData(**msg) if isinstance(msg, dict) else msg for msg in messages
        ]

        request = PromptCreateRequest(
            name=name,
            taskId=task_id,
            description=description,
            branchName=branch_name,
            messages=message_data,
        )

        response = await self.post(
            "/prompts",
            json=request.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )
        response.raise_for_status()

        prompt_data = self._unwrap_gateway_response(response.json())
        prompt = PromptTemplate.model_validate(prompt_data)

        # Register any signed content for auto-refresh
        await self._register_signed_content_in_messages(prompt.messages)

        return prompt

    async def create_telemetry_log(
        self,
        log_request: TelemetryLogRequest,
    ) -> TelemetryLogResponse:
        """Send telemetry log to the API."""
        logger.debug(f"Sending telemetry log: {log_request}")

        try:
            # Ensure proper serialization of all fields
            json_data = log_request.model_dump(
                exclude_none=True,
                mode="json",
                by_alias=True,
            )

            response = await self.client.post(
                "/telemetry/log-event",
                json=json_data,
            )
            response.raise_for_status()

            response_data = self._unwrap_gateway_response(response.json())
            return TelemetryLogResponse.model_validate(response_data)

        except httpx.TimeoutException as e:
            logger.error(f"Telemetry prompt timed out: {e}")
            raise RuntimeError("Telemetry prompt timed out") from e
        except Exception as e:
            logger.error(f"Telemetry prompt failed: {e}", exc_info=True)
            raise RuntimeError("Failed to send telemetry log") from e

    async def create_prompt_session(
        self,
        prompt_id: str,
        branch_name: str | None = None,
        commit_id: str | None = None,
        session_data: RenderableModel | None = None,
    ) -> PromptSession:
        """
        Create a new PromptSession for managing LLM interactions.

        Args:
            prompt_id: The base prompt ID
            branch_name: Branch name (mutually exclusive with commit_id, defaults to "main")
            commit_id: Commit ID (mutually exclusive with branch_name)
            session_data: Optional session data to use in message rendering
        """
        prompt = await self.get_prompt(
            prompt_id, branch_name=branch_name, commit_id=commit_id
        )
        session = PromptSession.from_prompt_template(
            prompt=prompt, session_data=session_data
        )
        return session

    async def prompt_session_from_session_data(
        self,
        session_data: RenderableModel,
        branch_name: str | None = None,
        commit_id: str | None = None,
    ) -> PromptSession:
        """
        Create a new PromptSession for managing LLM interactions.

        Args:
            session_data: Input schema to use in message rendering
            branch_name: Branch name (mutually exclusive with commit_id)
            commit_id: Commit ID (mutually exclusive with branch_name).
                If both branch_name and commit_id are None, falls back to
                session_data.moxn_schema_metadata.commit_id.

        Raises:
            ValueError: If session_data does not have a prompt_id (e.g., task-level schema)
        """
        if not session_data.moxn_schema_metadata.prompt_id:
            raise ValueError(
                "Session data must have prompt_id to create a prompt session. "
                "Task-level schemas without prompt_id cannot be used for sessions."
            )

        # Fallback to session_data's commit_id if no explicit version args
        # Branch-based access is always explicit (no fallback to branch_id)
        effective_commit_id = commit_id
        if branch_name is None and commit_id is None:
            effective_commit_id = session_data.moxn_schema_metadata.commit_id

        prompt = await self.get_prompt(
            session_data.moxn_schema_metadata.prompt_id,
            branch_name=branch_name,
            commit_id=effective_commit_id,
        )
        session = PromptSession.from_prompt_template(
            prompt=prompt, session_data=session_data
        )
        return session

    @asynccontextmanager
    async def span(
        self,
        prompt_session: PromptSession,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        *,
        parent_context: SpanContext | None = None,
        trace_context: TraceContext | None = None,
    ) -> AsyncGenerator[Span, None]:
        """
        Creates a new span and sets it as the current span.

        Context resolution order:
        1. parent_context parameter (explicit parent for callbacks)
        2. current_span ContextVar (automatic nesting)
        3. trace_context parameter (new root in existing trace)
        4. Generate new trace

        Args:
            prompt_session: The prompt session for this span
            name: Optional span name (defaults to prompt name)
            metadata: User-provided searchable metadata (e.g., customer_id, request_id)
            parent_context: Explicit parent SpanContext (for async/callback patterns)
            trace_context: Explicit TraceContext (for distributed tracing)

        Example:
            async with client.span(
                prompt_session=session,
                name="document_processing",
                metadata={"customer_id": "cust_123", "document_type": "invoice"}
            ) as span:
                # Add more metadata during execution
                span.set_attribute("status", "processing")
                await client.log_telemetry_event(llm_event)

        Example (distributed tracing):
            # Continue a trace from incoming HTTP headers
            trace_ctx = extract_trace_context(request.headers)
            async with client.span(session, trace_context=trace_ctx) as span:
                await client.log_telemetry_event(llm_event)

        Example (async callback):
            # Pass parent context to a callback
            carrier = client.extract_context()
            await queue.put({"carrier": carrier.model_dump(), "data": ...})

            # In callback handler:
            carrier = MoxnTraceCarrier.model_validate(message["carrier"])
            async with client.span_from_carrier(carrier) as span:
                await process(message["data"])
        """
        if name is None:
            name = prompt_session.prompt.name
        async with self.telemetry_client.span(
            prompt_session=prompt_session,
            name=name,
            metadata=metadata,
            parent_context=parent_context,
            trace_context=trace_context,
        ) as span:
            yield span

    @asynccontextmanager
    async def span_from_carrier(
        self,
        carrier: MoxnTraceCarrier,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AsyncGenerator[Span, None]:
        """
        Create a span that continues from a MoxnTraceCarrier.

        Use this when receiving trace context from another service
        or resuming a trace in a callback/queue handler.

        Args:
            carrier: The trace carrier containing context and Moxn metadata
            name: Optional span name (defaults to prompt name from carrier)
            metadata: User-provided searchable attributes

        Example:
            # In a queue worker or callback handler
            carrier = MoxnTraceCarrier.model_validate(message["carrier"])
            async with client.span_from_carrier(carrier, name="process_item") as span:
                span.set_attribute("item_id", message["item_id"])
                await process(message["data"])
        """
        async with self.telemetry_client.span_from_carrier(
            carrier=carrier,
            name=name,
            metadata=metadata,
        ) as span:
            yield span

    def extract_context(self) -> MoxnTraceCarrier | None:
        """
        Extract current span as a carrier for propagation.

        Use this to pass trace context across async boundaries,
        to queue workers, or to other services.

        Returns:
            MoxnTraceCarrier if there's an active span, None otherwise.

        Example:
            async with client.span(session) as span:
                # Extract carrier to pass to a queue worker
                carrier = client.extract_context()
                if carrier:
                    await queue.put({
                        "carrier": carrier.model_dump(mode="json"),
                        "data": payload
                    })
        """
        return self.telemetry_client.extract_context()

    async def log_telemetry_event(self, event: LLMEvent) -> None:
        """Log an LLM event to the current span context or create a temporary span if needed."""
        event = event.model_copy(deep=True)
        await self.telemetry_client.log_event(event=event)

    @overload
    async def log_telemetry_event_from_response(
        self,
        prompt_session: PromptSession,
        response: AnthropicMessage,
        provider: Literal[Provider.ANTHROPIC],
    ) -> None: ...

    @overload
    async def log_telemetry_event_from_response(
        self,
        prompt_session: PromptSession,
        response: OpenAIChatCompletion,
        provider: Literal[Provider.OPENAI_CHAT],
    ) -> None: ...

    @overload
    async def log_telemetry_event_from_response(
        self,
        prompt_session: PromptSession,
        response: GoogleGenerateContentResponse,
        provider: Literal[Provider.GOOGLE_GEMINI] | Literal[Provider.GOOGLE_VERTEX],
    ) -> None: ...

    async def log_telemetry_event_from_response(
        self,
        prompt_session: PromptSession,
        response: (
            OpenAIChatCompletion | AnthropicMessage | GoogleGenerateContentResponse
        ),
        provider: Provider,
    ) -> None:
        """Log an LLM event to the current span context."""
        match provider:
            case Provider.ANTHROPIC:
                event = prompt_session.create_llm_event_from_response(
                    response=cast(AnthropicMessage, response),
                    provider=provider,
                )
            case Provider.OPENAI_CHAT:
                event = prompt_session.create_llm_event_from_response(
                    response=cast(OpenAIChatCompletion, response),
                    provider=provider,
                )
            case Provider.GOOGLE_GEMINI:
                event = prompt_session.create_llm_event_from_response(
                    response=cast(GoogleGenerateContentResponse, response),
                    provider=provider,
                )
            case Provider.GOOGLE_VERTEX:
                event = prompt_session.create_llm_event_from_response(
                    response=cast(GoogleGenerateContentResponse, response),
                    provider=provider,
                )
            case _:
                raise ValueError(f"Unsupported provider: {provider}")

        await self.log_telemetry_event(event=event)

    async def flush(self, timeout: float | None = None) -> None:
        """
        Await in-flight telemetry logs (call this at process-exit,
        lambda return, or FASTAPI shutdown).
        """
        if timeout is None:
            timeout = self.settings.telemetry_timeout
        await self.telemetry_client._dispatcher.flush(timeout)


def _get_headers(settings: MoxnSettings, _: bool = True) -> dict:
    """Returns headers for API requests - tenant-scoped auth (API key only)."""
    return {
        "x-api-key": settings.api_key.get_secret_value(),
        "Content-Type": "application/json",
    }
