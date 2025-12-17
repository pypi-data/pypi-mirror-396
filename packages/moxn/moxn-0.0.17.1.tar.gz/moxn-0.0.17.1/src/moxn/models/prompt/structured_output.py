"""Structured output formatting utilities for converting schemas to provider-specific formats.

This module provides formatters for converting SdkSchema to provider-specific
structured output / response format configurations.

Provider Translation Reference:

| Provider   | Response Format                                                              | Notes                                              |
|------------|------------------------------------------------------------------------------|----------------------------------------------------|
| OpenAI     | response_format: {type: 'json_schema', json_schema: {name, schema, strict}}  | Requires parallel_tool_calls: false                |
| Anthropic  | output_format: {type: 'json_schema', schema}                                 | Requires anthropic-beta: structured-outputs header |
| Google     | generation_config: {response_mime_type: 'application/json', response_schema} |                                                    |
"""

from __future__ import annotations

import json
from typing import Any

from moxn.types.tool import SdkSchema


class StructuredOutputFormatter:
    """Converts SdkSchema to provider-specific structured output formats."""

    @staticmethod
    def to_openai_response_format(schema: SdkSchema) -> dict[str, Any]:
        """Build OpenAI response_format with json_schema.

        OpenAI format:
        {
            "type": "json_schema",
            "json_schema": {
                "name": "schema_name",
                "schema": { ... JSON Schema ... },
                "strict": true
            }
        }

        Note: When using this, parallel_tool_calls must be set to false.

        Args:
            schema: SdkSchema containing the JSON Schema

        Returns:
            OpenAI response_format configuration
        """
        return {
            "type": "json_schema",
            "json_schema": {
                "name": schema.name,
                "schema": json.loads(schema.exported_json),
                "strict": True,
            },
        }

    @staticmethod
    def to_anthropic_output_format(schema: SdkSchema) -> dict[str, Any]:
        """Build Anthropic output_format for structured outputs.

        Anthropic format:
        {
            "type": "json_schema",
            "schema": { ... JSON Schema ... }
        }

        Note: This requires the beta header:
            extra_headers={"anthropic-beta": "structured-outputs-2025-11-13"}

        Args:
            schema: SdkSchema containing the JSON Schema

        Returns:
            Anthropic output_format configuration
        """
        return {
            "type": "json_schema",
            "schema": json.loads(schema.exported_json),
        }

    @staticmethod
    def to_google_generation_config(schema: SdkSchema) -> dict[str, Any]:
        """Build Google generation_config for structured output.

        Google format (partial generation_config):
        {
            "response_mime_type": "application/json",
            "response_schema": { ... JSON Schema ... }
        }

        Note: This should be merged with other generation_config parameters.

        Args:
            schema: SdkSchema containing the JSON Schema

        Returns:
            Google generation_config parameters for structured output
        """
        return {
            "response_mime_type": "application/json",
            "response_schema": json.loads(schema.exported_json),
        }
