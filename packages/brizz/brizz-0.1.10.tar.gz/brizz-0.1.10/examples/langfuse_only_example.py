"""Langfuse-only mode example with Brizz SDK.

This example demonstrates how to configure the Brizz SDK to work exclusively with
Langfuse for observability, disabling all Brizz SDK instrumentation.

Use Cases:
- When you're already using Langfuse and don't need Brizz instrumentation
- To avoid conflicts between multiple instrumentation libraries
- When you want Langfuse to be the single source of truth for tracing
- To reduce overhead by disabling automatic instrumentation

Configuration:
- Set `allowed_instrumentations=[]` to disable all Brizz instrumentation
- Langfuse remains fully functional and captures all traces
- The SDK still initializes but won't instrument any libraries
"""

import os
from typing import Any

from dotenv import load_dotenv
from langfuse import Langfuse

from brizz import Brizz, emit_event

load_dotenv()

# Check for required environment variables
required_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"Missing environment variables: {', '.join(missing_vars)}")
    print("Please set them in your .env file or environment")
    import sys
    sys.exit(1)


def initialize_brizz_langfuse_only() -> None:
    """Initialize Brizz SDK with Langfuse-only mode (no instrumentation)."""
    print("Initializing Brizz SDK in Langfuse-only mode...")
    print("  - All Brizz instrumentation: DISABLED")
    print("  - Langfuse integration: ENABLED")
    print()

    # Initialize Brizz with empty allowed_instrumentations list
    # This disables all automatic instrumentation while keeping the SDK running
    Brizz.initialize(
        app_name="langfuse-only-example",
        disable_batch=True,
        # IMPORTANT: Empty list disables ALL instrumentation
        # This prevents conflicts with Langfuse's own tracing
        allowed_instrumentations=[],
    )

    print("Brizz SDK initialized successfully in Langfuse-only mode")
    print()


def example_1_langfuse_basic_trace() -> None:
    """Example 1: Basic Langfuse tracing without Brizz instrumentation."""
    print("=" * 70)
    print("Example 1: Basic Langfuse Trace")
    print("=" * 70)

    # Initialize Langfuse client
    # In this mode, Langfuse handles all tracing directly
    langfuse = Langfuse()

    # Emit a Brizz event (optional, for correlation)
    emit_event(
        name="langfuse_only.example_started",
        attributes={
            "example": "basic_trace",
            "instrumentation_mode": "langfuse_only",
        },
    )

    # Create a Langfuse trace
    trace = langfuse.trace(  # type: ignore[attr-defined]
        name="basic_example_trace",
        user_id="user-123",
        metadata={"mode": "langfuse_only"},
    )

    # Create spans within the trace
    # Without Brizz instrumentation, only Langfuse captures these
    span1 = trace.span(
        name="processing_step_1",
        input={"query": "What is AI?"},
    )

    # Simulate some processing
    result_1 = "AI is the field of computer science..."

    span1.end(output={"result": result_1})

    # Create another span
    span2 = trace.span(
        name="processing_step_2",
        input={"previous_result": result_1},
    )

    final_result = "In summary, AI enables..."

    span2.end(output={"final_result": final_result})

    # End the trace
    trace.end(output={"result": final_result})

    print(f"Trace ID: {trace.id}")
    print(f"Result: {final_result}")
    print()

    emit_event(
        name="langfuse_only.example_completed",
        attributes={"example": "basic_trace", "trace_id": trace.id},
    )


def example_2_langfuse_with_llm_calls() -> None:
    """Example 2: Langfuse tracing LLM interactions without Brizz instrumentation."""
    print("=" * 70)
    print("Example 2: Langfuse LLM Call Tracing")
    print("=" * 70)

    langfuse = Langfuse()

    emit_event(
        name="langfuse_only.llm_example_started",
        attributes={"example": "llm_calls"},
    )

    # Create a trace for LLM interaction
    trace = langfuse.trace(  # type: ignore[attr-defined]
        name="llm_generation_trace",
        user_id="user-456",
        metadata={"model": "gpt-4", "mode": "langfuse_only"},
    )

    # Create a generation span (Langfuse's primary construct for LLM calls)
    generation = trace.generation(
        name="openai_generation",
        model="gpt-4",
        model_parameters={"temperature": 0.7, "max_tokens": 100},
        input=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in one sentence."},
        ],
    )

    # Simulate LLM response
    llm_output = (
        "Quantum computing uses quantum bits (qubits) that can exist in superposition, "
        "allowing simultaneous processing of multiple states."
    )

    # End generation with output and metrics
    generation.end(
        output=llm_output,
        usage={
            "input": 30,
            "output": 25,
        },
    )

    trace.end()

    print(f"Trace ID: {trace.id}")
    print(f"Generation ID: {generation.id}")
    print(f"LLM Output: {llm_output}")
    print()

    emit_event(
        name="langfuse_only.llm_example_completed",
        attributes={
            "example": "llm_calls",
            "trace_id": trace.id,
            "generation_id": generation.id,
        },
    )


def example_3_langfuse_custom_observations() -> None:
    """Example 3: Langfuse custom observations and metrics."""
    print("=" * 70)
    print("Example 3: Langfuse Custom Observations")
    print("=" * 70)

    langfuse = Langfuse()

    emit_event(
        name="langfuse_only.custom_observation_started",
        attributes={"example": "custom_observations"},
    )

    # Create a trace
    trace = langfuse.trace(  # type: ignore[attr-defined]
        name="custom_observation_trace",
        user_id="user-789",
        metadata={"mode": "langfuse_only"},
    )

    # Create a custom span for RAG retrieval
    retrieval_span = trace.span(
        name="rag_retrieval",
        input={
            "query": "What are embeddings?",
            "top_k": 5,
        },
    )

    retrieved_docs = [
        "Embeddings are dense vector representations of text.",
        "They capture semantic meaning in a continuous vector space.",
        "Common embedding models include BERT and GPT embeddings.",
    ]

    retrieval_span.end(
        output={
            "documents": retrieved_docs,
            "count": len(retrieved_docs),
        },
    )

    # Create a ranking span
    ranking_span = trace.span(
        name="document_ranking",
        input={
            "documents": retrieved_docs,
        },
    )

    ranked_docs = retrieved_docs[:2]  # Simulate ranking

    ranking_span.end(
        output={
            "top_documents": ranked_docs,
            "score": [0.95, 0.87],
        },
    )

    # End the trace with final metrics
    trace.end(
        output={"result": "RAG pipeline completed successfully"},
    )

    print(f"Trace ID: {trace.id}")
    print(f"Retrieved Documents: {len(retrieved_docs)}")
    print(f"Ranked Documents: {len(ranked_docs)}")
    print()

    emit_event(
        name="langfuse_only.custom_observation_completed",
        attributes={
            "example": "custom_observations",
            "trace_id": trace.id,
            "retrieved_count": len(retrieved_docs),
        },
    )


def example_4_error_handling_in_langfuse() -> None:
    """Example 4: Error handling and recovery with Langfuse."""
    print("=" * 70)
    print("Example 4: Error Handling in Langfuse")
    print("=" * 70)

    langfuse = Langfuse()

    emit_event(
        name="langfuse_only.error_handling_started",
        attributes={"example": "error_handling"},
    )

    # Create a trace that will capture an error
    trace = langfuse.trace(  # type: ignore[attr-defined]
        name="error_handling_trace",
        user_id="user-error",
        metadata={"mode": "langfuse_only"},
    )

    try:
        # Attempt 1: Initial operation
        span1 = trace.span(
            name="initial_operation",
            input={"data": "invalid_input"},
        )

        # Simulate error
        raise ValueError("Invalid input format")

    except ValueError as e:
        # End span with error
        span1.end(
            output=None,
            level="error",  # Mark span as error
        )

        emit_event(
            name="langfuse_only.operation_failed",
            attributes={
                "error": str(e),
                "example": "error_handling",
            },
        )

        # Attempt 2: Retry with corrected input
        span2 = trace.span(
            name="retry_operation",
            input={"data": "valid_input"},
        )

        result = "Successfully processed corrected input"

        span2.end(output=result)

        # End trace
        trace.end(output=result)

        print(f"Trace ID: {trace.id}")
        print(f"Error Handled: {str(e)}")
        print(f"Recovery Result: {result}")
        print()

    emit_event(
        name="langfuse_only.error_handling_completed",
        attributes={
            "example": "error_handling",
            "trace_id": trace.id,
        },
    )


def example_5_batch_operations() -> None:
    """Example 5: Batch processing with Langfuse."""
    print("=" * 70)
    print("Example 5: Batch Operations")
    print("=" * 70)

    langfuse = Langfuse()

    emit_event(
        name="langfuse_only.batch_started",
        attributes={"example": "batch_operations"},
    )

    # Create a parent trace for batch processing
    batch_trace = langfuse.trace(  # type: ignore[attr-defined]
        name="batch_processing_trace",
        user_id="user-batch",
        metadata={"total_items": 3, "mode": "langfuse_only"},
    )

    batch_results: list[dict[str, Any]] = []

    # Process multiple items
    for i in range(3):
        item_span = batch_trace.span(
            name=f"process_item_{i}",
            input={"item_index": i, "data": f"batch_item_{i}"},
        )

        # Simulate processing
        result = f"processed_item_{i}"

        item_span.end(output={"result": result})

        batch_results.append({
            "index": i,
            "result": result,
            "span_id": item_span.id,
        })

    # End batch trace
    batch_trace.end(
        output={
            "total_processed": len(batch_results),
            "results": batch_results,
        }
    )

    print(f"Trace ID: {batch_trace.id}")
    print(f"Total Items Processed: {len(batch_results)}")
    for batch_result in batch_results:
        print(f"  - Item {batch_result['index']}: {batch_result['result']}")
    print()

    emit_event(
        name="langfuse_only.batch_completed",
        attributes={
            "example": "batch_operations",
            "trace_id": batch_trace.id,
            "items_processed": len(batch_results),
        },
    )


def print_key_differences() -> None:
    """Print key differences between modes."""
    print("=" * 70)
    print("Key Differences: Langfuse-Only vs. Default Brizz Mode")
    print("=" * 70)

    differences = {
        "Instrumentation": {
            "Langfuse-Only": "Manual (you create traces)",
            "Default Brizz": "Automatic (decorators + instrumentation)",
        },
        "Overhead": {
            "Langfuse-Only": "Lower (no auto-instrumentation)",
            "Default Brizz": "Higher (comprehensive coverage)",
        },
        "Setup Required": {
            "Langfuse-Only": "More code, explicit tracing",
            "Default Brizz": "Less code, decorator-based",
        },
        "Integration": {
            "Langfuse-Only": "Langfuse only",
            "Default Brizz": "Multiple providers supported",
        },
        "Library Conflicts": {
            "Langfuse-Only": "None (no instrumentation)",
            "Default Brizz": "Potential conflicts with other SDKs",
        },
    }

    for aspect, modes in differences.items():
        print(f"\n{aspect}:")
        for mode, value in modes.items():
            print(f"  {mode}: {value}")

    print("\n" + "=" * 70)


def main() -> None:
    """Run all examples in Langfuse-only mode."""
    print("\n")
    print("=" * 70)
    print("Brizz SDK - Langfuse-Only Mode Examples")
    print("=" * 70)
    print()
    print("In this mode:")
    print("  - Brizz SDK is initialized but doesn't instrument any libraries")
    print("  - Langfuse captures all tracing directly")
    print("  - No conflicts between instrumentation libraries")
    print()

    # Initialize Brizz in Langfuse-only mode
    initialize_brizz_langfuse_only()

    # Run examples
    example_1_langfuse_basic_trace()
    example_2_langfuse_with_llm_calls()
    example_3_langfuse_custom_observations()
    example_4_error_handling_in_langfuse()
    example_5_batch_operations()

    # Print differences
    print_key_differences()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  1. Check your Langfuse dashboard for the traces")
    print("  2. Verify trace IDs in the logs match the dashboard")
    print("  3. Review span structure and metadata")
    print()

    emit_event(
        name="langfuse_only_examples_completed",
        attributes={"success": True},
    )


if __name__ == "__main__":
    main()
