"""
Loop API

Public interface for InnerLoop.
Provides sync and async methods for running agent loops.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import contextlib
import json
import shutil
import tempfile
from collections.abc import AsyncIterator, Coroutine, Generator, Iterator
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Any, TypeVar, cast, overload

from .loop import execute as loop_execute
from .loop import stream as loop_stream
from .providers import get_provider
from .schema import validate as schema_validate
from .session import SessionStore
from .structured import ResponseTool
from .tooling.todo import TodoState, rehydrate_from_session
from .types import (
    Config,
    DoneEvent,
    Event,
    Message,
    MessageEvent,
    Response,
    StructuredOutputEvent,
    TextEvent,
    ThinkingConfig,
    ThinkingEvent,
    ThinkingLevel,
    Tool,
    ToolCallEvent,
    ToolContext,
    ToolResultEvent,
    UsageEvent,
    UserMessage,
)

T = TypeVar("T")


def _run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run a coroutine synchronously, handling nested event loops.

    If called from within an existing event loop (e.g., Jupyter notebook,
    async web framework), runs the coroutine in a thread pool executor
    with its own event loop. Otherwise, uses asyncio.run() directly.

    Args:
        coro: The coroutine to execute

    Returns:
        The result of the coroutine
    """
    try:
        asyncio.get_running_loop()
        # Inside an event loop - run in a thread with its own loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running loop - use asyncio.run directly
        return asyncio.run(coro)


class Loop:
    """
    Agent loop with session management.

    Examples:
        # Simple usage
        loop = Loop(model="anthropic/claude-sonnet-4")
        response = loop.run("Hello!")

        # With tools
        @tool
        def get_weather(city: str) -> str:
            return f"Weather in {city}: 72°F"

        loop = Loop(
            model="anthropic/claude-sonnet-4",
            tools=[get_weather],
        )
        response = loop.run("What's the weather in NYC?")

        # Streaming
        for event in loop.stream("Tell me a story"):
            if isinstance(event, TextEvent):
                print(event.text, end="", flush=True)
    """

    def __init__(
        self,
        model: str,
        tools: list[Tool] | None = None,
        thinking: ThinkingLevel | ThinkingConfig | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        system: str | None = None,
        workdir: Path | str | None = None,
        session: str | None = None,
        tool_timeout: float | None = None,
        timeout: float = 300.0,
    ):
        """
        Initialize a Loop.

        Args:
            model: Model string (e.g., "anthropic/claude-sonnet-4").
            tools: List of tools (functions decorated with @tool).
                   Default: [] (no tools).
                   If todo tools are included, state is auto-managed and
                   accessible via loop.todos after execution.
            thinking: Thinking level or config (optional).
            api_key: Explicit API key (optional, uses env var otherwise).
            base_url: Custom base URL (optional, for local models).
            system: System prompt (optional).
            workdir: Working directory for tools (default: current directory).
            session: Session ID to resume (from a previous response.session_id).
                     If None, creates a new session with auto-generated ID.
                     If todo tools are present, state is auto-rehydrated.
            tool_timeout: Timeout in seconds for tool execution.
                         Default: None (auto-computed as 80% of timeout).
            timeout: Total loop execution timeout in seconds (default: 300.0).
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        # Compute tool_timeout: default to 80% of loop timeout, cap at 80%
        if tool_timeout is None:
            self.tool_timeout = timeout * 0.8
        else:
            # Cap tool_timeout at 80% of loop timeout
            self.tool_timeout = min(tool_timeout, timeout * 0.8)

        # Set up working directory
        self.workdir = Path(workdir).resolve() if workdir else Path.cwd()

        # Tools (default to empty list)
        self.tools: list[Tool] = list(tools) if tools else []

        # Configure thinking
        if isinstance(thinking, ThinkingLevel):
            self.thinking: ThinkingConfig | None = ThinkingConfig(level=thinking)
        else:
            self.thinking = thinking

        # System prompt
        self.system = system

        # Session management
        self._store = SessionStore()
        if session:
            self.session_id = session
            self.messages = self._store.load(session)
        else:
            self.session_id = self._store.new_session_id()
            self.messages = []

        # Detect todo tools by name and create state if present
        # State is passed to tools via ToolContext.todos
        has_todo_tools = any(getattr(t, "name", None) == "add_todo" for t in self.tools)
        if has_todo_tools:
            if session:
                # Resuming session: rehydrate state from session history
                self.todos: TodoState | None = rehydrate_from_session(self.messages)
            else:
                # Fresh session: start with empty state
                self.todos = TodoState()
        else:
            self.todos = None

        # Get provider
        self._provider = get_provider(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
        )

        # Temp directory for overflow files (lazily created)
        self._temp_dir: Path | None = None

    @property
    def temp_dir(self) -> Path:
        """Lazily create temp directory for overflow files (e.g., bash output)."""
        if self._temp_dir is None:
            self._temp_dir = Path(tempfile.mkdtemp(prefix="innerloop-"))
        return self._temp_dir

    def cleanup(self) -> None:
        """Clean up temp directory. Call when done with the Loop."""
        if self._temp_dir and self._temp_dir.exists():
            shutil.rmtree(self._temp_dir)
            self._temp_dir = None

    def __enter__(self) -> Loop:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit - cleanup temp directory."""
        self.cleanup()

    def _build_config(self, **overrides: Any) -> Config:
        """Build config with thinking and system prompt."""
        config = Config(
            system=self.system,
            thinking=self.thinking,
            **overrides,
        )
        return config

    def _make_config(
        self,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
    ) -> Config:
        """Build config from optional parameters, filtering None values."""
        kwargs: dict[str, Any] = {}
        if max_output_tokens is not None:
            kwargs["max_output_tokens"] = max_output_tokens
        if temperature is not None:
            kwargs["temperature"] = temperature
        if timeout is not None:
            kwargs["timeout"] = timeout
        if max_turns is not None:
            kwargs["max_turns"] = max_turns
        return self._build_config(**kwargs)

    def _save_message(self, message: Message) -> None:
        """Save a message to the session."""
        self._store.append(
            self.session_id, message, model=self.model, workdir=self.workdir
        )

    @overload
    async def arun(
        self,
        prompt: str,
        response_format: None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Response[str]: ...

    @overload
    async def arun(
        self,
        prompt: str,
        response_format: type[T],
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Response[T]: ...

    async def arun(
        self,
        prompt: str,
        response_format: type[T] | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Response[T] | Response[str]:
        """
        Run a prompt asynchronously.

        Args:
            prompt: User prompt.
            response_format: Pydantic model class for structured output (optional).
                            When provided, forces the model to call a 'respond' tool
                            and validates the output against this schema.
            max_output_tokens: Maximum tokens in response (default: 8192).
            temperature: Sampling temperature (optional).
            timeout: Total loop timeout in seconds (default: 300.0).
            max_turns: Maximum agent loop iterations (default: 50).
            validation_retries: Max validation retry attempts for structured output.

        Returns:
            Response object. If response_format is provided, response.output
            contains the validated Pydantic model instance.
        """
        # Handle structured output via response_format
        if response_format is not None:
            return await self._arun_structured(
                prompt=prompt,
                output_type=response_format,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                timeout=timeout,
                max_turns=max_turns,
                validation_retries=validation_retries,
            )

        # Add user message
        user_msg = UserMessage(content=prompt)
        self.messages.append(user_msg)
        self._save_message(user_msg)

        # Build config
        config = self._make_config(max_output_tokens, temperature, timeout, max_turns)

        # Create tool context (with todos if todo tools are present)
        tool_context = ToolContext(
            workdir=self.workdir,
            session_id=self.session_id,
            model=self.model,
            tool_timeout=self.tool_timeout,
            todos=self.todos,
            temp_dir=self.temp_dir,  # Lazily created when first accessed
        )

        # Execute agent loop
        updated_messages, response = await loop_execute(
            provider=self._provider,
            messages=self.messages,
            tools=self.tools,
            config=config,
            context=tool_context,
            todo_state=self.todos,
        )

        # Update messages and save new ones
        new_messages = updated_messages[len(self.messages) :]
        for msg in new_messages:
            self._save_message(msg)
        self.messages = updated_messages

        # Set session ID on response
        response.session_id = self.session_id

        return response

    async def _arun_structured(
        self,
        prompt: str,
        output_type: type[T],
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Response[T]:
        """
        Internal method for structured output execution.

        Creates a ResponseTool, injects it into the tools list, and streams
        events until respond is called successfully (with early exit).
        """
        from .types import ToolResult, Usage

        # Collect events from streaming and return as Response
        # This allows early exit when respond succeeds
        text_parts: list[str] = []
        thinking_parts: list[str] = []
        tool_results: list[ToolResult] = []
        usage: Usage | None = None
        stop_reason = "end_turn"
        validated_output: T | None = None

        # Track tool calls to get the input (since ToolResultEvent only has output)
        pending_tool_calls: dict[str, tuple[str, str]] = {}  # id -> (name, input_json)

        async for event in self._astream_structured(
            prompt=prompt,
            output_type=output_type,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            timeout=timeout,
            max_turns=max_turns,
            validation_retries=validation_retries,
        ):
            # Collect relevant data from events
            if isinstance(event, TextEvent):
                text_parts.append(event.text)
            elif isinstance(event, ThinkingEvent):
                thinking_parts.append(event.text)
            elif isinstance(event, ToolCallEvent):
                # Track tool call for later result matching
                pending_tool_calls[event.id] = (event.name, event.input)
            elif isinstance(event, ToolResultEvent):
                # Get input from tracked tool call
                tool_name, input_json = pending_tool_calls.get(
                    event.tool_use_id, (event.tool_name, "{}")
                )
                try:
                    input_dict = json.loads(input_json)
                except json.JSONDecodeError:
                    input_dict = {}
                tool_results.append(
                    ToolResult(
                        tool_use_id=event.tool_use_id,
                        tool_name=event.tool_name,
                        input=input_dict,
                        output=event.content,
                        is_error=event.is_error,
                    )
                )
            elif isinstance(event, UsageEvent):
                if usage is None:
                    usage = Usage(
                        input_tokens=event.input_tokens,
                        output_tokens=event.output_tokens,
                    )
                else:
                    # Accumulate usage
                    usage = usage.add(
                        Usage(
                            input_tokens=event.input_tokens,
                            output_tokens=event.output_tokens,
                        )
                    )
            elif isinstance(event, DoneEvent):
                stop_reason = event.stop_reason
            elif isinstance(event, StructuredOutputEvent):
                validated_output = event.output

        # Build response
        # Note: validated_output can be None if validation failed, but the Response
        # class handles this via its default (falls back to text). The cast tells
        # the type checker we're intentionally passing T | None.
        response = cast(
            "Response[T]",
            Response(
                text="".join(text_parts),
                thinking="".join(thinking_parts) if thinking_parts else None,
                model=f"{self._provider.name}/{self._provider.model_id}",
                session_id=self.session_id,
                usage=usage or Usage(input_tokens=0, output_tokens=0),
                tool_results=tool_results,
                stop_reason=stop_reason,
                output=validated_output,
            ),
        )

        return response

    @overload
    def run(
        self,
        prompt: str,
        response_format: None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Response[str]: ...

    @overload
    def run(
        self,
        prompt: str,
        response_format: type[T],
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Response[T]: ...

    def run(
        self,
        prompt: str,
        response_format: type[T] | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Response[T] | Response[str]:
        """
        Run a prompt synchronously.

        Args:
            prompt: User prompt.
            response_format: Pydantic model class for structured output (optional).
                            When provided, forces the model to call a 'respond' tool
                            and validates the output against this schema.
            max_output_tokens: Maximum tokens in response (default: 8192).
            temperature: Sampling temperature (optional).
            timeout: Total loop timeout in seconds (default: 300.0).
            max_turns: Maximum agent loop iterations (default: 50).
            validation_retries: Max validation retry attempts for structured output.

        Returns:
            Response object. If response_format is provided, response.output
            contains the validated Pydantic model instance.
        """
        result = _run_sync(
            self.arun(
                prompt,
                response_format,
                max_output_tokens,
                temperature,
                timeout,
                max_turns,
                validation_retries,
            )
        )
        return cast("Response[T] | Response[str]", result)

    async def astream(
        self,
        prompt: str,
        response_format: type[T] | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> AsyncIterator[Event]:
        """
        Stream events asynchronously.

        Args:
            prompt: User prompt.
            response_format: Pydantic model class for structured output (optional).
                            When provided, yields a StructuredOutputEvent with
                            the validated model after the respond tool is called.
            max_output_tokens: Maximum tokens in response (default: 8192).
            temperature: Sampling temperature (optional).
            timeout: Total loop timeout in seconds (default: 300.0).
            max_turns: Maximum agent loop iterations (default: 50).
            validation_retries: Max validation retry attempts for structured output.

        Yields:
            Event objects. If response_format is provided, includes a
            StructuredOutputEvent with the validated model.
        """
        # Handle structured output via response_format
        if response_format is not None:
            async for event in self._astream_structured(
                prompt=prompt,
                output_type=response_format,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                timeout=timeout,
                max_turns=max_turns,
                validation_retries=validation_retries,
            ):
                yield event
            return

        # Add user message
        user_msg = UserMessage(content=prompt)
        self.messages.append(user_msg)
        self._save_message(user_msg)

        # Build config
        config = self._make_config(max_output_tokens, temperature, timeout, max_turns)

        # Create tool context (with todos if todo tools are present)
        tool_context = ToolContext(
            workdir=self.workdir,
            session_id=self.session_id,
            model=self.model,
            tool_timeout=self.tool_timeout,
            todos=self.todos,
            temp_dir=self.temp_dir,  # Lazily created when first accessed
        )

        # Stream events
        async for event in loop_stream(
            provider=self._provider,
            messages=self.messages,
            tools=self.tools,
            config=config,
            context=tool_context,
            todo_state=self.todos,
        ):
            # Handle MessageEvent - save to session
            if isinstance(event, MessageEvent):
                self.messages.append(event.message)
                self._save_message(event.message)
            yield event

    async def _astream_structured(
        self,
        prompt: str,
        output_type: type[T],
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> AsyncIterator[Event]:
        """
        Internal method for streaming structured output with retry support.

        Streams events normally and yields a StructuredOutputEvent when
        the respond tool validation succeeds. Retries on validation failure.

        Messages are automatically saved via MessageEvent from the loop.
        """
        # Create respond tool and build tools list (without mutating self.tools)
        respond_tool = ResponseTool(output_type)
        tools_with_respond = [*self.tools, respond_tool]

        for attempt in range(validation_retries):
            # Use empty prompt on retries (session has context)
            current_prompt = prompt if attempt == 0 else ""

            # Track respond tool calls for validation
            pending_respond_calls: dict[str, str] = {}  # id -> input JSON

            # Add user message if prompt provided
            if current_prompt:
                user_msg = UserMessage(content=current_prompt)
                self.messages.append(user_msg)
                self._save_message(user_msg)

            # Build config
            config = self._make_config(
                max_output_tokens, temperature, timeout, max_turns
            )

            # Create tool context (with todos if todo tools are present)
            tool_context = ToolContext(
                workdir=self.workdir,
                session_id=self.session_id,
                model=self.model,
                tool_timeout=self.tool_timeout,
                todos=self.todos,
                temp_dir=self.temp_dir,  # Lazily created when first accessed
            )

            validation_failed = False
            respond_called = False

            # Stream events - let model use all tools freely
            # The model can call any tool (fetch, search, etc.) and should call
            # 'respond' when ready to produce structured output
            async for event in loop_stream(
                provider=self._provider,
                messages=self.messages,
                tools=tools_with_respond,
                config=config,
                context=tool_context,
            ):
                yield event

                # Handle MessageEvent - save to session
                if isinstance(event, MessageEvent):
                    self.messages.append(event.message)
                    self._save_message(event.message)

                # Track respond tool calls for validation
                elif isinstance(event, ToolCallEvent) and event.name == "respond":
                    pending_respond_calls[event.id] = event.input

                # Check respond tool result for validation
                elif (
                    isinstance(event, ToolResultEvent) and event.tool_name == "respond"
                ):
                    respond_called = True
                    if not event.is_error:
                        # Get the input from the tracked tool call
                        input_json = pending_respond_calls.get(event.tool_use_id, "{}")
                        try:
                            input_data = json.loads(input_json)
                            validated = schema_validate(output_type, input_data)
                            yield StructuredOutputEvent(
                                output=validated,
                                success=True,
                            )
                            # Terminate stream on successful structured output
                            return
                        except json.JSONDecodeError:
                            # JSON parsing failed, mark for retry
                            validation_failed = True
                        except Exception:
                            # Schema validation failed, mark for retry
                            validation_failed = True
                    else:
                        # Validation failed, mark for retry
                        validation_failed = True

            # If respond wasn't called or validation failed, retry if attempts remain
            if not respond_called or validation_failed:
                # Continue to next retry attempt
                continue

        # All retries exhausted
        yield StructuredOutputEvent(
            output=None,
            success=False,
        )

    def stream(
        self,
        prompt: str,
        response_format: type[T] | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        max_turns: int | None = None,
        validation_retries: int = 3,
    ) -> Iterator[Event]:
        """
        Stream events synchronously.

        Args:
            prompt: User prompt.
            response_format: Pydantic model class for structured output (optional).
                            When provided, yields a StructuredOutputEvent with
                            the validated model after the respond tool is called.
            max_output_tokens: Maximum tokens in response (default: 8192).
            temperature: Sampling temperature (optional).
            timeout: Total loop timeout in seconds (default: 300.0).
            max_turns: Maximum agent loop iterations (default: 50).
            validation_retries: Max validation retry attempts for structured output.

        Yields:
            Event objects. If response_format is provided, includes a
            StructuredOutputEvent with the validated model.
        """
        # Use thread + queue for true sync streaming
        queue: Queue[Event | None] = Queue()
        exception_holder: list[Exception | None] = [None]

        def producer() -> None:
            try:
                event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(event_loop)
                try:

                    async def stream_events() -> None:
                        async for event in self.astream(
                            prompt,
                            response_format,
                            max_output_tokens,
                            temperature,
                            timeout,
                            max_turns,
                            validation_retries,
                        ):
                            queue.put(event)
                        queue.put(None)  # Sentinel

                    event_loop.run_until_complete(stream_events())
                finally:
                    event_loop.close()
            except Exception as e:
                exception_holder[0] = e
                queue.put(None)

        thread = Thread(target=producer, daemon=True)
        thread.start()

        while True:
            item = queue.get()
            if item is None:
                # Check for exception before breaking
                if exception_holder[0]:
                    raise exception_holder[0]
                break
            if exception_holder[0]:
                raise exception_holder[0]
            yield item

    @contextlib.contextmanager
    def session(
        self,
    ) -> Generator[Any, None, None]:
        """
        Context manager for multi-turn conversations.

        Yields a callable that runs prompts within the same session.

        Example:
            with loop.session() as ask:
                ask("Remember this word: avocado")
                response = ask("What word did I ask you to remember?")
        """

        def ask(prompt: str, **kwargs: Any) -> Response[Any]:
            return self.run(prompt, **kwargs)

        # Add stream method to ask (dynamic attribute on function)
        ask.stream = lambda prompt, **kwargs: self.stream(prompt, **kwargs)

        yield ask

    @contextlib.asynccontextmanager
    async def asession(
        self,
    ) -> AsyncIterator[Any]:
        """
        Async context manager for multi-turn conversations.

        Yields a callable that runs prompts within the same session.

        Example:
            async with loop.asession() as ask:
                await ask("Remember this word: avocado")
                response = await ask("What word did I ask you to remember?")

                # Streaming also works within the session
                async for event in ask.astream("Tell me more"):
                    ...
        """

        async def ask(prompt: str, **kwargs: Any) -> Response[Any]:
            return await self.arun(prompt, **kwargs)

        # Add astream method to ask (dynamic attribute on function)
        ask.astream = lambda prompt, **kwargs: self.astream(prompt, **kwargs)

        yield ask


@overload
def run(
    prompt: str,
    model: str,
    response_format: None = None,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> Response[str]: ...


@overload
def run(
    prompt: str,
    model: str,
    response_format: type[T],
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> Response[T]: ...


def run(
    prompt: str,
    model: str,
    response_format: type[T] | None = None,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> Response[T] | Response[str]:
    """
    One-shot helper for running a prompt.

    Args:
        prompt: User prompt.
        model: Model string (e.g., "anthropic/claude-sonnet-4").
        response_format: Pydantic model class for structured output (optional).
        max_output_tokens: Maximum tokens in response (default: 8192).
        temperature: Sampling temperature (optional).
        timeout: Total loop timeout in seconds (default: 300.0).
        max_turns: Maximum agent loop iterations (default: 50).
        validation_retries: Max validation retry attempts for structured output.
        **kwargs: Additional Loop arguments (tools, system, workdir, etc.).

    Returns:
        Response object. If response_format is provided, response.output
        contains the validated Pydantic model instance.
    """
    return Loop(model=model, **kwargs).run(
        prompt,
        response_format=response_format,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        timeout=timeout,
        max_turns=max_turns,
        validation_retries=validation_retries,
    )


@overload
async def arun(
    prompt: str,
    model: str,
    response_format: None = None,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> Response[str]: ...


@overload
async def arun(
    prompt: str,
    model: str,
    response_format: type[T],
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> Response[T]: ...


async def arun(
    prompt: str,
    model: str,
    response_format: type[T] | None = None,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> Response[T] | Response[str]:
    """
    One-shot async helper for running a prompt.

    Args:
        prompt: User prompt.
        model: Model string (e.g., "anthropic/claude-sonnet-4").
        response_format: Pydantic model class for structured output (optional).
        max_output_tokens: Maximum tokens in response (default: 8192).
        temperature: Sampling temperature (optional).
        timeout: Total loop timeout in seconds (default: 300.0).
        max_turns: Maximum agent loop iterations (default: 50).
        validation_retries: Max validation retry attempts for structured output.
        **kwargs: Additional Loop arguments (tools, system, workdir, etc.).

    Returns:
        Response object. If response_format is provided, response.output
        contains the validated Pydantic model instance.
    """
    return await Loop(model=model, **kwargs).arun(
        prompt,
        response_format=response_format,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        timeout=timeout,
        max_turns=max_turns,
        validation_retries=validation_retries,
    )


def stream(
    prompt: str,
    model: str,
    response_format: type[T] | None = None,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> Iterator[Event]:
    """
    One-shot helper for streaming events.

    Args:
        prompt: User prompt.
        model: Model string (e.g., "anthropic/claude-sonnet-4").
        response_format: Pydantic model class for structured output (optional).
        max_output_tokens: Maximum tokens in response (default: 8192).
        temperature: Sampling temperature (optional).
        timeout: Total loop timeout in seconds (default: 300.0).
        max_turns: Maximum agent loop iterations (default: 50).
        validation_retries: Max validation retry attempts for structured output.
        **kwargs: Additional Loop arguments (tools, system, workdir, etc.).

    Yields:
        Event objects. If response_format is provided, includes a
        StructuredOutputEvent with the validated model.
    """
    yield from Loop(model=model, **kwargs).stream(
        prompt,
        response_format=response_format,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        timeout=timeout,
        max_turns=max_turns,
        validation_retries=validation_retries,
    )


async def astream(
    prompt: str,
    model: str,
    response_format: type[T] | None = None,
    max_output_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float | None = None,
    max_turns: int | None = None,
    validation_retries: int = 3,
    **kwargs: Any,
) -> AsyncIterator[Event]:
    """
    One-shot async helper for streaming events.

    Args:
        prompt: User prompt.
        model: Model string (e.g., "anthropic/claude-sonnet-4").
        response_format: Pydantic model class for structured output (optional).
        max_output_tokens: Maximum tokens in response (default: 8192).
        temperature: Sampling temperature (optional).
        timeout: Total loop timeout in seconds (default: 300.0).
        max_turns: Maximum agent loop iterations (default: 50).
        validation_retries: Max validation retry attempts for structured output.
        **kwargs: Additional Loop arguments (tools, system, workdir, etc.).

    Yields:
        Event objects. If response_format is provided, includes a
        StructuredOutputEvent with the validated model.
    """
    async for event in Loop(model=model, **kwargs).astream(
        prompt,
        response_format=response_format,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
        timeout=timeout,
        max_turns=max_turns,
        validation_retries=validation_retries,
    ):
        yield event


__all__ = ["Loop", "run", "arun", "stream", "astream"]
