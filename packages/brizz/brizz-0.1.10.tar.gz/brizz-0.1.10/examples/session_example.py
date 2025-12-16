"""Simple session context example for Brizz Python SDK."""

import asyncio
import uuid

from brizz import (
    Brizz,
    asession_context,
    astart_session,
    awith_session_id,
    session_context,
    start_session,
    with_session_id,
)

# Initialize SDK
Brizz.initialize(
    base_url="http://localhost:4318",
    disable_batch=True,
    app_name="session-example",
)


async def endpoint_async(user_id: str) -> str:
    """Async operation with session context."""
    Brizz.emit_event("operation.started", attributes={"user_id": user_id})
    return f"Processed user {user_id}"


def endpoint_sync(task: str) -> str:
    """Sync operation with session context."""
    Brizz.emit_event("task.completed", attributes={"task": task})
    return f"Completed {task}"


async def endpoint_async_decorator(task: str) -> str:
    """Sync operation with session context."""
    session_id = uuid.uuid4().hex

    @asession_context(session_id)
    async def inner_async_decorator(task: str) -> str:
        """Async operation with session context."""
        Brizz.emit_event("task.completed", attributes={"task": task})
        return f"Completed {task}"

    return await inner_async_decorator(task)


def endpoint_sync_decorator(task: str) -> str:
    """Sync operation with session context."""
    session_id = uuid.uuid4().hex

    @session_context(session_id)
    def inner_sync_decorator(task: str) -> str:
        """Sync operation with session context."""
        Brizz.emit_event("task.completed", attributes={"task": task})
        return f"Completed {task}"

    return inner_sync_decorator(task)


def session_with_llm_call(user_input: str) -> str:
    """Example of session management with LLM call."""
    session_id = uuid.uuid4().hex

    with start_session(session_id) as session:
        # Record user input
        session.set_input(user_input)

        # Update custom properties
        session.update_properties(user_id="user-123", model="gpt-4")

        # Simulate LLM call
        Brizz.emit_event("llm.call", attributes={"model": "gpt-4", "prompt_tokens": 150})

        # Record output
        output = f"Response to: {user_input}"
        session.set_output(output)

        Brizz.emit_event("llm.response", attributes={"completion_tokens": 50})

        return output


async def async_session_with_llm_call(user_input: str) -> str:
    """Async example of session management with LLM call."""
    session_id = uuid.uuid4().hex

    async with astart_session(session_id) as session:
        # Record user input
        session.set_input(user_input)

        # Update custom properties
        session.update_properties(user_id="user-456", model="gpt-4")

        # Simulate async LLM call
        Brizz.emit_event("llm.call", attributes={"model": "gpt-4", "prompt_tokens": 200})
        await asyncio.sleep(0.1)  # Simulate async operation

        # Record output
        output = f"Async response to: {user_input}"
        session.set_output(output)

        Brizz.emit_event("llm.response", attributes={"completion_tokens": 75})

        return output


async def main() -> None:
    """Main function to demonstrate session context usage."""
    # Original examples
    session_id = uuid.uuid4().hex
    result1 = await awith_session_id(session_id, endpoint_async, "doo")
    result2 = with_session_id(session_id, endpoint_sync, "goo")
    result3 = await endpoint_async_decorator("foo")
    result4 = endpoint_sync_decorator("bar")

    print(f"Async: {result1}")
    print(f"Sync: {result2}")
    print(f"Async Decorator: {result3}")
    print(f"Sync Decorator: {result4}")

    # New session management examples
    print("\n--- New Session Management Examples ---")

    # Sync example
    result5 = session_with_llm_call("What is the meaning of life?")
    print(f"Sync Session LLM: {result5}")

    # Async example
    result6 = await async_session_with_llm_call("Tell me a joke")
    print(f"Async Session LLM: {result6}")


if __name__ == "__main__":
    asyncio.run(main())
