"""Session context utilities for Brizz SDK."""

import json
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from typing import Any, TypeVar, cast

from opentelemetry import context, trace
from opentelemetry.sdk.trace import Span

from brizz._internal.semantic_conventions import (
    BRIZZ,
    PROPERTIES_CONTEXT_KEY,
    SESSION_ID,
    SESSION_INPUT,
    SESSION_OUTPUT,
    SESSION_SPAN_NAME,
)

# Type variable for generic function support
F = TypeVar("F", bound=Callable[..., Any])


class Session:
    """Session object for managing session-level attributes and data.

    Provides methods to set session input/output and custom attributes on the
    associated span.
    """

    def __init__(self, session_id: str, span: Span) -> None:
        """Initialize a Session instance.

        Args:
            session_id: The session identifier
            span: The OpenTelemetry span associated with this session
        """
        self.session_id = session_id
        self._span = span

    def set_input(self, text: str) -> None:
        """Append text to session input array attribute.

        Args:
            text: Text to append to session input
        """
        self._append_to_array_attribute(SESSION_INPUT, text)

    def set_output(self, text: str) -> None:
        """Append text to session output array attribute.

        Args:
            text: Text to append to session output
        """
        self._append_to_array_attribute(SESSION_OUTPUT, text)

    def update_properties(self, properties: dict[str, Any] | None = None, **kwargs: Any) -> None:
        """Update custom properties on the session span.

        Properties are set with the 'brizz.' prefix, matching the format
        used by custom_properties.

        Args:
            properties: Optional dictionary of properties to set
            **kwargs: Key-value pairs to set as custom properties

        Examples:
            session.update_properties(success=False)
            session.update_properties({"user_id": "123", "count": 5})
            session.update_properties({"user_id": "123"}, count=5)
        """
        # Merge dictionary and keyword arguments
        all_props = {}
        if properties:
            all_props.update(properties)
        if kwargs:
            all_props.update(kwargs)

        if not all_props:
            return

        # Set each property on the span with brizz. prefix
        for key, value in all_props.items():
            self._span.set_attribute(f"{BRIZZ}.{key}", value)

    def _append_to_array_attribute(self, key: str, value: str) -> None:
        """Helper method to append value to an array attribute on the span.

        The array is stored as a JSON string since span attributes don't support
        complex objects/arrays directly.

        Args:
            key: The attribute key
            value: The value to append
        """
        # Get current JSON string value (if it exists)
        current_json = None
        if hasattr(self._span, "attributes") and self._span.attributes:
            current_json = self._span.attributes.get(key)

        # Parse existing JSON array or create new array
        if current_json and isinstance(current_json, str):
            try:
                array = json.loads(current_json)
                if not isinstance(array, list):
                    array = [value]
                else:
                    array.append(value)
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, create new array
                array = [value]
        else:
            # Create new array
            array = [value]

        # Serialize array to JSON and set as attribute
        self._span.set_attribute(key, json.dumps(array))


def new_context(properties: dict[str, str]) -> context.Context:
    """Create a new OpenTelemetry context with given properties.

    Args:
        properties: Dictionary of properties to add to context

    Returns:
        New OpenTelemetry context with the properties set
    """
    if not properties:
        return context.get_current()

    # Get existing properties and merge with new ones
    current_context = context.get_current()
    existing_properties = cast(dict[str, Any], current_context.get(PROPERTIES_CONTEXT_KEY, {})) or {}
    merged_properties = {**existing_properties, **properties}

    return context.set_value(PROPERTIES_CONTEXT_KEY, merged_properties)


def with_properties(properties: dict[str, str], fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a function with OpenTelemetry context properties.

    Args:
        properties: Dictionary of properties to add to context
        fn: Function to execute with the properties
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    if not properties:
        return fn(*args, **kwargs)

    # Get existing properties and merge with new ones
    token = context.attach(new_context(properties))
    try:
        return fn(*args, **kwargs)
    finally:
        context.detach(token)


def with_session_id(session_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a function with session context.

    All telemetry (traces, spans, events) generated within the function
    will include the session ID.

    Examples:
        Basic usage with function:
        ```python
        result = with_session_id('session-123', my_function, arg1, arg2)
        ```

        With async function:
        ```python
        result = await with_session_id('session-456', my_async_function)
        ```

        Wrapping AI operations:
        ```python
        async def ai_operation():
            response = await openai.chat.completions.create({
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': 'Hello'}]
            })
            emit_event('ai.response', {'tokens': response.usage.total_tokens})
            return response

        response = await with_session_id('chat-session', ai_operation)
        ```

    Args:
        session_id: Session identifier to include in all telemetry
        fn: Function to execute with session context
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    return with_properties({SESSION_ID: session_id}, fn, *args, **kwargs)


async def awith_properties(properties: dict[str, str], fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute an async function with OpenTelemetry context properties.

    Args:
        properties: Dictionary of properties to add to context
        fn: Async function to execute with the properties
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    if not properties:
        return await fn(*args, **kwargs)

    # Get existing properties and merge with new ones
    token = context.attach(new_context(properties))
    try:
        return await fn(*args, **kwargs)
    finally:
        context.detach(token)


async def awith_session_id(session_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute an async function with session context.

    All telemetry (traces, spans, events) generated within the function
    will include the session ID.

    Examples:
        Basic usage with async function:
        ```python
        result = await awith_session_id('session-123', my_async_function, arg1, arg2)
        ```

        Wrapping async AI operations:
        ```python
        async def ai_operation():
            response = await openai.chat.completions.create({
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': 'Hello'}]
            })
            emit_event('ai.response', {'tokens': response.usage.total_tokens})
            return response

        response = await awith_session_id('chat-session', ai_operation)
        ```

    Args:
        session_id: Session identifier to include in all telemetry
        fn: Async function to execute with session context
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function
    """
    return await awith_properties({SESSION_ID: session_id}, fn, *args, **kwargs)


@contextmanager
def start_session(session_id: str, properties: dict[str, str] | None = None) -> Generator[Session]:
    """Context manager for session scope with optional additional properties.

    All telemetry (traces, spans, events) generated within the context
    will include the session ID and any additional properties.

    Args:
        session_id: Session identifier to include in all telemetry
        properties: Optional additional properties to include

    Yields:
        Session: Session object for managing session-level attributes

    Examples:
        Basic usage (without capturing session):
        ```python
        with start_session('session-123'):
            # All telemetry here includes session.id
            emit_event('user.action', {'action': 'click'})
        ```

        With capturing session:
        ```python
        with start_session('session-123') as session:
            session.set_input("user input")
            # LLM call
            session.set_output("generated output")
            session.update_properties(user_id='user-456')
        ```

        With additional properties:
        ```python
        with start_session('session-456', {'user_id': 'user-789', 'region': 'us-east'}):
            # All telemetry includes session.id, user_id, and region
            emit_event('purchase', {'amount': 99.99})
        ```

        With OpenAI:
        ```python
        with start_session('chat-session-123'):
            response = openai.chat.completions.create(
                model='gpt-4',
                messages=[{'role': 'user', 'content': 'Hello'}]
            )
        ```
    """
    all_properties = {SESSION_ID: session_id}
    if properties:
        all_properties.update(properties)

    # Use custom_properties to manage context
    with custom_properties(all_properties):
        # Create a span for this session
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(SESSION_SPAN_NAME) as span:
            session = Session(session_id, cast(Span, span))
            # Explicitly set SESSION_ID on the span for exporters
            span.set_attribute(f"{BRIZZ}.{SESSION_ID}", session_id)
            yield session


@contextmanager
def custom_properties(properties: dict[str, str]) -> Generator[None]:
    """Context manager for custom property scope.

    All telemetry (traces, spans, events) generated within the context
    will include the specified properties.

    Args:
        properties: Dictionary of properties to add to context

    Yields:
        None

    Examples:
        Basic usage:
        ```python
        with custom_properties({'user_id': 'user-123', 'region': 'us-west'}):
            # All telemetry here includes user_id and region
            emit_event('api.request', {'endpoint': '/users'})
        ```

        Nested usage:
        ```python
        with custom_properties({'tenant_id': 'tenant-1'}):
            with custom_properties({'request_id': 'req-456'}):
                # Both tenant_id and request_id are available
                emit_event('data.access')
        ```

        With OpenAI:
        ```python
        with custom_properties({'user_id': '123', 'experiment': 'variant-a'}):
            response = openai.chat.completions.create(
                model='gpt-4',
                messages=[{'role': 'user', 'content': 'Hello'}]
            )
        ```
    """
    if not properties:
        yield
        return

    token = context.attach(new_context(properties))
    try:
        yield
    finally:
        context.detach(token)


@asynccontextmanager
async def astart_session(
    session_id: str, properties: dict[str, str] | None = None
) -> AsyncGenerator[Session]:
    """Async context manager for session scope with optional additional properties.

    All telemetry (traces, spans, events) generated within the context
    will include the session ID and any additional properties.

    Args:
        session_id: Session identifier to include in all telemetry
        properties: Optional additional properties to include

    Yields:
        Session: Session object for managing session-level attributes

    Examples:
        Basic usage (without capturing session):
        ```python
        async with astart_session('session-123'):
            # All telemetry here includes session.id
            await async_operation()
        ```

        With capturing session:
        ```python
        async with astart_session('session-123') as session:
            session.set_input("user input")
            # Async LLM call
            session.set_output("generated output")
            session.update_properties(user_id='user-456')
        ```

        With additional properties:
        ```python
        async with astart_session('session-456', {'user_id': 'user-789'}):
            # All telemetry includes session.id and user_id
            await async_operation()
        ```

        With async OpenAI:
        ```python
        async with astart_session('chat-session-123'):
            response = await openai.chat.completions.create(
                model='gpt-4',
                messages=[{'role': 'user', 'content': 'Hello'}]
            )
        ```
    """
    all_properties = {SESSION_ID: session_id}
    if properties:
        all_properties.update(properties)

    # Use acustom_properties to manage context
    async with acustom_properties(all_properties):
        # Create a span for this session
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(SESSION_SPAN_NAME) as span:
            session = Session(session_id, cast(Span, span))
            # Explicitly set SESSION_ID on the span for exporters
            span.set_attribute(f"{BRIZZ}.{SESSION_ID}", session_id)
            yield session


@asynccontextmanager
async def acustom_properties(properties: dict[str, str]) -> AsyncGenerator[None]:
    """Async context manager for custom property scope.

    All telemetry (traces, spans, events) generated within the context
    will include the specified properties.

    Args:
        properties: Dictionary of properties to add to context

    Yields:
        None

    Examples:
        Basic usage:
        ```python
        async with acustom_properties({'user_id': 'user-123', 'region': 'us-west'}):
            # All telemetry here includes user_id and region
            await async_operation()
        ```

        With async OpenAI:
        ```python
        async with acustom_properties({'user_id': '123', 'experiment': 'variant-a'}):
            response = await openai.chat.completions.create(
                model='gpt-4',
                messages=[{'role': 'user', 'content': 'Hello'}]
            )
        ```
    """
    if not properties:
        yield
        return

    token = context.attach(new_context(properties))
    try:
        yield
    finally:
        context.detach(token)


def session_context(session_id: str) -> Callable[[F], F]:
    """Decorator to add session context to a function.

    Args:
        session_id: Session identifier to include in all telemetry

    Returns:
        Decorator function

    Examples:
        ```python
        @session_context('my-session')
        def my_function():
            # All telemetry here will include session_id
            pass
        ```
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return with_session_id(session_id, func, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def asession_context(session_id: str) -> Callable[[F], F]:
    """Async decorator to add session context to an async function.

    Args:
        session_id: Session identifier to include in all telemetry

    Returns:
        Decorator function

    Examples:
        ```python
        @asession_context('my-async-session')
        async def my_async_function():
            # All telemetry here will include session_id
            pass
        ```
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await awith_session_id(session_id, func, *args, **kwargs)

        return async_wrapper  # type: ignore

    return decorator
