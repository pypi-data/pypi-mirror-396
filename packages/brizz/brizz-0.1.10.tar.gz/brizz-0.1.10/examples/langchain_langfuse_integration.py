"""LangChain + Langfuse integration example with Brizz SDK.

This example demonstrates:
- Using LangChain for LLM calls with various models
- Integrating Langfuse for observability and tracing
- Combining Brizz SDK for additional instrumentation
- Creating RAG-like workflows with chains
- Using session context for request tracking and correlation
"""

import asyncio
import json
import os
import sys
import uuid
from typing import Any

from dotenv import load_dotenv
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langfuse.langchain import CallbackHandler

from brizz import Brizz, awith_session_id, emit_event, with_session_id

load_dotenv()

# Check for required environment variables
required_vars = ["OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"Missing environment variables: {', '.join(missing_vars)}")
    print("Please set them in your .env file or environment")
    sys.exit(1)

# Initialize Brizz SDK
Brizz.initialize(
    disable_batch=True,
    app_name="langchain-langfuse-example",
)

# Initialize Langfuse callback handler
langfuse_handler = CallbackHandler()


def example_1_simple_chain() -> str:
    """Example 1: Simple LangChain with LLM chain and session tracking."""
    session_id = uuid.uuid4().hex

    def run_chain(topic: str) -> str:
        """Run chain within session context."""
        emit_event(
            name="langchain.example_started",
            attributes={"example": "simple_chain", "session_id": session_id},
        )

        # Create LLM
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that explains concepts concisely.",
                ),
                ("user", "Explain {topic} in one sentence."),
            ]
        )

        # Create chain
        chain = prompt | llm

        # Run chain
        result = chain.invoke({"topic": topic})

        output = result.content if hasattr(result, "content") else str(result)
        output_str: str = output if isinstance(output, str) else str(output)

        emit_event(
            name="langchain.example_completed",
            attributes={"example": "simple_chain", "success": True, "session_id": session_id},
        )

        return output_str

    # Use with_session_id to wrap the chain execution
    return_value = with_session_id(session_id, run_chain, "quantum computing")
    return return_value if isinstance(return_value, str) else str(return_value)


def example_2_rag_workflow() -> str:
    """Example 2: RAG-like workflow with document retrieval and QA."""
    emit_event(
        name="langchain.example_started",
        attributes={"example": "rag_workflow"},
    )

    # Sample documents
    documents_text = [
        "Quantum computers use quantum bits (qubits) that can exist in superposition.",
        "Machine learning models learn patterns from data through training.",
        "Natural language processing enables computers to understand human language.",
        "Deep learning uses neural networks with multiple layers to process data.",
        "Transfer learning allows models trained on one task to be applied to another.",
    ]

    # Create documents
    docs = [Document(page_content=text) for text in documents_text]

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
    )
    chunks = text_splitter.split_documents(docs)

    emit_event(
        name="langchain.documents_prepared",
        attributes={"chunk_count": len(chunks)},
    )

    # Create simple in-memory retriever
    class SimpleRetriever(BaseRetriever):
        """Simple retriever that finds relevant documents."""

        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun | None = None
        ) -> list[Document]:
            # Simple keyword matching for demo
            query_lower = query.lower()
            return [doc for doc in chunks if any(word in doc.page_content.lower() for word in query_lower.split())]

    retriever = SimpleRetriever()

    # Create LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    # Create RAG prompt
    rag_prompt = ChatPromptTemplate.from_template(
        """Use the following context to answer the question.
        Context: {context}
        Question: {question}
        Answer:"""
    )

    # Create RAG chain
    def format_docs(docs_list: list[Document]) -> str:
        return "\n\n".join(doc.page_content for doc in docs_list)

    rag_chain: Any = (
        {
            "context": lambda x: format_docs(retriever.invoke(x["question"])),
            "question": lambda x: x["question"],
        }
        | rag_prompt
        | llm
    )

    # Run RAG chain
    result = rag_chain.invoke({"question": "What is machine learning?"})

    output = result.content if hasattr(result, "content") else str(result)
    output_str: str = output if isinstance(output, str) else str(output)

    emit_event(
        name="langchain.example_completed",
        attributes={"example": "rag_workflow", "success": True},
    )

    return output_str


def example_3_multi_step_chain() -> dict[str, Any]:
    """Example 3: Multi-step chain with tool use and sequential processing."""
    emit_event(
        name="langchain.example_started",
        attributes={"example": "multi_step_chain"},
    )

    # Define tools
    @tool
    def get_weather(location: str) -> str:
        """Get weather information for a location."""
        emit_event(
            name="tool.weather_called",
            attributes={"location": location},
        )
        # Mock weather data
        weather_data = {
            "new york": "Sunny, 72°F",
            "london": "Rainy, 55°F",
            "tokyo": "Cloudy, 68°F",
        }
        return weather_data.get(location.lower(), "Weather data not available")

    @tool
    def get_recommendations(weather: str) -> str:
        """Get activity recommendations based on weather."""
        emit_event(
            name="tool.recommendations_called",
            attributes={"weather": weather},
        )
        if "sunny" in weather.lower():
            return "Go to the beach or park, wear sunscreen"
        elif "rainy" in weather.lower():
            return "Stay indoors, watch a movie, read a book"
        else:
            return "Perfect day for a walk or light outdoor activities"

    # Create LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    # Create prompt for tool use
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Use the available tools to help the user.",
            ),
            ("user", "{query}"),
        ]
    )

    # Create chain
    chain = prompt | llm

    # Simulate multi-step workflow
    query = "What's the weather in New York and what should I do?"

    result = chain.invoke({"query": query})

    # Get tool results manually for demo
    weather_result = get_weather("new york")
    recommendations_result = get_recommendations(weather_result)

    output = {
        "llm_response": (result.content if hasattr(result, "content") else str(result)),
        "weather": weather_result,
        "recommendations": recommendations_result,
    }

    emit_event(
        name="langchain.example_completed",
        attributes={"example": "multi_step_chain", "success": True},
    )

    return output


def example_4_batch_processing() -> list[str]:
    """Example 4: Batch processing multiple queries with streaming."""
    emit_event(
        name="langchain.example_started",
        attributes={"example": "batch_processing"},
    )

    # Create LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    # Create prompt
    prompt = PromptTemplate.from_template("Generate a creative name for a {business_type} business:")

    # Create chain
    chain = prompt | llm

    # Batch queries
    queries = [
        {"business_type": "coffee shop"},
        {"business_type": "tech startup"},
        {"business_type": "bookstore"},
    ]

    results: list[str] = []

    for i, query in enumerate(queries):
        emit_event(
            name="langchain.batch_item_processing",
            attributes={"batch_index": i, "total": len(queries)},
        )

        result = chain.invoke(query)

        output = result.content if hasattr(result, "content") else str(result)
        output_str: str = output if isinstance(output, str) else str(output)
        results.append(output_str)

        emit_event(
            name="langchain.batch_item_completed",
            attributes={"batch_index": i, "result_length": len(output_str)},
        )

    emit_event(
        name="langchain.example_completed",
        attributes={"example": "batch_processing", "total_items": len(results)},
    )

    return results


def example_5_error_handling_and_retry() -> str:
    """Example 5: Error handling and retry logic."""
    emit_event(
        name="langchain.example_started",
        attributes={"example": "error_handling"},
    )

    # Create LLM with retry
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_retries=2,
    )

    # Create prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer the question concisely.",
            ),
            ("user", "{question}"),
        ]
    )

    # Create chain with error handling
    chain = prompt | llm

    try:
        result = chain.invoke({"question": "What is the meaning of life?"})

        output = result.content if hasattr(result, "content") else str(result)
        output_str: str = output if isinstance(output, str) else str(output)

        emit_event(
            name="langchain.example_completed",
            attributes={"example": "error_handling", "success": True},
        )

        return output_str

    except Exception as e:
        emit_event(
            name="langchain.error_occurred",
            attributes={"example": "error_handling", "error": str(e)},
        )
        error_msg: str = f"Error: {str(e)}"
        return error_msg


def example_6_with_session_context() -> str:
    """Example 6: Using session context for request tracking."""
    session_id = uuid.uuid4().hex

    def process_with_session(topic: str) -> str:
        """Process LLM call within session context."""
        emit_event(
            name="langchain.session_context_started",
            attributes={"session_id": session_id, "topic": topic},
        )

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that explains concepts concisely.",
                ),
                ("user", "Explain {topic} in one sentence."),
            ]
        )

        chain = prompt | llm
        result = chain.invoke({"topic": topic})
        output = result.content if hasattr(result, "content") else str(result)
        output_str: str = output if isinstance(output, str) else str(output)

        emit_event(
            name="langchain.session_context_completed",
            attributes={"session_id": session_id, "topic": topic},
        )

        return output_str

    # Use with_session_id to wrap the function call
    result = with_session_id(session_id, process_with_session, "artificial intelligence")
    return result if isinstance(result, str) else str(result)


async def example_7_async_with_session_context() -> str:
    """Example 7: Async session context for concurrent operations."""
    session_id = uuid.uuid4().hex

    async def async_process_with_session(topic: str) -> str:
        """Process LLM call asynchronously within session context."""
        emit_event(
            name="langchain.async_session_started",
            attributes={"session_id": session_id, "topic": topic},
        )

        # Simulate async processing
        await asyncio.sleep(0.1)

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that explains concepts concisely.",
                ),
                ("user", "Explain {topic} in one sentence."),
            ]
        )

        chain = prompt | llm
        result = chain.invoke({"topic": topic})
        output = result.content if hasattr(result, "content") else str(result)
        output_str: str = output if isinstance(output, str) else str(output)

        emit_event(
            name="langchain.async_session_completed",
            attributes={"session_id": session_id, "topic": topic},
        )

        return output_str

    # Use awith_session_id for async operations
    result = await awith_session_id(session_id, async_process_with_session, "machine learning")
    return result if isinstance(result, str) else str(result)


def main() -> None:
    """Run all examples."""
    emit_event(
        name="langchain_langfuse_examples_started",
        attributes={"app": "langchain-langfuse-example"},
    )

    print("\n" + "=" * 60)
    print("LangChain + Langfuse Integration Examples")
    print("=" * 60)

    # Example 1: Simple chain
    print("\n[Example 1] Simple Chain:")
    print("-" * 60)
    result1 = example_1_simple_chain()
    print(f"Result: {result1}\n")

    # Example 2: RAG workflow
    print("[Example 2] RAG Workflow:")
    print("-" * 60)
    result2 = example_2_rag_workflow()
    print(f"Result: {result2}\n")

    # Example 3: Multi-step chain
    print("[Example 3] Multi-Step Chain:")
    print("-" * 60)
    result3 = example_3_multi_step_chain()
    print(f"Result: {json.dumps(result3, indent=2)}\n")

    # Example 4: Batch processing
    print("[Example 4] Batch Processing:")
    print("-" * 60)
    result4 = example_4_batch_processing()
    for i, result in enumerate(result4):
        print(f"  {i + 1}. {result}")
    print()

    # Example 5: Error handling
    print("[Example 5] Error Handling:")
    print("-" * 60)
    result5 = example_5_error_handling_and_retry()
    print(f"Result: {result5}\n")

    # Example 6: Session context
    print("[Example 6] Session Context:")
    print("-" * 60)
    result6 = example_6_with_session_context()
    print(f"Result: {result6}\n")

    # Example 7: Async session context
    print("[Example 7] Async Session Context:")
    print("-" * 60)
    result7 = asyncio.run(example_7_async_with_session_context())
    print(f"Result: {result7}\n")

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)

    emit_event(
        name="langchain_langfuse_examples_completed",
        attributes={"app": "langchain-langfuse-example", "success": True},
    )


if __name__ == "__main__":
    main()
