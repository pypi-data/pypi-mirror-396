"""Main tracing module for Brizz SDK."""

from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, Resource
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import SpanExporter

from ..config import BrizzConfig
from ..log.logging import get_logger
from ..semantic_conventions import BRIZZ_SDK_LANGUAGE, BRIZZ_SDK_VERSION, SDK_LANGUAGE
from ..version import get_version
from .processors.span_processor import BrizzBatchSpanProcessor, BrizzSimpleSpanProcessor

logger = get_logger(__name__)


class TracingModule:
    """Main tracing module for Brizz SDK with singleton pattern."""

    _instance: Optional["TracingModule"] = None
    _initialized: bool = False

    def __new__(cls) -> "TracingModule":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if not self._initialized:
            self._span_exporter: SpanExporter | None = None
            self._span_processor: SpanProcessor | None = None
            self._tracer_provider: TracerProvider | None = None
            TracingModule._initialized = True

    @classmethod
    def get_instance(cls) -> "TracingModule":
        """Get the singleton instance of TracingModule.

        Raises:
            RuntimeError: If Brizz SDK is not initialized
        """
        if cls._instance is None:
            raise RuntimeError("Brizz must be initialized before accessing TracingModule")
        return cls._instance

    def setup(self, config: BrizzConfig) -> None:
        """Initialize the tracing module with the provided configuration.

        Args:
            config: Resolved Brizz SDK configuration
        """
        logger.info("Setting up tracing module")

        # Initialize exporter (custom or default)
        self._init_span_exporter(config)

        # Initialize processor with masking support
        self._init_span_processor(config)

        # Initialize TracerProvider
        self._init_tracer_provider(config)

        # Set as module instance for standalone functions
        TracingModule._instance = self

        logger.info("Tracing module setup completed")

    def _init_span_exporter(self, config: BrizzConfig) -> None:
        """Initialize the span exporter.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._span_exporter is not None:
            logger.debug("Span exporter already initialized, skipping re-initialization")
            return

        # Use custom span exporter if provided
        if hasattr(config, "custom_span_exporter") and config.custom_span_exporter is not None:
            logger.debug("Using custom span exporter")
            self._span_exporter = config.custom_span_exporter
            logger.debug("Custom span exporter initialized successfully")
            return

        # Use default OTLP exporter
        traces_url = config.base_url.rstrip("/") + "/v1/traces"
        logger.debug("Initializing default OTLP span exporter", extra={"url": traces_url})

        headers = dict(config.headers) if config.headers else {}

        self._span_exporter = OTLPSpanExporter(
            endpoint=traces_url,
            headers=headers,
        )

        logger.debug("OTLP span exporter initialized successfully")

    def _init_span_processor(self, config: BrizzConfig) -> None:
        """Initialize the span processor with masking support.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._span_processor is not None:
            logger.debug("Span processor already initialized, skipping re-initialization")
            return

        if self._span_exporter is None:
            raise RuntimeError("Span exporter must be initialized before processor")

        has_masking = (
            hasattr(config, "masking")
            and config.masking is not None
            and hasattr(config.masking, "span_masking")
            and config.masking.span_masking is not None
        )

        logger.debug(
            "Initializing span processor",
            extra={
                "disable_batch": config.disable_batch,
                "has_masking": has_masking,
            },
        )

        # Use masked processors if masking is configured, otherwise use standard processors
        disable_batch = config.disable_batch
        if disable_batch:
            logger.debug("Initializing simple span processor")
            self._span_processor = BrizzSimpleSpanProcessor(self._span_exporter, config)
        else:
            logger.debug("Initializing batch span processor")
            self._span_processor = BrizzBatchSpanProcessor(self._span_exporter, config)

        logger.debug("Span processor initialized successfully")

    def _init_tracer_provider(self, config: BrizzConfig) -> None:
        """Initialize and register the TracerProvider globally.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._tracer_provider is not None:
            logger.debug("TracerProvider already initialized, skipping re-initialization")
            return

        if self._span_processor is None:
            raise RuntimeError("Span processor must be initialized before TracerProvider")

        # Try to get existing TracerProvider from the SDK (not Proxy or NoOp)
        existing_provider = trace.get_tracer_provider()

        # Check if it's a real TracerProvider from the SDK that we can add processors to
        if isinstance(existing_provider, TracerProvider) and hasattr(existing_provider, "add_span_processor"):
            logger.debug("Existing SDK TracerProvider found - adding Brizz span processor to it")
            existing_provider.add_span_processor(self._span_processor)
            self._tracer_provider = existing_provider
            logger.debug(f"Brizz span processor added to existing TracerProvider for service: {config.app_name}")
        else:
            logger.debug("No existing SDK TracerProvider found - creating new one")

            # Create resource with app_name and additional attributes
            resource_attrs = {SERVICE_NAME: config.app_name}
            resource_attrs.update(config.resource_attributes)

            # Add environment attribute if specified
            if config.environment:
                resource_attrs[DEPLOYMENT_ENVIRONMENT] = config.environment

            # Add SDK version and language
            resource_attrs[BRIZZ_SDK_VERSION] = get_version()
            resource_attrs[BRIZZ_SDK_LANGUAGE] = SDK_LANGUAGE

            resource = Resource.create(resource_attrs)

            # Create TracerProvider with resource and add span processor
            self._tracer_provider = TracerProvider(resource=resource)
            self._tracer_provider.add_span_processor(self._span_processor)

            # Set as global TracerProvider
            trace.set_tracer_provider(self._tracer_provider)
            logger.info(f"New TracerProvider initialized and registered globally for service: {config.app_name}")

    def get_span_exporter(self) -> SpanExporter:
        """Get the span exporter.

        Returns:
            The initialized span exporter

        Raises:
            RuntimeError: If tracing module is not initialized
        """
        if self._span_exporter is None:
            raise RuntimeError("Tracing module not initialized")
        return self._span_exporter

    def get_span_processor(self) -> SpanProcessor:
        """Get the span processor.

        Returns:
            The initialized span processor

        Raises:
            RuntimeError: If tracing module is not initialized
        """
        if self._span_processor is None:
            raise RuntimeError("Tracing module not initialized")
        return self._span_processor

    def shutdown(self) -> None:
        """Shutdown the tracing module."""
        logger.debug("Shutting down tracing module")

        if self._tracer_provider and hasattr(self._tracer_provider, "shutdown"):
            self._tracer_provider.shutdown()

        if self._span_processor and hasattr(self._span_processor, "shutdown"):
            self._span_processor.shutdown()

        if self._span_exporter and hasattr(self._span_exporter, "shutdown"):
            self._span_exporter.shutdown()

        self._tracer_provider = None
        self._span_processor = None
        self._span_exporter = None

        # Reset singleton state
        TracingModule._instance = None
        TracingModule._initialized = False

        logger.debug("Tracing module shutdown completed")


def get_span_exporter() -> SpanExporter:
    """Get the OpenTelemetry Span Exporter configured for Brizz.

    Returns:
        The configured span exporter

    Raises:
        RuntimeError: If SDK is not initialized
    """
    return TracingModule.get_instance().get_span_exporter()


def get_span_processor() -> SpanProcessor:
    """Get the Span Processor configured for Brizz.

    Returns:
        The configured span processor

    Raises:
        RuntimeError: If SDK is not initialized
    """
    return TracingModule.get_instance().get_span_processor()
