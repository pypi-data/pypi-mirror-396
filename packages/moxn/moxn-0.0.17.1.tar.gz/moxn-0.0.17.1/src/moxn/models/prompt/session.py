from typing import Any, Literal, Sequence, overload
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from moxn.base_models.blocks.context import MessageContext
from moxn.models import message as msg
from moxn.models.response import (
    LLMEvent,
    ParsedResponse,
    ResponseParser,
    ResponseTypeDetector,
)
from moxn.types import base
from moxn.types.content import Author, MessageRole, Provider
from moxn.types.request_config import RequestConfig, SchemaDefinition
from moxn.types.type_aliases.anthropic import AnthropicMessage, AnthropicMessagesParam
from moxn.types.type_aliases.google import (
    GoogleGenerateContentResponse,
    GoogleMessagesParam,
)
from moxn.types.type_aliases.openai_chat import (
    OpenAIChatCompletion,
    OpenAIChatMessagesParam,
)
from moxn.types.type_aliases.openai_responses import (
    OpenAIResponse,
    OpenAIResponsesMessagesParam,
)
from moxn.types.type_aliases.provider import (
    ProviderInvocationPayload,
    ProviderMessageParam,
    ProviderPayload,
)
from moxn.types.type_aliases.invocation import (
    AnthropicInvocationParam,
    GoogleInvocationParam,
    OpenAIChatInvocationParam,
    OpenAIResponsesInvocationParam,
)

from .content import PromptContent
from .conversion import MessageConverter
from .core import PromptTemplate
from .prompt_converter import PromptConverter
from .response_handler import ResponseHandler
from .structured_output import StructuredOutputFormatter
from .tool_formatter import ToolChoiceTranslator, ToolFormatter


class PromptSession(BaseModel):
    """Manages the runtime state and operations for a prompt execution."""

    id: UUID = Field(default_factory=uuid4)
    prompt: PromptTemplate
    content: PromptContent
    session_data: base.RenderableModel | None = None
    render_kwargs: dict[str, Any] = {}

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def prompt_id(self) -> UUID:
        return self.prompt.id

    @property
    def prompt_commit_id(self) -> UUID:
        """Deprecated: Use prompt.commit_id directly"""
        if not self.prompt.commit_id:
            raise ValueError("Prompt must have commit_id for telemetry")
        return self.prompt.commit_id

    @property
    def messages(self) -> list[msg.Message]:
        return self.content.messages

    @classmethod
    def from_prompt_template(
        cls,
        prompt: PromptTemplate,
        session_data: base.RenderableModel | None = None,
        render_kwargs: dict[str, Any] | None = None,
    ) -> "PromptSession":
        """Create a PromptSession from a base Prompt."""
        selected_messages = prompt.get_messages()
        return cls(
            prompt=prompt,
            content=PromptContent(messages=selected_messages),
            session_data=session_data,
            render_kwargs=render_kwargs or {},
        )

    def _create_context_from_session_data(self) -> MessageContext | None:
        """Create a MessageContext from session_data's rendered output.

        Returns:
            MessageContext with variables from session_data.render(), or None if no session_data.
        """
        if not self.session_data:
            return None

        # Render the session data to get variables
        rendered_data = self.session_data.render(**self.render_kwargs)

        # Create context from the rendered variables
        if rendered_data:
            return MessageContext.from_variables(rendered_data)

        return None

    def _normalize_context(
        self, user_context: MessageContext | dict | None
    ) -> MessageContext | None:
        """Normalize user context to MessageContext, merging with session_data if available.

        Args:
            user_context: User-provided context as MessageContext, dict, or None.

        Returns:
            Normalized MessageContext, or None if no context available.
        """
        base_context = self._create_context_from_session_data()

        if base_context:
            # We have session_data context - merge with user context
            if user_context is None:
                return base_context
            elif isinstance(user_context, dict):
                return base_context.merge(MessageContext.from_variables(user_context))
            else:
                return base_context.merge(user_context)
        else:
            # No session_data context - normalize user context only
            if user_context is None:
                return None
            elif isinstance(user_context, dict):
                return MessageContext.from_variables(user_context)
            else:
                return user_context

    def to_message_params(
        self,
        provider: Provider,
        context: MessageContext | dict | None = None,
    ) -> Sequence[ProviderMessageParam]:
        """Convert current state to provider-specific message-level blocks.

        Note: This method returns message-level blocks, not complete API payloads.
        For complete prompt-level payloads, use to_provider_payload() or the
        provider-specific methods (to_anthropic, to_openai_chat, etc.).

        Args:
            provider: The LLM provider to format messages for.
            context: Optional context for variable substitution and provider settings.
                     If not provided but session_data exists, context will be auto-generated
                     from session_data.render(). If provided, it will be merged with
                     session_data context (provided context takes precedence).

        Returns:
            Provider-specific message-level blocks.
        """
        final_context = self._normalize_context(context)
        return MessageConverter.to_message_params(
            self.messages,
            provider,
            final_context,
        )

    def to_provider_payload(
        self,
        provider: Provider,
        context: MessageContext | dict | None = None,
    ) -> ProviderPayload:
        """Convert session to provider-specific API payload.

        This is the generic method for converting to any provider's format.
        It produces the complete TypedDict structure expected by provider SDKs.

        Args:
            provider: The LLM provider to format for.
            context: Optional context for variable substitution.
                     If not provided but session_data exists, variables will be auto-populated
                     from session_data.render(). Provided context takes precedence.

        Returns:
            Provider-specific TypedDict ready for SDK usage.
            - Anthropic: {system: ..., messages: [...]}
            - OpenAI: {messages: [...]}
            - Google: {system_instruction: ..., content: [...]}
        """
        final_context = self._normalize_context(context)
        return PromptConverter.to_provider_payload(
            self.messages,
            provider,
            final_context,
        )

    def parse_provider_response(
        self,
        response: Any,
        provider: Provider,
    ) -> ParsedResponse:
        """Parse a provider response into a normalized format."""
        return ResponseHandler.parse_provider_response(response, provider)

    def create_llm_event_from_parsed_response(
        self,
        parsed_response: ParsedResponse,
        request_config: RequestConfig | None = None,
        schema_definition: SchemaDefinition | None = None,
        attributes: dict[str, Any] | None = None,
        validation_errors: list[str] | None = None,
    ) -> LLMEvent:
        """Create an LLM event from messages and parsed response.

        Args:
            parsed_response: The parsed LLM response
            request_config: Optional provider-specific request configuration
            schema_definition: Optional schema or tool definitions used
            attributes: Optional custom attributes
            validation_errors: Optional validation errors if schema validation failed

        Returns:
            LLMEvent with enhanced telemetry fields
        """
        # Detect response type using the detector
        response_type = ResponseTypeDetector.detect(parsed_response, request_config)

        # Count tool calls for telemetry
        tool_calls_count = ResponseTypeDetector.count_tool_calls(parsed_response)

        return LLMEvent(
            promptId=self.prompt_id,
            promptName=self.prompt.name,
            taskId=self.prompt.task_id,
            branchId=self.prompt.branch_id,
            commitId=self.prompt.commit_id,
            messages=[message.model_copy(deep=True) for message in self.messages],
            provider=parsed_response.provider,
            rawResponse=parsed_response.raw_response or {},
            parsedResponse=parsed_response,
            sessionData=self.session_data,
            renderedInput=(
                self.session_data.render(**self.render_kwargs)
                if self.session_data is not None
                else None
            ),
            attributes=attributes,
            isUncommitted=self.prompt.commit_id is None,
            # Enhanced telemetry fields
            responseType=response_type,
            requestConfig=request_config,
            schemaDefinition=schema_definition,
            toolCallsCount=tool_calls_count,
            validationErrors=validation_errors,
        )

    @overload
    def create_llm_event_from_response(
        self,
        response: AnthropicMessage,
        provider: Literal[Provider.ANTHROPIC],
    ) -> LLMEvent: ...

    @overload
    def create_llm_event_from_response(
        self,
        response: OpenAIChatCompletion,
        provider: Literal[Provider.OPENAI_CHAT],
    ) -> LLMEvent: ...

    @overload
    def create_llm_event_from_response(
        self,
        response: OpenAIResponse,
        provider: Literal[Provider.OPENAI_RESPONSES],
    ) -> LLMEvent: ...

    @overload
    def create_llm_event_from_response(
        self,
        response: GoogleGenerateContentResponse,
        provider: Literal[Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX],
    ) -> LLMEvent: ...

    def create_llm_event_from_response(
        self,
        response: (
            AnthropicMessage
            | OpenAIChatCompletion
            | OpenAIResponse
            | GoogleGenerateContentResponse
        ),
        provider: Provider,
    ) -> LLMEvent:
        match provider:
            case Provider.ANTHROPIC:
                parsed_response = ResponseParser.parse(response, Provider.ANTHROPIC)  # type: ignore
            case Provider.OPENAI_CHAT:
                parsed_response = ResponseParser.parse(response, Provider.OPENAI_CHAT)  # type: ignore
            case Provider.OPENAI_RESPONSES:
                parsed_response = ResponseParser.parse(
                    response, Provider.OPENAI_RESPONSES
                )  # type: ignore
            case Provider.GOOGLE_GEMINI:
                parsed_response = ResponseParser.parse(response, Provider.GOOGLE_GEMINI)  # type: ignore
            case Provider.GOOGLE_VERTEX:
                parsed_response = ResponseParser.parse(response, Provider.GOOGLE_VERTEX)  # type: ignore
            case _:
                raise ValueError(f"Unsupported provider: {provider}")

        return self.create_llm_event_from_parsed_response(parsed_response)

    def to_anthropic(
        self, context: MessageContext | dict | None = None
    ) -> AnthropicMessagesParam:
        """Convert session to Anthropic format with system/messages structure.

        Args:
            context: Optional context for variable substitution and provider settings.
                     If not provided but session_data exists, variables will be auto-populated
                     from session_data.render(). Provided context takes precedence.

        Returns:
            AnthropicMessagesParam TypedDict that can be unpacked with ** into the Anthropic SDK.
            The TypedDict has:
            - system: optional system prompt (string or list of blocks)
            - messages: list of user/assistant messages
        """
        final_context = self._normalize_context(context)
        return PromptConverter.to_provider_payload(
            self.messages,
            Provider.ANTHROPIC,
            final_context,
        )

    def to_openai_chat(
        self, context: MessageContext | dict | None = None
    ) -> OpenAIChatMessagesParam:
        """Convert session to OpenAI Chat format with messages array.

        Args:
            context: Optional context for variable substitution and provider settings.
                     If not provided but session_data exists, variables will be auto-populated
                     from session_data.render(). Provided context takes precedence.

        Returns:
            OpenAIChatMessagesParam TypedDict that can be unpacked with ** into the OpenAI SDK.
            The TypedDict has:
            - messages: list of all messages (system, user, assistant)
        """
        final_context = self._normalize_context(context)
        return PromptConverter.to_provider_payload(
            self.messages,
            Provider.OPENAI_CHAT,
            final_context,
        )

    def to_openai_responses(
        self, context: MessageContext | dict | None = None
    ) -> OpenAIResponsesMessagesParam:
        """Convert session to OpenAI Responses API format with input items and instructions.

        Args:
            context: Optional context for variable substitution and provider settings.
                     If not provided but session_data exists, variables will be auto-populated
                     from session_data.render(). Provided context takes precedence.

        Returns:
            OpenAIResponsesMessagesParam TypedDict that can be unpacked with ** into the OpenAI SDK.
            The TypedDict has:
            - input: list of message/tool items
            - instructions: system message text (if any system messages present)
        """
        final_context = self._normalize_context(context)
        return PromptConverter.to_provider_payload(
            self.messages,
            Provider.OPENAI_RESPONSES,
            final_context,
        )

    def to_google_gemini(
        self, context: MessageContext | dict | None = None
    ) -> GoogleMessagesParam:
        """Convert session to Google Gemini format.

        Args:
            context: Optional context for variable substitution and provider settings.
                     If not provided but session_data exists, variables will be auto-populated
                     from session_data.render(). Provided context takes precedence.

        Returns:
            GoogleMessagesParam TypedDict that can be unpacked with ** into the Google SDK.
            The TypedDict has:
            - system_instruction: optional system instruction string
            - content: list of content messages
        """
        final_context = self._normalize_context(context)
        return PromptConverter.to_provider_payload(
            self.messages,
            Provider.GOOGLE_GEMINI,
            final_context,
        )

    def to_google_vertex(
        self, context: MessageContext | dict | None = None
    ) -> GoogleMessagesParam:
        """Convert session to Google Vertex format.

        Args:
            context: Optional context for variable substitution and provider settings.
                     If not provided but session_data exists, variables will be auto-populated
                     from session_data.render(). Provided context takes precedence.

        Returns:
            GoogleMessagesParam TypedDict that can be unpacked with ** into the Google SDK.
            The TypedDict has:
            - system_instruction: optional system instruction string
            - content: list of content messages
        """
        final_context = self._normalize_context(context)
        return PromptConverter.to_provider_payload(
            self.messages,
            Provider.GOOGLE_VERTEX,
            final_context,
        )

    def append_user_text(
        self,
        text: str,
        name: str = "",
        description: str = "",
    ) -> None:
        """Append a user message with text content.

        Args:
            text: The text content to append
            name: Optional name for the message
            description: Optional description for the message
        """
        self.content.append_text(
            text=text,
            name=name,
            description=description,
            role=MessageRole.USER,
        )

    def append_assistant_text(
        self,
        text: str,
        name: str = "",
        description: str = "",
    ) -> None:
        """Append an assistant message with text content.

        Args:
            text: The text content to append
            name: Optional name for the message
            description: Optional description for the message
        """
        self.content.append_text(
            text=text,
            name=name,
            description=description,
            author=Author.MACHINE,
            role=MessageRole.ASSISTANT,
        )

    def append_assistant_response(
        self,
        parsed_response: ParsedResponse,
        candidate_idx: int = 0,
        name: str = "",
        description: str = "",
    ) -> None:
        """Append an assistant response from a parsed LLM response.

        Args:
            parsed_response: The parsed response from an LLM provider
            candidate_idx: Which candidate to use (default 0)
            name: Optional name for the message
            description: Optional description for the message
        """
        self.content.append_parsed_response(
            parsed_response=parsed_response,
            candidate_idx=candidate_idx,
            name=name,
            description=description,
        )

    # -------------------------------------------------------------------------
    # Invocation Methods - Combined message + model parameter payloads
    # -------------------------------------------------------------------------

    def _get_model_params(
        self,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build model parameters dict, merging prompt config with overrides.

        Priority: explicit kwargs > prompt.completion_config > omit

        Args:
            model: Model identifier override
            max_tokens: Max tokens override
            temperature: Temperature override
            top_p: Top-p override
            thinking: Thinking/reasoning configuration override

        Returns:
            Dictionary with model parameters (only includes non-None values)
        """
        config = self.prompt.completion_config
        params: dict[str, Any] = {}

        # Model
        if model is not None:
            params["model"] = model
        elif config and config.model:
            params["model"] = config.model

        # max_tokens
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        elif config and config.max_tokens:
            params["max_tokens"] = config.max_tokens

        # temperature
        if temperature is not None:
            params["temperature"] = temperature
        elif config and config.temperature is not None:
            params["temperature"] = config.temperature

        # top_p
        if top_p is not None:
            params["top_p"] = top_p
        elif config and config.top_p is not None:
            params["top_p"] = config.top_p

        # thinking
        if thinking is not None:
            params["thinking"] = thinking
        elif config and config.thinking is not None:
            params["thinking"] = config.thinking

        return params

    def to_anthropic_invocation(
        self,
        context: MessageContext | dict | None = None,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: dict[str, Any] | None = None,
    ) -> AnthropicInvocationParam:
        """Convert session to complete Anthropic invocation payload.

        Combines messages with model parameters for direct SDK usage:
            response = await anthropic.messages.create(
                **session.to_anthropic_invocation()
            )

        If the prompt has tools configured, they are automatically included.
        If structured output is configured (response_schema_id), output_format is added.

        Note: For structured outputs, you must add the beta header manually:
            extra_headers={"anthropic-beta": "structured-outputs-2025-11-13"}

        Args:
            context: Optional context for variable substitution.
            model: Model override (e.g., "claude-3-opus-20240229")
            max_tokens: Max tokens override (required by Anthropic)
            temperature: Temperature override
            top_p: Top-p override
            thinking: Thinking configuration (type, budget_tokens)

        Returns:
            AnthropicInvocationParam ready for SDK unpacking.
        """
        messages_payload = self.to_anthropic(context)
        model_params = self._get_model_params(
            model, max_tokens, temperature, top_p, thinking
        )
        # Anthropic uses 'thinking' directly, no transformation needed
        result: dict[str, Any] = {**messages_payload, **model_params}

        # Add tools if configured
        function_tools = self.prompt.function_tools
        if function_tools:
            tool_choice_config = (
                self.prompt.completion_config.tool_choice
                if self.prompt.completion_config
                else None
            )

            # Translate tool_choice - if 'none', don't add tools
            if tool_choice_config != "none":
                result["tools"] = ToolFormatter.to_anthropic_tools(function_tools)

                if tool_choice_config:
                    anthropic_tool_choice = ToolChoiceTranslator.to_anthropic(
                        tool_choice_config
                    )
                    if anthropic_tool_choice is not None:
                        result["tool_choice"] = anthropic_tool_choice

        # Add structured output if configured
        structured_schema = self.prompt.structured_output_schema
        if structured_schema:
            result["output_format"] = StructuredOutputFormatter.to_anthropic_output_format(
                structured_schema
            )

        return result  # type: ignore

    def to_openai_chat_invocation(
        self,
        context: MessageContext | dict | None = None,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: dict[str, Any] | None = None,
    ) -> OpenAIChatInvocationParam:
        """Convert session to complete OpenAI Chat invocation payload.

        Combines messages with model parameters for direct SDK usage:
            response = await openai.chat.completions.create(
                **session.to_openai_chat_invocation()
            )

        If the prompt has tools configured, they are automatically included.
        If structured output is configured (response_schema_id), response_format is added.

        Note: When structured output is used, parallel_tool_calls is automatically
        set to False (required by OpenAI).

        Args:
            context: Optional context for variable substitution.
            model: Model override (e.g., "gpt-4")
            max_tokens: Max tokens override
            temperature: Temperature override
            top_p: Top-p override
            thinking: Thinking configuration (reasoning_effort)

        Returns:
            OpenAIChatInvocationParam ready for SDK unpacking.
        """
        messages_payload = self.to_openai_chat(context)
        model_params = self._get_model_params(
            model, max_tokens, temperature, top_p, thinking
        )
        # OpenAI Chat uses 'reasoning_effort' - extract from thinking dict
        if "thinking" in model_params:
            thinking_config = model_params.pop("thinking")
            if isinstance(thinking_config, dict):
                if "reasoning_effort" in thinking_config:
                    model_params["reasoning_effort"] = thinking_config["reasoning_effort"]
                elif "effort" in thinking_config:
                    model_params["reasoning_effort"] = thinking_config["effort"]
        result: dict[str, Any] = {**messages_payload, **model_params}

        # Check if structured output is configured
        structured_schema = self.prompt.structured_output_schema
        has_structured_output = structured_schema is not None

        # Add tools if configured
        function_tools = self.prompt.function_tools
        if function_tools:
            tool_choice_config = (
                self.prompt.completion_config.tool_choice
                if self.prompt.completion_config
                else None
            )

            # Only add tools if tool_choice is not 'none'
            if tool_choice_config != "none":
                result["tools"] = ToolFormatter.to_openai_tools(function_tools)

                if tool_choice_config:
                    result["tool_choice"] = ToolChoiceTranslator.to_openai(
                        tool_choice_config
                    )

                # Handle parallel_tool_calls
                parallel_tool_calls = (
                    self.prompt.completion_config.parallel_tool_calls
                    if self.prompt.completion_config
                    else None
                )
                # Must be False when using structured output
                if has_structured_output:
                    result["parallel_tool_calls"] = False
                elif parallel_tool_calls is not None:
                    result["parallel_tool_calls"] = parallel_tool_calls

        # Add structured output if configured
        if structured_schema:
            result["response_format"] = StructuredOutputFormatter.to_openai_response_format(
                structured_schema
            )

        return result  # type: ignore

    def to_openai_responses_invocation(
        self,
        context: MessageContext | dict | None = None,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: dict[str, Any] | None = None,
    ) -> OpenAIResponsesInvocationParam:
        """Convert session to complete OpenAI Responses API invocation payload.

        Combines input items with model parameters for direct SDK usage:
            response = await openai.responses.create(
                **session.to_openai_responses_invocation()
            )

        If the prompt has tools configured, they are automatically included.
        If structured output is configured (response_schema_id), response_format is added.

        Note: When structured output is used, parallel_tool_calls is automatically
        set to False (required by OpenAI).

        Args:
            context: Optional context for variable substitution.
            model: Model override
            max_tokens: Max tokens override
            temperature: Temperature override
            top_p: Top-p override
            thinking: Thinking configuration (effort, summary)

        Returns:
            OpenAIResponsesInvocationParam ready for SDK unpacking.
        """
        messages_payload = self.to_openai_responses(context)
        model_params = self._get_model_params(
            model, max_tokens, temperature, top_p, thinking
        )
        # OpenAI Responses uses 'reasoning' - rename from 'thinking'
        if "thinking" in model_params:
            model_params["reasoning"] = model_params.pop("thinking")
        result: dict[str, Any] = {**messages_payload, **model_params}

        # Check if structured output is configured
        structured_schema = self.prompt.structured_output_schema
        has_structured_output = structured_schema is not None

        # Add tools if configured
        function_tools = self.prompt.function_tools
        if function_tools:
            tool_choice_config = (
                self.prompt.completion_config.tool_choice
                if self.prompt.completion_config
                else None
            )

            # Only add tools if tool_choice is not 'none'
            if tool_choice_config != "none":
                result["tools"] = ToolFormatter.to_openai_tools(function_tools)

                if tool_choice_config:
                    result["tool_choice"] = ToolChoiceTranslator.to_openai(
                        tool_choice_config
                    )

                # Handle parallel_tool_calls
                parallel_tool_calls = (
                    self.prompt.completion_config.parallel_tool_calls
                    if self.prompt.completion_config
                    else None
                )
                # Must be False when using structured output
                if has_structured_output:
                    result["parallel_tool_calls"] = False
                elif parallel_tool_calls is not None:
                    result["parallel_tool_calls"] = parallel_tool_calls

        # Add structured output if configured
        if structured_schema:
            result["response_format"] = StructuredOutputFormatter.to_openai_response_format(
                structured_schema
            )

        return result  # type: ignore

    def to_google_gemini_invocation(
        self,
        context: MessageContext | dict | None = None,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: dict[str, Any] | None = None,
    ) -> GoogleInvocationParam:
        """Convert session to complete Google Gemini invocation payload.

        Designed for direct SDK unpacking:
            payload = session.to_google_gemini_invocation()
            response = client.models.generate_content(**payload)

        The payload structure matches Google genai SDK's generate_content() signature:
        - model: str - the model name
        - contents: list - the conversation contents (plural)
        - config: dict - all generation config params nested here

        Args:
            context: Optional context for variable substitution.
            model: Model override (e.g., "gemini-2.5-flash")
            max_tokens: Max tokens override (becomes max_output_tokens in config)
            temperature: Temperature override
            top_p: Top-p override
            thinking: Thinking configuration (thinking_budget or thinking_level)

        Returns:
            GoogleInvocationParam ready for SDK unpacking.
        """
        # Get messages payload: {"system_instruction": ..., "content": [...]}
        messages_payload = self.to_google_gemini(context)

        # Build the config dict with all nested params
        config: dict[str, Any] = {}

        # Move system_instruction into config
        if "system_instruction" in messages_payload:
            config["system_instruction"] = messages_payload["system_instruction"]

        # Add model params to config
        model_params = self._get_model_params(
            model, max_tokens, temperature, top_p, thinking
        )
        # Rename max_tokens to max_output_tokens for Google API
        if "max_tokens" in model_params:
            config["max_output_tokens"] = model_params.pop("max_tokens")
        # Google uses 'thinking_config' - rename from 'thinking'
        if "thinking" in model_params:
            config["thinking_config"] = model_params.pop("thinking")
        # Add remaining params (temperature, top_p) to config
        for key in ["temperature", "top_p"]:
            if key in model_params:
                config[key] = model_params[key]

        # Add tools to config if configured
        function_tools = self.prompt.function_tools
        if function_tools:
            tool_choice_config = (
                self.prompt.completion_config.tool_choice
                if self.prompt.completion_config
                else None
            )

            # Only add tools if tool_choice is not 'none'
            if tool_choice_config != "none":
                # Google wraps function declarations in a tools array
                config["tools"] = [
                    {
                        "function_declarations": ToolFormatter.to_google_function_declarations(
                            function_tools
                        )
                    }
                ]

                if tool_choice_config:
                    config["tool_config"] = {
                        "function_calling_config": ToolChoiceTranslator.to_google(
                            tool_choice_config
                        )
                    }

        # Add structured output to config if configured
        structured_schema = self.prompt.structured_output_schema
        if structured_schema:
            generation_config = StructuredOutputFormatter.to_google_generation_config(
                structured_schema
            )
            # Add response_schema and response_mime_type directly to config
            if "response_schema" in generation_config:
                config["response_schema"] = generation_config["response_schema"]
            if "response_mime_type" in generation_config:
                config["response_mime_type"] = generation_config["response_mime_type"]

        # Build result with new structure:
        # - model at top level
        # - contents (plural) at top level
        # - config containing all nested params
        result: dict[str, Any] = {}

        # Add model if provided
        if "model" in model_params:
            result["model"] = model_params["model"]

        # Use 'contents' (plural) - extract from messages_payload 'content' key
        if "content" in messages_payload:
            result["contents"] = messages_payload["content"]

        # Add config if we have any config params
        if config:
            result["config"] = config

        return result  # type: ignore

    def to_google_vertex_invocation(
        self,
        context: MessageContext | dict | None = None,
        *,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: dict[str, Any] | None = None,
    ) -> GoogleInvocationParam:
        """Convert session to complete Google Vertex invocation payload.

        Designed for direct SDK unpacking:
            payload = session.to_google_vertex_invocation()
            response = client.models.generate_content(**payload)

        The payload structure matches Google genai SDK's generate_content() signature:
        - model: str - the model name
        - contents: list - the conversation contents (plural)
        - config: dict - all generation config params nested here

        Args:
            context: Optional context for variable substitution.
            model: Model override
            max_tokens: Max tokens override (becomes max_output_tokens in config)
            temperature: Temperature override
            top_p: Top-p override
            thinking: Thinking configuration (thinking_budget or thinking_level)

        Returns:
            GoogleInvocationParam ready for SDK unpacking.
        """
        # Get messages payload: {"system_instruction": ..., "content": [...]}
        messages_payload = self.to_google_vertex(context)

        # Build the config dict with all nested params
        config: dict[str, Any] = {}

        # Move system_instruction into config
        if "system_instruction" in messages_payload:
            config["system_instruction"] = messages_payload["system_instruction"]

        # Add model params to config
        model_params = self._get_model_params(
            model, max_tokens, temperature, top_p, thinking
        )
        # Rename max_tokens to max_output_tokens for Google API
        if "max_tokens" in model_params:
            config["max_output_tokens"] = model_params.pop("max_tokens")
        # Google uses 'thinking_config' - rename from 'thinking'
        if "thinking" in model_params:
            config["thinking_config"] = model_params.pop("thinking")
        # Add remaining params (temperature, top_p) to config
        for key in ["temperature", "top_p"]:
            if key in model_params:
                config[key] = model_params[key]

        # Add tools to config if configured
        function_tools = self.prompt.function_tools
        if function_tools:
            tool_choice_config = (
                self.prompt.completion_config.tool_choice
                if self.prompt.completion_config
                else None
            )

            # Only add tools if tool_choice is not 'none'
            if tool_choice_config != "none":
                # Google wraps function declarations in a tools array
                config["tools"] = [
                    {
                        "function_declarations": ToolFormatter.to_google_function_declarations(
                            function_tools
                        )
                    }
                ]

                if tool_choice_config:
                    config["tool_config"] = {
                        "function_calling_config": ToolChoiceTranslator.to_google(
                            tool_choice_config
                        )
                    }

        # Add structured output to config if configured
        structured_schema = self.prompt.structured_output_schema
        if structured_schema:
            generation_config = StructuredOutputFormatter.to_google_generation_config(
                structured_schema
            )
            # Add response_schema and response_mime_type directly to config
            if "response_schema" in generation_config:
                config["response_schema"] = generation_config["response_schema"]
            if "response_mime_type" in generation_config:
                config["response_mime_type"] = generation_config["response_mime_type"]

        # Build result with new structure:
        # - model at top level
        # - contents (plural) at top level
        # - config containing all nested params
        result: dict[str, Any] = {}

        # Add model if provided
        if "model" in model_params:
            result["model"] = model_params["model"]

        # Use 'contents' (plural) - extract from messages_payload 'content' key
        if "content" in messages_payload:
            result["contents"] = messages_payload["content"]

        # Add config if we have any config params
        if config:
            result["config"] = config

        return result  # type: ignore

    def to_invocation(
        self,
        context: MessageContext | dict | None = None,
        *,
        provider: Provider | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: dict[str, Any] | None = None,
    ) -> ProviderInvocationPayload:
        """Convert session to provider-specific invocation payload.

        Generic method that auto-selects the correct provider method based on
        completion_config.provider or explicit provider override.

        Args:
            context: Optional context for variable substitution.
            provider: Provider override (uses completion_config.provider if not specified)
            model: Model override
            max_tokens: Max tokens override
            temperature: Temperature override
            top_p: Top-p override
            thinking: Thinking/reasoning configuration override

        Returns:
            Provider-specific invocation payload ready for SDK unpacking.

        Raises:
            ValueError: If no provider available (neither in completion_config nor override)
        """
        effective_provider = provider or (
            self.prompt.completion_config.provider
            if self.prompt.completion_config
            else None
        )
        if not effective_provider:
            raise ValueError(
                "No provider specified: set completion_config.provider or pass provider="
            )

        match effective_provider:
            case Provider.ANTHROPIC:
                return self.to_anthropic_invocation(
                    context,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    thinking=thinking,
                )
            case Provider.OPENAI_CHAT:
                return self.to_openai_chat_invocation(
                    context,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    thinking=thinking,
                )
            case Provider.OPENAI_RESPONSES:
                return self.to_openai_responses_invocation(
                    context,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    thinking=thinking,
                )
            case Provider.GOOGLE_GEMINI:
                return self.to_google_gemini_invocation(
                    context,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    thinking=thinking,
                )
            case Provider.GOOGLE_VERTEX:
                return self.to_google_vertex_invocation(
                    context,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    thinking=thinking,
                )
            case _:
                raise ValueError(f"Unsupported provider: {effective_provider}")
