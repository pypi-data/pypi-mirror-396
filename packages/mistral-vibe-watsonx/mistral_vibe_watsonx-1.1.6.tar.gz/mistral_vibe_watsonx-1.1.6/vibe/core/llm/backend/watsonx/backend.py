"""WatsonX Backend Adapter with Prompt-Based Tool Emulation.

This backend emulates the Mistral Vibe BackendLike interface while using WatsonX's
standard chat/generate endpoints. It compensates for WatsonX vLLM's lack of native
tool calling support by:

1. Embedding tool schemas in the system prompt
2. Parsing JSON tool calls from model responses
3. Handling reasoning_content (thinking) field quirks
4. Using tenacity for intelligent retry on malformed responses

The adapter makes WatsonX appear to support native tool calling while actually
using prompt engineering behind the scenes.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
import json
import logging
import os
import re
import types
from typing import TYPE_CHECKING, Any
import uuid

logger = logging.getLogger(__name__)

import httpx
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from vibe.core.llm.backend.watsonx.auth import WatsonXAuth, WatsonXAuthError
from vibe.core.llm.exceptions import BackendErrorBuilder
from vibe.core.types import (
    AvailableTool,
    FunctionCall,
    LLMChunk,
    LLMMessage,
    LLMUsage,
    Role,
    StrToolChoice,
    ToolCall,
)

if TYPE_CHECKING:
    from vibe.core.config import ModelConfig, ProviderConfig


class WatsonXBackendError(Exception):
    """Raised when WatsonX backend encounters an error."""

    def __init__(
        self, message: str, *, cause: Exception | None = None, retryable: bool = False
    ) -> None:
        super().__init__(message)
        self.cause = cause
        self.retryable = retryable


class ToolParsingError(WatsonXBackendError):
    """Raised when tool call JSON parsing fails - triggers retry with guidance."""

    def __init__(self, message: str, raw_response: str) -> None:
        super().__init__(message, retryable=True)
        self.raw_response = raw_response


class EmptyResponseError(WatsonXBackendError):
    """Raised when WatsonX returns empty content - triggers retry."""

    def __init__(self, finish_reason: str) -> None:
        super().__init__(
            f"WatsonX returned empty response with finish_reason={finish_reason}",
            retryable=True,
        )
        self.finish_reason = finish_reason


# WatsonX API configuration
WATSONX_API_VERSION = "2024-05-31"
DEFAULT_MAX_TOKENS = 8192
DEFAULT_TIMEOUT = 300.0  # 5 minutes

# HTTP status codes for retry logic
HTTP_SERVER_ERROR_MIN = 500
HTTP_SERVER_ERROR_MAX = 600


def _build_tool_schemas_prompt(tools: list[AvailableTool]) -> str:
    """Build tool schemas section for system prompt injection."""
    if not tools:
        return ""

    tool_schemas = "\n\n<tools>\n"
    for tool in tools:
        tool_dict = {
            "type": "function",
            "function": {
                "name": tool.function.name,
                "description": tool.function.description,
                "parameters": tool.function.parameters,
            },
        }
        tool_schemas += f"{json.dumps(tool_dict, indent=2)}\n\n"
    tool_schemas += "</tools>\n"
    return tool_schemas


def _build_tool_instructions() -> str:
    """Build tool calling instructions for system prompt injection.

    These instructions guide the model to output properly formatted JSON
    tool calls that we can parse.
    """
    backtick = "```"
    return f"""
# Tool Calling Instructions

When you need to use a tool, respond with ONLY a JSON object wrapped in markdown code fences.

Your response must follow this EXACT format when calling a tool:

{backtick}json
{{
  "name": "tool_name",
  "input": {{
    "parameter1": "value1",
    "parameter2": "value2"
  }}
}}
{backtick}

## CRITICAL RULES

1. **JSON Format Only**: When calling a tool, output ONLY the JSON block - no explanations before or after
2. **Exact Parameter Names**: Use the exact parameter names from the tool schema
3. **Proper Escaping**: For code content, escape special characters (\\n for newlines, \\" for quotes)
4. **Copy Code Verbatim**: When user provides code, include it EXACTLY in your tool call - never paraphrase
5. **One Tool Per Response**: Call only one tool at a time

## Examples

**Reading a file:**
{backtick}json
{{
  "name": "read_file",
  "input": {{
    "path": "src/main.py"
  }}
}}
{backtick}

**Writing content:**
{backtick}json
{{
  "name": "write_file",
  "input": {{
    "path": "test.py",
    "content": "def hello():\\n    print(\\"Hello\\")"
  }}
}}
{backtick}

## When NOT Calling Tools

If you're providing information, answering questions, or don't need a tool, respond normally without JSON code blocks.
"""


def _extract_json_with_brace_counting(content: str) -> str | None:
    """Extract JSON object from content using brace counting."""
    start_idx = content.find("{")
    if start_idx < 0:
        return None

    brace_count = 0
    for i, char in enumerate(content[start_idx:], start=start_idx):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                return content[start_idx : i + 1]
    return None


def _extract_tool_call_from_response(content: str) -> tuple[str, list[ToolCall]]:
    """Extract tool call JSON from model response.

    Looks for ```json ... ``` blocks and parses them as tool calls.
    Returns cleaned content and list of tool calls (0 or 1).
    """
    tool_calls: list[ToolCall] = []

    # Try markdown-wrapped JSON first (greedy to capture nested braces)
    json_match = re.search(r"```json\s*(\{.*\})\s*```", content, re.DOTALL)
    json_str = json_match.group(1) if json_match else _extract_json_with_brace_counting(content)

    if not json_str:
        return content, tool_calls

    try:
        tool_call_json = json.loads(json_str)
        tool_name = tool_call_json.get("name")
        tool_input = tool_call_json.get("input", {})

        if tool_name:
            tool_call = ToolCall(
                id=f"call_{uuid.uuid4().hex[:24]}",
                function=FunctionCall(
                    name=tool_name,
                    arguments=json.dumps(tool_input),
                ),
                index=0,  # Required for streaming handler compatibility
            )
            tool_calls.append(tool_call)

            # Clean the JSON block from content
            content = re.sub(
                r"```json\s*\{.*\}\s*```", "", content, flags=re.DOTALL
            ).strip()

    except json.JSONDecodeError as e:
        raise ToolParsingError(
            f"Failed to parse tool call JSON: {e}",
            raw_response=content,
        )

    return content, tool_calls


def _separate_content_and_reasoning(
    message: dict[str, Any], finish_reason: str
) -> tuple[str, str | None]:
    """Separate content and reasoning fields from WatsonX message.

    WatsonX may return:
    - content: The actual response text
    - reasoning_content: The model's reasoning/thought process (if present)

    Handles various edge cases where one or both may be empty/None.
    """
    content = message.get("content") or ""
    reasoning_content = message.get("reasoning_content") or ""

    # Both present: content is answer, reasoning_content is thought process
    if content and reasoning_content:
        return content, reasoning_content

    # Only content present
    if content:
        return content, None

    # Only reasoning present - use as main response
    if reasoning_content:
        return reasoning_content, None

    # Neither present - handle based on finish reason
    if finish_reason == "length":
        return "[Response truncated: Token limit reached]", None

    if finish_reason == "stop":
        raise EmptyResponseError(finish_reason)

    return f"[Empty response with finish_reason={finish_reason}]", None


class WatsonXBackend:
    """WatsonX backend adapter implementing BackendLike protocol.

    Emulates native tool calling through prompt engineering while using
    WatsonX's standard chat endpoint.
    """

    def __init__(
        self,
        *,
        provider: ProviderConfig,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize WatsonX backend.

        Args:
            provider: Provider configuration with api_base and api_key_env_var
            timeout: Request timeout in seconds
        """
        self._provider = provider
        self._timeout = timeout

        # Extract configuration from environment
        self._api_key = os.getenv(provider.api_key_env_var) if provider.api_key_env_var else None
        self._project_id = os.getenv("WATSONX_PROJECT_ID", "")
        self._region = os.getenv("WATSONX_REGION", "us-south")
        # Allow direct endpoint override via WATSONX_ENDPOINT for custom deployments
        self._custom_endpoint = os.getenv("WATSONX_ENDPOINT", "")

        # Will be initialized in __aenter__
        self._auth: WatsonXAuth | None = None
        self._client: httpx.AsyncClient | None = None

    @property
    def base_url(self) -> str:
        """Get WatsonX API base URL.

        Priority order:
        1. WATSONX_ENDPOINT env var (for custom deployments)
        2. Provider config api_base (if contains ml.cloud.ibm.com)
        3. Region-based URL from WATSONX_REGION env var
        """
        # Custom endpoint takes highest priority
        if self._custom_endpoint:
            return self._custom_endpoint.rstrip("/")
        # Allow override via provider config
        if self._provider.api_base and "ml.cloud.ibm.com" in self._provider.api_base:
            return self._provider.api_base.rstrip("/")
        # Default: construct from region
        return f"https://{self._region}.ml.cloud.ibm.com"

    async def __aenter__(self) -> WatsonXBackend:
        """Initialize auth and HTTP client."""
        if not self._api_key:
            raise WatsonXBackendError(
                f"Missing API key: set {self._provider.api_key_env_var} environment variable"
            )

        if not self._project_id:
            raise WatsonXBackendError(
                "Missing project ID: set WATSONX_PROJECT_ID environment variable"
            )

        self._auth = WatsonXAuth(self._api_key)
        await self._auth.__aenter__()

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=self._auth,
            timeout=httpx.Timeout(self._timeout),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Clean up resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

        if self._auth:
            await self._auth.__aexit__(exc_type, exc_val, exc_tb)
            self._auth = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client, creating if needed."""
        if self._client is None:
            raise WatsonXBackendError(
                "WatsonXBackend not initialized. Use 'async with' context manager."
            )
        return self._client

    def _build_request_body(
        self,
        *,
        model_name: str,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int | None,
        has_tools: bool,
    ) -> dict[str, Any]:
        """Build WatsonX chat request body."""
        return {
            "model_id": model_name,
            "messages": messages,
            "max_tokens": max_tokens or DEFAULT_MAX_TOKENS,
            "parameters": {
                "temperature": 0.0 if has_tools else temperature,  # Deterministic for tool calls
                "top_p": 1.0,
                "top_k": 50,
            },
            "project_id": self._project_id,
        }

    def _prepare_messages_with_tools(
        self,
        messages: list[LLMMessage],
        tools: list[AvailableTool] | None,
    ) -> list[dict[str, Any]]:
        """Prepare messages, injecting tool schemas into system prompt if needed."""
        converted: list[dict[str, Any]] = []
        tool_injection_done = False

        logger.info(
            f"WatsonX _prepare_messages_with_tools: {len(messages)} messages, "
            f"{len(tools) if tools else 0} tools provided"
        )

        for msg in messages:
            msg_dict: dict[str, Any] = {"role": msg.role.value, "content": msg.content or ""}

            # Inject tool schemas into system prompt
            # Put CRITICAL format instruction at the START for maximum visibility
            if msg.role == Role.system and tools:
                tool_schemas = _build_tool_schemas_prompt(tools)
                tool_instructions = _build_tool_instructions()
                # Critical instruction at START, schemas and details at END
                critical_prefix = (
                    "CRITICAL: When you need to use a tool, you MUST respond with ONLY "
                    "a JSON code block in this exact format:\n"
                    "```json\n"
                    '{"name": "tool_name", "input": {"param": "value"}}\n'
                    "```\n"
                    "Do NOT explain what you will do. Just output the JSON.\n\n"
                )
                msg_dict["content"] = f"{critical_prefix}{msg.content}\n\n{tool_schemas}\n{tool_instructions}"
                tool_injection_done = True
                logger.info(
                    f"WatsonX: Injected {len(tools)} tool schemas into system prompt "
                    f"(total content length: {len(msg_dict['content'])} chars)"
                )

            # Add tool reminder to user messages to reinforce the format
            if msg.role == Role.user and tools and tool_injection_done:
                reminder = (
                    "\n\n[IMPORTANT: If you need to use a tool, respond with ONLY "
                    "a ```json code block containing {\"name\": \"tool_name\", \"input\": {...}}. "
                    "Do not explain - just output the JSON.]"
                )
                msg_dict["content"] = f"{msg.content}{reminder}"

            # Handle tool role messages
            if msg.role == Role.tool:
                msg_dict["tool_call_id"] = msg.tool_call_id
                if msg.name:
                    msg_dict["name"] = msg.name

            converted.append(msg_dict)

        if tools and not tool_injection_done:
            logger.warning(
                f"WatsonX: Tools provided ({len(tools)}) but no system message found! "
                f"Message roles: {[m.role.value for m in messages]}"
            )

        return converted

    def _parse_response(self, data: dict[str, Any]) -> tuple[str, str | None, LLMUsage, str]:
        """Parse WatsonX response into components.

        Returns:
            Tuple of (content, reasoning, usage, finish_reason)
        """
        if "choices" not in data or not data["choices"]:
            raise WatsonXBackendError("Invalid response: missing choices")

        choice = data["choices"][0]
        message = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "stop")

        # Separate content and reasoning
        content, reasoning = _separate_content_and_reasoning(message, finish_reason)

        # Extract usage
        usage_data = data.get("usage", {})
        usage = LLMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
        )

        return content, reasoning, usage, finish_reason

    async def _make_request_with_retry(
        self,
        *,
        model_name: str,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int | None,
        has_tools: bool,
    ) -> dict[str, Any]:
        """Make WatsonX API request with retry logic.

        Retries on 5xx errors and timeouts with exponential backoff.
        """
        client = self._get_client()

        request_body = self._build_request_body(
            model_name=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            has_tools=has_tools,
        )

        headers = {
            "Content-Type": "application/json",
            "X-Project-Id": self._project_id,
        }

        url = f"/ml/v1/text/chat?version={WATSONX_API_VERSION}"

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(5),
                wait=wait_exponential(multiplier=2, min=5, max=60),
                retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
                reraise=True,
            ):
                with attempt:
                    response = await client.post(url, json=request_body, headers=headers)

                    # Retry on 5xx errors
                    if HTTP_SERVER_ERROR_MIN <= response.status_code < HTTP_SERVER_ERROR_MAX:
                        response.raise_for_status()

                    response.raise_for_status()
                    return response.json()

        except RetryError:
            raise
        except httpx.HTTPStatusError as e:
            raise WatsonXBackendError(
                f"WatsonX API error {e.response.status_code}: {e.response.text[:500]}",
                cause=e,
            ) from e
        except httpx.TimeoutException as e:
            raise WatsonXBackendError(
                f"WatsonX request timed out after {self._timeout}s",
                cause=e,
            ) from e

        # Should not reach here, but satisfy type checker
        raise WatsonXBackendError("Request failed after all retries")

    async def _execute_completion(
        self,
        *,
        model_name: str,
        converted_messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int | None,
        has_tools: bool,
    ) -> LLMChunk:
        """Execute a single completion attempt with tool extraction."""
        response_data = await self._make_request_with_retry(
            model_name=model_name,
            messages=converted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            has_tools=has_tools,
        )

        content, _reasoning, usage, finish_reason = self._parse_response(response_data)

        logger.info(
            f"WatsonX response: finish_reason={finish_reason}, "
            f"content_length={len(content)}, has_tools={has_tools}"
        )
        logger.info(f"WatsonX raw content (first 500 chars): {content[:500]}")

        # Extract tool calls if we have tools
        tool_calls: list[ToolCall] | None = None
        if has_tools:
            content, extracted_tools = _extract_tool_call_from_response(content)
            if extracted_tools:
                tool_calls = extracted_tools
                finish_reason = "tool_calls"
                logger.info(
                    f"WatsonX: Extracted tool call: {extracted_tools[0].function.name}"
                )
            else:
                logger.info("WatsonX: No tool call found in response")

        return LLMChunk(
            message=LLMMessage(
                role=Role.assistant,
                content=content,
                tool_calls=tool_calls,
            ),
            usage=usage,
            finish_reason=finish_reason,
        )

    async def complete(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        tools: list[AvailableTool] | None = None,
        max_tokens: int | None = None,
        tool_choice: StrToolChoice | AvailableTool | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> LLMChunk:
        """Complete a chat conversation with optional tool calling.

        If tools are provided, they are injected into the system prompt and
        the model's response is parsed for JSON tool calls.
        """
        has_tools = bool(tools)
        converted_messages = self._prepare_messages_with_tools(messages, tools)

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                retry=retry_if_exception_type((EmptyResponseError, ToolParsingError)),
                reraise=True,
            ):
                with attempt:
                    return await self._execute_completion(
                        model_name=model.name,
                        converted_messages=converted_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        has_tools=has_tools,
                    )

        except RetryError as e:
            last_error = e.last_attempt.exception() if e.last_attempt else e
            raise WatsonXBackendError(
                f"Failed after retries: {last_error}",
                cause=last_error if isinstance(last_error, Exception) else None,
            ) from e
        except (WatsonXBackendError, WatsonXAuthError):
            raise
        except httpx.HTTPStatusError as e:
            raise BackendErrorBuilder.build_http_error(
                provider=self._provider.name,
                endpoint=self.base_url,
                response=e.response,
                headers=dict(e.response.headers.items()),
                model=model.name,
                messages=messages,
                temperature=temperature,
                has_tools=has_tools,
                tool_choice=tool_choice,
            ) from e
        except httpx.RequestError as e:
            raise BackendErrorBuilder.build_request_error(
                provider=self._provider.name,
                endpoint=self.base_url,
                error=e,
                model=model.name,
                messages=messages,
                temperature=temperature,
                has_tools=has_tools,
                tool_choice=tool_choice,
            ) from e

        # Unreachable - all code paths above either return or raise
        raise WatsonXBackendError("Completion failed unexpectedly")

    async def complete_streaming(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float = 0.2,
        tools: list[AvailableTool] | None = None,
        max_tokens: int | None = None,
        tool_choice: StrToolChoice | AvailableTool | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> AsyncGenerator[LLMChunk, None]:
        """Streaming completion - falls back to non-streaming for WatsonX.

        WatsonX streaming with tool emulation is complex, so we emit
        the complete response as a single chunk.
        """
        result = await self.complete(
            model=model,
            messages=messages,
            temperature=temperature,
            tools=tools,
            max_tokens=max_tokens,
            tool_choice=tool_choice,
            extra_headers=extra_headers,
        )
        yield result

    async def count_tokens(
        self,
        *,
        model: ModelConfig,
        messages: list[LLMMessage],
        temperature: float = 0.0,
        tools: list[AvailableTool] | None = None,
        tool_choice: StrToolChoice | AvailableTool | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> int:
        """Count tokens by making a minimal completion request.

        WatsonX doesn't have a dedicated token counting endpoint,
        so we use a completion with minimal output.
        """
        # Add a user message if needed to ensure valid request
        probe_messages = list(messages)
        if not probe_messages or probe_messages[-1].role != Role.user:
            probe_messages.append(LLMMessage(role=Role.user, content=""))

        result = await self.complete(
            model=model,
            messages=probe_messages,
            temperature=temperature,
            tools=tools,
            max_tokens=16,  # Minimal
            tool_choice=tool_choice,
            extra_headers=extra_headers,
        )

        if result.usage is None:
            return 0

        return result.usage.prompt_tokens

    async def close(self) -> None:
        """Close the backend and release resources."""
        if self._client:
            await self._client.aclose()
            self._client = None

        if self._auth:
            await self._auth.__aexit__(None, None, None)
            self._auth = None