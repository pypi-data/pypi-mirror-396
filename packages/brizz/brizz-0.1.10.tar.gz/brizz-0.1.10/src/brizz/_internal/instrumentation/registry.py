"""Simple auto instrumentation for AI libraries."""

import importlib
import logging
import os
from typing import Optional, Protocol

from opentelemetry.instrumentation.dependencies import DependencyConflictError
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger("brizz.instrumentation")

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_DISABLE_TRACKING"] = "true"

# Default AI packages to instrument (excludes HTTP/infrastructure packages)
DEFAULT_AI_INSTRUMENTATIONS = {
    "openai",
    "anthropic",
    "cohere",
    "langchain",
    "llamaindex",
    "bedrock",
    "vertexai",
    "alephalpha",
    "chromadb",
    "crewai",
    "google_generativeai",
    "groq",
    "lancedb",
    "marqo",
    "milvus",
    "mistralai",
    "ollama",
    "pinecone",
    "qdrant",
    "replicate",
    "sagemaker",
    "together",
    "transformers",
    "watsonx",
    "weaviate",
}


class InstrumentationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    module_name: str
    instrumentation_class: str


class Instrumentation(Protocol):
    def __call__(self) -> None:
        """Call the instrumentation to apply it."""
        ...

    def instrument(self) -> None:
        """Instrument the library."""
        ...

    def uninstrument(self) -> None:
        """Uninstrument the library."""
        ...


class InstrumentationRegistry:
    """Simple registry for auto-instrumenting AI libraries with singleton pattern."""

    _instance: Optional["InstrumentationRegistry"] = None
    _initialized: bool = False

    # All supported instrumentations with their package names
    SUPPORTED_INSTRUMENTATIONS: list[InstrumentationConfig] = [
        InstrumentationConfig(
            module_name="openinference.instrumentation.openai", instrumentation_class="OpenAIInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.anthropic", instrumentation_class="AnthropicInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.cohere", instrumentation_class="CohereInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.langchain", instrumentation_class="LangchainInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.llamaindex", instrumentation_class="LlamaIndexInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.bedrock", instrumentation_class="BedrockInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.vertexai", instrumentation_class="VertexAIInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.alephalpha", instrumentation_class="AlephAlphaInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.chromadb", instrumentation_class="ChromaInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.crewai", instrumentation_class="CrewAIInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.google_generativeai",
            instrumentation_class="GoogleGenerativeAiInstrumentor",
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.groq", instrumentation_class="GroqInstrumentor"
        ),
        # TODO: disable for now due to circular import issues - RND-820
        # InstrumentationConfig(
        #     module_name="opentelemetry.instrumentation.haystack", instrumentation_class="HaystackInstrumentor"
        # ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.lancedb", instrumentation_class="LanceInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.marqo", instrumentation_class="MarqoInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.milvus", instrumentation_class="MilvusInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.mistralai", instrumentation_class="MistralAiInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.ollama", instrumentation_class="OllamaInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.pinecone", instrumentation_class="PineconeInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.qdrant", instrumentation_class="QdrantInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.redis", instrumentation_class="RedisInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.replicate", instrumentation_class="ReplicateInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.requests", instrumentation_class="RequestsInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.httpx", instrumentation_class="HTTPXClientInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.urllib", instrumentation_class="URLLibInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.aiohttp_client",
            instrumentation_class="AioHttpClientInstrumentor",
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.sagemaker", instrumentation_class="SageMakerInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.sqlalchemy", instrumentation_class="SQLAlchemyInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.threading", instrumentation_class="ThreadingInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.together", instrumentation_class="TogetherAiInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.transformers", instrumentation_class="TransformersInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.urllib3", instrumentation_class="URLLib3Instrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.watsonx", instrumentation_class="WatsonxInstrumentor"
        ),
        InstrumentationConfig(
            module_name="opentelemetry.instrumentation.weaviate", instrumentation_class="WeaviateInstrumentor"
        ),
    ]

    def __new__(cls) -> "InstrumentationRegistry":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if not self._initialized:
            self._instrumented: set[InstrumentationConfig] = set()
            InstrumentationRegistry._initialized = True

    @classmethod
    def get_instance(cls) -> "InstrumentationRegistry":
        """Get the singleton instance of InstrumentationRegistry.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def auto_instrument_all(
        self,
        allowed_instrumentations: list[str] | None = None,
        blocked_instrumentations: list[str] | None = None,
    ) -> None:
        """Auto-instrument all available AI libraries.

        Args:
            allowed_instrumentations: Explicit whitelist of instrumentation names to enable.
                If set, blocked_instrumentations is ignored.
                If None, uses DEFAULT_AI_INSTRUMENTATIONS with blocked_instrumentations applied.
                If empty list, disables all instrumentation (useful for Langfuse-only mode).
            blocked_instrumentations: List of instrumentation names to block.
                Only applied when allowed_instrumentations is None.
        """
        # Determine which instrumentations to enable
        if allowed_instrumentations is not None:
            if len(allowed_instrumentations) == 0:
                # Empty list = disable all instrumentation
                logger.info("All instrumentation disabled (allowed_instrumentations is empty)")
                return
            # Use explicit whitelist
            allowed_set = set(allowed_instrumentations)
            logger.debug(
                f"Using explicit whitelist with {len(allowed_set)} allowed instrumentations: "
                f"{', '.join(sorted(allowed_set))}"
            )
        else:
            # Default: use AI packages with optional blocklist
            allowed_set = DEFAULT_AI_INSTRUMENTATIONS.copy()
            if blocked_instrumentations:
                blocked_set = set(blocked_instrumentations)
                allowed_set = allowed_set - blocked_set
                logger.debug(
                    f"Using default AI instrumentations minus blocklist. "
                    f"Blocked: {', '.join(sorted(blocked_set))}. "
                    f"Allowed: {', '.join(sorted(allowed_set))}"
                )
            else:
                logger.debug(f"Using default AI instrumentations: {', '.join(sorted(allowed_set))}")

        instrumented_count = 0

        logger.debug(f"Checking {len(self.SUPPORTED_INSTRUMENTATIONS)} instrumentation packages")

        for instrumentation_config in self.SUPPORTED_INSTRUMENTATIONS:
            # Extract the instrumentation name from module_name
            # e.g., "opentelemetry.instrumentation.urllib" -> "urllib"
            instrumentation_name = instrumentation_config.module_name.split(".")[-1]

            if instrumentation_name not in allowed_set:
                logger.debug(f"Skipping {instrumentation_config.module_name} (not in allowed list)")
                continue

            if self._auto_instrument_package(instrumentation_config):
                self._instrumented.add(instrumentation_config)
                instrumented_count += 1

        if instrumented_count > 0:
            library_names = [config.module_name for config in self._instrumented]
            logger.info(f"Auto-instrumented {instrumented_count} libraries: {', '.join(library_names)}")
        else:
            logger.debug("No libraries found for instrumentation")

    def _auto_instrument_package(self, instrumentation_config: InstrumentationConfig) -> bool:
        """Auto-instrument a single package.

        Args:
            instrumentation_config: Configuration for the instrumentation package

        Returns:
            True if instrumentation succeeded, False otherwise
        """
        try:
            module = importlib.import_module(instrumentation_config.module_name)
        except ImportError:
            logger.debug(f"Failed to auto-instrument {instrumentation_config.module_name}", exc_info=True)
            return False
        try:
            instrumentation_class = getattr(module, instrumentation_config.instrumentation_class)
            instrumentation: Instrumentation = instrumentation_class()
            instrumentation.instrument(raise_exception_on_conflict=True)  # type: ignore
            return True
        except DependencyConflictError as e:
            if 'but found: "None"' in str(e):
                # This usually means the library is not installed - ignore
                logger.debug(
                    f"Failed to auto-instrument {instrumentation_config.module_name}: {e}",
                    exc_info=True,
                    extra={"instrumentation_config": instrumentation_config.model_dump()},
                )
            else:
                logger.error(
                    f"Dependency conflict for {instrumentation_config.module_name}: {e}",
                    exc_info=True,
                    extra={"instrumentation_config": instrumentation_config.model_dump()},
                )
            return False
        except Exception as e:
            logger.debug(
                f"Failed to auto-instrument {instrumentation_config.module_name}: {e}",
                exc_info=True,
                extra={"instrumentation_config": instrumentation_config.model_dump()},
            )
            return False

    def get_instrumented_count(self) -> int:
        """Get the number of instrumented libraries.

        Returns:
            Number of instrumented libraries
        """
        return len(self._instrumented)


def auto_instrument(
    allowed_instrumentations: list[str] | None = None,
    blocked_instrumentations: list[str] | None = None,
) -> None:
    """Auto-instrument all available AI libraries.

    This is the main entry point for auto instrumentation.
    It will automatically detect and instrument all supported AI libraries.

    Args:
        allowed_instrumentations: Explicit whitelist of instrumentation names to enable.
            If set, blocked_instrumentations is ignored.
            If None, uses DEFAULT_AI_INSTRUMENTATIONS with blocked_instrumentations applied.
            If empty list, disables all instrumentation (useful for Langfuse-only mode).
        blocked_instrumentations: List of instrumentation names to block.
            Only applied when allowed_instrumentations is None.
    """
    registry = InstrumentationRegistry.get_instance()
    registry.auto_instrument_all(
        allowed_instrumentations=allowed_instrumentations,
        blocked_instrumentations=blocked_instrumentations,
    )
