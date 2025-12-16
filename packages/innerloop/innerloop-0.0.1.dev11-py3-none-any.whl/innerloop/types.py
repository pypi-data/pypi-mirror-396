"""
InnerLoop v2 Types

Provider-agnostic types for messages, events, tools, and configuration.
All types are Pydantic models for validation and serialization.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Generic type variable for Response output
OutputT = TypeVar("OutputT")

# =============================================================================
# Truncation Configuration
# =============================================================================


class TruncateConfig:
    """Framework-level truncation configuration.

    Applied after tool returns, before output goes to context.
    This is the safety net - catches overflow when tool params don't limit enough.

    Attributes:
        max_bytes: Maximum output size in bytes (default: 50KB)
        max_lines: Maximum line count (default: 2000)
        strategy: When truncating, keep "head" or "tail"
        temp_file: Write full output to temp file when truncated
        line_max_chars: Truncate individual lines longer than this
    """

    __slots__ = ("max_bytes", "max_lines", "strategy", "temp_file", "line_max_chars")

    def __init__(
        self,
        max_bytes: int = 50_000,
        max_lines: int = 2000,
        strategy: Literal["head", "tail"] = "tail",
        temp_file: bool = False,
        line_max_chars: int = 2000,
    ):
        self.max_bytes = max_bytes
        self.max_lines = max_lines
        self.strategy = strategy
        self.temp_file = temp_file
        self.line_max_chars = line_max_chars


# Default config - used when truncate=True or unspecified
DEFAULT_TRUNCATE = TruncateConfig()

# =============================================================================
# Tool Context (dependency injection for tools)
# =============================================================================


@dataclass(frozen=True)
class ToolContext:
    """Context injected into tools that request it.

    Tools can receive this as a parameter to access execution context
    without coupling to global state. The parameter is NOT sent to the LLM.

    Attributes:
        workdir: Working directory for file operations (jailed).
        session_id: Current session identifier.
        model: Model string (provider/model-id).
        tool_timeout: Timeout in seconds for tool execution.
        todos: Shared todo state (mutable, for todo tools).
        temp_dir: Temporary directory for overflow files (e.g., bash output).

    Example:
        @tool
        def read_file(path: str, ctx: ToolContext) -> str:
            '''Read a file relative to workdir.'''
            full_path = ctx.workdir / path
            return full_path.read_text()
    """

    workdir: Path
    session_id: str
    model: str
    tool_timeout: float
    todos: Any = None  # TodoState, but Any to avoid circular import
    temp_dir: Path | None = None  # For overflow files (bash output, etc.)


# =============================================================================
# Content Parts (building blocks for messages)
# =============================================================================


class TextPart(BaseModel):
    """Text content in a message."""

    type: Literal["text"] = "text"
    text: str


class ToolUsePart(BaseModel):
    """Tool call in an assistant message."""

    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict[str, Any]


class ThinkingPart(BaseModel):
    """Extended thinking content (Anthropic, OpenAI reasoning)."""

    type: Literal["thinking"] = "thinking"
    text: str
    signature: str | None = None  # Anthropic cache signature


ContentPart = TextPart | ToolUsePart | ThinkingPart


# =============================================================================
# Messages
# =============================================================================


def _now() -> int:
    """Return current Unix timestamp in seconds."""
    return int(time.time())


def _now_ms() -> int:
    """Return current Unix timestamp in milliseconds."""
    return int(time.time() * 1000)


def _now_iso() -> str:
    """Return current timestamp in ISO 8601 format with milliseconds.

    Example: 2025-12-11T16:23:30.123Z
    """
    import datetime

    return (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
        + f"{int((time.time() % 1) * 1000):03d}Z"
    )


def _format_timestamp(ts: int, fmt: str) -> int | str:
    """Format a Unix timestamp according to the given format.

    Args:
        ts: Unix timestamp in seconds
        fmt: Format string (unix, unix_ms, iso8601)

    Returns:
        Formatted timestamp (int for unix/unix_ms, str for iso8601)
    """
    import datetime

    if fmt == "unix":
        return ts
    elif fmt == "unix_ms":
        return ts * 1000
    elif fmt == "iso8601":
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return ts


class UserMessage(BaseModel):
    """Message from the user."""

    role: Literal["user"] = "user"
    content: str
    timestamp: int = Field(default_factory=_now)


class AssistantMessage(BaseModel):
    """Message from the assistant (model)."""

    role: Literal["assistant"] = "assistant"
    content: list[ContentPart]
    model: str | None = None
    timestamp: int = Field(default_factory=_now)


class ToolResultMessage(BaseModel):
    """Result of a tool execution."""

    role: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    tool_name: str
    content: str
    is_error: bool = False
    timestamp: int = Field(default_factory=_now)


Message = UserMessage | AssistantMessage | ToolResultMessage


# =============================================================================
# Events (streaming)
# =============================================================================


class TextEvent(BaseModel):
    """Text chunk from streaming response."""

    type: Literal["llm.text"] = "llm.text"
    text: str


class ThinkingEvent(BaseModel):
    """Thinking chunk from streaming response."""

    type: Literal["llm.thinking"] = "llm.thinking"
    text: str


class ToolCallEvent(BaseModel):
    """Tool call detected during streaming.

    Note: input accumulates as partial JSON during streaming.
    Final input is complete JSON when tool_call_end would be emitted.
    """

    type: Literal["llm.tool_call"] = "llm.tool_call"
    id: str
    name: str
    input: str  # JSON string (may be partial during streaming)


class ToolResultEvent(BaseModel):
    """Tool execution result."""

    type: Literal["llm.tool_result"] = "llm.tool_result"
    tool_use_id: str
    tool_name: str
    content: str
    is_error: bool = False


class UsageEvent(BaseModel):
    """Token usage information."""

    type: Literal["llm.usage"] = "llm.usage"
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0


class TurnStartEvent(BaseModel):
    """Emitted at the start of each agent turn."""

    type: Literal["llm.turn_start"] = "llm.turn_start"
    turn: int


class ErrorEvent(BaseModel):
    """Error during execution."""

    type: Literal["llm.error"] = "llm.error"
    error: str
    code: str | None = None
    recoverable: bool = False


class DoneEvent(BaseModel):
    """Stream completion."""

    type: Literal["llm.done"] = "llm.done"
    stop_reason: str  # "end_turn", "tool_use", "max_tokens", "error"


class StructuredOutputEvent(BaseModel):
    """Structured output validation result (when using response_format with streaming)."""

    type: Literal["llm.structured_output"] = "llm.structured_output"
    output: Any  # The validated Pydantic model instance
    success: bool = True


class MessageEvent(BaseModel):
    """Message added to conversation history.

    Emitted by the loop when a message is added to the conversation,
    allowing callers to track and persist messages without reconstructing
    them from other events.
    """

    type: Literal["llm.message"] = "llm.message"
    message: Message


Event = (
    TextEvent
    | ThinkingEvent
    | ToolCallEvent
    | ToolResultEvent
    | UsageEvent
    | TurnStartEvent
    | ErrorEvent
    | DoneEvent
    | StructuredOutputEvent
    | MessageEvent
)


# =============================================================================
# Tool Definition
# =============================================================================


class Tool(BaseModel):
    """Base tool interface.

    Subclasses (LocalTool, MCPTool) implement execute().
    """

    name: str
    description: str
    input_schema: dict[str, Any]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_description(self) -> str:
        """Get the tool description.

        Override in subclasses to support dynamic descriptions that change
        between turns. Default implementation returns the static description.

        Dynamic descriptions are useful for tools that want to communicate
        current state to the LLM (e.g., "List todos. Current: 3 todo, 2 done").
        """
        return self.description

    async def execute(
        self, input: dict[str, Any], context: ToolContext | None = None
    ) -> tuple[str, bool]:
        """Execute the tool.

        Args:
            input: Tool input from LLM
            context: Optional execution context for tools that need it

        Returns:
            tuple of (result_string, is_error)

        Note: Returns tuple instead of raising exceptions (functional style).
        """
        raise NotImplementedError("Subclasses must implement execute()")


# =============================================================================
# Configuration
# =============================================================================


# =============================================================================
# Session Configuration
# =============================================================================


class TimestampFormat(str, Enum):
    """Timestamp format for session logs."""

    UNIX = "unix"  # Unix seconds (int) - legacy
    UNIX_MS = "unix_ms"  # Unix milliseconds (int)
    ISO8601 = "iso8601"  # ISO 8601 with ms (string) - HL compatible


class LogLevel(str, Enum):
    """What events to include in session logs."""

    MESSAGES = "messages"  # Messages only (current behavior)
    USAGE = "usage"  # Messages + usage events
    FULL = "full"  # Messages + usage + done events


class SessionConfig(BaseModel):
    """Configuration for session logging behavior.

    Controls what data is written to session JSONL files and in what format.
    These are session persistence settings, not observability logging.

    Attributes:
        log_level: What events to log (messages, usage, full)
        timestamp_format: Format for timestamp field (unix, unix_ms, iso8601)
        include_hl_fields: Add level/msg fields for HL log viewer compatibility
    """

    log_level: LogLevel = LogLevel.MESSAGES
    timestamp_format: TimestampFormat = TimestampFormat.ISO8601
    include_hl_fields: bool = True


class ThinkingLevel(str, Enum):
    """Provider-agnostic thinking levels."""

    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ThinkingConfig(BaseModel):
    """Extended thinking configuration."""

    level: ThinkingLevel = ThinkingLevel.OFF
    budget_tokens: int | None = None  # Anthropic override
    summary: str | None = None  # OpenAI override ("auto", "detailed", "concise")


class Config(BaseModel):
    """Loop execution configuration.

    Attributes:
        max_output_tokens: Maximum tokens in model response (default: 8192).
        temperature: Sampling temperature (default: None, uses provider default).
        timeout: Total loop execution timeout in seconds (default: 300.0).
        max_turns: Maximum agent loop iterations (default: 50).
        system: System prompt (default: None).
        thinking: Extended thinking configuration (default: None).
    """

    max_output_tokens: int = 8192
    temperature: float | None = None
    timeout: float = 300.0
    max_turns: int = 50
    system: str | None = None
    thinking: ThinkingConfig | None = None


# =============================================================================
# Usage Tracking
# =============================================================================


class Usage(BaseModel):
    """Aggregated token usage across turns."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0

    def add(self, other: Usage | UsageEvent) -> Usage:
        """Add usage from another source. Returns new Usage (immutable)."""
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            cache_write_tokens=self.cache_write_tokens + other.cache_write_tokens,
        )


# =============================================================================
# Tool Result (for Response)
# =============================================================================


class ToolResult(BaseModel):
    """Record of a tool execution."""

    tool_use_id: str
    tool_name: str
    input: dict[str, Any]
    output: str
    is_error: bool = False


# =============================================================================
# Response
# =============================================================================


class Response(BaseModel, Generic[OutputT]):
    """Result of a Loop.run() or Loop.arun() call.

    When `response_format` is used, `output` contains the validated Pydantic model
    and the Response is typed as Response[YourModel].
    Otherwise, `output` is the same as `text` and typed as Response[str].

    Type Parameters:
        OutputT: The type of the structured output. Defaults to str when no
                 response_format is provided.
    """

    text: str
    output: OutputT | str = ""  # Structured output (BaseModel) or text
    thinking: str | None = None
    model: str
    session_id: str
    usage: Usage = Field(default_factory=Usage)
    tool_results: list[ToolResult] = Field(default_factory=list)
    stop_reason: str = "end_turn"

    def model_post_init(self, __context: Any) -> None:
        """Set output to text if not explicitly set."""
        if self.output == "":
            object.__setattr__(self, "output", self.text)


# =============================================================================
# OTel Trace Correlation
# =============================================================================


def _get_trace_context() -> dict[str, str]:
    """Get OTel trace context if available (no hard dependency).

    Returns empty dict if OTel is not installed or no active span.
    This enables correlation between session logs and OTel/Logfire/Weave traces.
    """
    try:
        from opentelemetry.trace import (  # type: ignore[import-not-found]
            get_current_span,
        )

        span = get_current_span()
        ctx = span.get_span_context()
        if ctx and ctx.is_valid:
            return {
                "trace_id": f"{ctx.trace_id:032x}",
                "span_id": f"{ctx.span_id:016x}",
            }
    except ImportError:
        pass
    except Exception:
        # Don't fail on any OTel errors
        pass
    return {}


# =============================================================================
# Serialization
# =============================================================================


def _message_summary(msg: Message) -> str:
    """Generate a human-readable summary for HL log viewer.

    Examples:
        user: What is 2+2?
        assistant: [text]
        assistant: [tool_call: bash]
        tool_result: bash (error)
    """
    if isinstance(msg, UserMessage):
        # Truncate long content
        content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
        return f"user: {content}"
    elif isinstance(msg, AssistantMessage):
        # Summarize content parts
        parts = []
        for p in msg.content:
            if isinstance(p, TextPart):
                parts.append("text")
            elif isinstance(p, ToolUsePart):
                parts.append(f"tool_call: {p.name}")
            elif isinstance(p, ThinkingPart):
                parts.append("thinking")
        return f"assistant: [{', '.join(parts) or 'empty'}]"
    else:  # ToolResultMessage
        suffix = " (error)" if msg.is_error else ""
        return f"tool_result: {msg.tool_name}{suffix}"


def message_to_dict(
    msg: Message,
    include_hl_fields: bool = True,
    timestamp_format: str = "iso8601",
    include_trace_context: bool = True,
) -> dict[str, Any]:
    """Convert a Message to a JSON-serializable dict.

    Args:
        msg: Message to convert
        include_hl_fields: Add level/msg fields for HL log viewer compatibility
        timestamp_format: Timestamp format (unix, unix_ms, iso8601)
        include_trace_context: Add OTel trace_id/span_id if available
    """
    # Determine level for HL compatibility
    level = "info"
    if isinstance(msg, ToolResultMessage) and msg.is_error:
        level = "error"

    # Format timestamp based on config
    # Use "ts" for ISO8601 (HL-compatible), "timestamp" for unix formats
    ts_value = _format_timestamp(msg.timestamp, timestamp_format)
    ts_key = "ts" if timestamp_format == "iso8601" else "timestamp"

    if isinstance(msg, UserMessage):
        base: dict[str, Any] = {
            "role": "user",
            "content": msg.content,
            ts_key: ts_value,
        }
    elif isinstance(msg, AssistantMessage):
        base = {
            "role": "assistant",
            "content": [_part_to_dict(p) for p in msg.content],
            "model": msg.model,
            ts_key: ts_value,
        }
    elif isinstance(msg, ToolResultMessage):
        base = {
            "role": "tool_result",
            "tool_use_id": msg.tool_use_id,
            "tool_name": msg.tool_name,
            "content": msg.content,
            "is_error": msg.is_error,
            ts_key: ts_value,
        }
    else:
        raise ValueError(f"Unknown message type: {type(msg)}")

    # Add HL-compatible fields if requested
    if include_hl_fields:
        base["level"] = level
        base["msg"] = _message_summary(msg)

    # Add OTel trace context if available and requested
    if include_trace_context:
        trace_ctx = _get_trace_context()
        if trace_ctx:
            base.update(trace_ctx)

    return base


def _part_to_dict(part: ContentPart) -> dict[str, Any]:
    """Convert a ContentPart to a dict."""
    if isinstance(part, TextPart):
        return {"type": "text", "text": part.text}
    elif isinstance(part, ToolUsePart):
        return {
            "type": "tool_use",
            "id": part.id,
            "name": part.name,
            "input": part.input,
        }
    elif isinstance(part, ThinkingPart):
        d = {"type": "thinking", "text": part.text}
        if part.signature:
            d["signature"] = part.signature
        return d
    else:
        raise ValueError(f"Unknown part type: {type(part)}")


def _parse_timestamp(data: dict[str, Any]) -> int | None:
    """Extract timestamp from dict, handling both old and new formats.

    Supports:
    - "timestamp" (int): Unix seconds (legacy)
    - "ts" (str): ISO 8601 format (new)
    - "ts" (int): Unix milliseconds
    """
    import datetime

    # Try legacy "timestamp" field first
    if "timestamp" in data and data["timestamp"] is not None:
        return int(data["timestamp"])

    # Try new "ts" field
    if "ts" in data and data["ts"] is not None:
        ts = data["ts"]
        if isinstance(ts, str):
            # ISO 8601 format - parse to Unix seconds
            try:
                dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                return int(dt.timestamp())
            except ValueError:
                return None
        elif isinstance(ts, int):
            # Unix milliseconds - convert to seconds
            return ts // 1000 if ts > 1_000_000_000_000 else ts

    return None


def dict_to_message(data: dict[str, Any]) -> Message:
    """Convert a dict back to a Message.

    Handles both legacy format (timestamp field) and new format (ts field).
    """
    role = data.get("role")
    ts = _parse_timestamp(data)

    if role == "user":
        kwargs: dict[str, Any] = {"content": data["content"]}
        if ts is not None:
            kwargs["timestamp"] = ts
        return UserMessage(**kwargs)
    elif role == "assistant":
        content = [_dict_to_part(p) for p in data.get("content", [])]
        kwargs = {"content": content, "model": data.get("model")}
        if ts is not None:
            kwargs["timestamp"] = ts
        return AssistantMessage(**kwargs)
    elif role == "tool_result":
        kwargs = {
            "tool_use_id": data["tool_use_id"],
            "tool_name": data["tool_name"],
            "content": data["content"],
            "is_error": data.get("is_error", False),
        }
        if ts is not None:
            kwargs["timestamp"] = ts
        return ToolResultMessage(**kwargs)
    else:
        raise ValueError(f"Unknown role: {role}")


def _dict_to_part(data: dict[str, Any]) -> ContentPart:
    """Convert a dict back to a ContentPart."""
    part_type = data.get("type")

    if part_type == "text":
        return TextPart(text=data["text"])
    elif part_type == "tool_use":
        return ToolUsePart(
            id=data["id"],
            name=data["name"],
            input=data["input"],
        )
    elif part_type == "thinking":
        return ThinkingPart(
            text=data["text"],
            signature=data.get("signature"),
        )
    else:
        raise ValueError(f"Unknown part type: {part_type}")


__all__ = [
    # Truncation
    "TruncateConfig",
    "DEFAULT_TRUNCATE",
    # Tool context
    "ToolContext",
    # Content parts
    "TextPart",
    "ToolUsePart",
    "ThinkingPart",
    "ContentPart",
    # Messages
    "UserMessage",
    "AssistantMessage",
    "ToolResultMessage",
    "Message",
    # Events
    "TextEvent",
    "ThinkingEvent",
    "ToolCallEvent",
    "ToolResultEvent",
    "UsageEvent",
    "TurnStartEvent",
    "ErrorEvent",
    "DoneEvent",
    "StructuredOutputEvent",
    "Event",
    # Tool
    "Tool",
    "ToolResult",
    # Config
    "TimestampFormat",
    "LogLevel",
    "SessionConfig",
    "ThinkingLevel",
    "ThinkingConfig",
    "Config",
    # Usage & Response
    "Usage",
    "Response",
    "OutputT",
    # Serialization
    "message_to_dict",
    "dict_to_message",
]
