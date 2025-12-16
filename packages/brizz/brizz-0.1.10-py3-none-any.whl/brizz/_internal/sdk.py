"""Brizz SDK - Internal implementation that coordinates all telemetry modules."""

import os
import sys
from typing import Any, Optional

from opentelemetry._logs import SeverityNumber
from opentelemetry.sdk._logs.export import LogExporter, LogRecordExporter
from opentelemetry.sdk.metrics.export import MetricReader
from opentelemetry.sdk.trace.export import SpanExporter

from brizz._internal.config import BrizzConfig, resolve_config
from brizz._internal.instrumentation import auto_instrument
from brizz._internal.log.logging import LoggingModule, get_logger
from brizz._internal.metric.metrics import MetricsModule
from brizz._internal.models import MaskingConfig
from brizz._internal.trace.tracing import TracingModule

from .exceptions import InitializationError, NotInitializedError

logger = get_logger("brizz.sdk")


# Exception classes (keeping existing ones)


class _Brizz:
    """Internal SDK implementation that coordinates all telemetry modules.

    This class is responsible for initialization and shutdown of the SDK.
    All functionality is exposed through the individual modules and utility functions.
    """

    _instance: Optional["_Brizz"] = None
    _initialized: bool = False

    def __new__(cls) -> "_Brizz":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the Brizz SDK."""
        # Only initialize once
        if not self._initialized:
            self._config: BrizzConfig | None = None
            self._tracing_module: TracingModule | None = None
            self._metrics_module: MetricsModule | None = None
            self._logging_module: LoggingModule | None = None
            _Brizz._initialized = True

    @classmethod
    def get_instance(cls) -> "_Brizz":
        """Get the singleton instance of _Brizz.

        Raises:
            RuntimeError: If Brizz SDK is not initialized
        """
        if cls._instance is None or not cls._instance.is_initialized():
            raise RuntimeError("Brizz SDK not initialized. Call initialize() first.")
        return cls._instance

    def initialize(
        self,
        app_name: str | None = None,
        base_url: str = "https://telemetry.brizz.dev",
        api_key: str | None = None,
        headers: dict[str, str] | None = None,
        disable_batch: bool = False,
        resource_attributes: dict[str, Any] | None = None,
        environment: str | None = None,
        masking: MaskingConfig | bool | None = None,
        log_level: str | int | None = None,
        allowed_instrumentations: list[str] | None = None,
        blocked_instrumentations: list[str] | None = None,
        # OpenTelemetry provider control
        custom_span_exporter: SpanExporter | None = None,
        custom_log_exporter: LogExporter | LogRecordExporter | None = None,
        custom_metric_reader: MetricReader | None = None,
    ) -> None:
        """Initialize the Brizz SDK.

        Args:
            app_name: Your application name (defaults to sys.argv[0])
            base_url: Base URL for telemetry endpoints (defaults to Brizz endpoint)
            api_key: Your Brizz API key
            headers: Additional headers
            disable_batch: Disable batch exporting
            resource_attributes: Additional resource attributes
            environment: Deployment environment (e.g., 'production', 'staging', 'development')
            masking: Masking configuration for sensitive data
            log_level: Log level for SDK internal logging (string or int/logging constant)
            allowed_instrumentations: Explicit whitelist of instrumentation names to enable.
                If set, blocked_instrumentations is ignored.
                If None, uses default AI packages with blocked_instrumentations applied.
                If empty list, disables all instrumentation.
            blocked_instrumentations: List of instrumentation names to block.
                Only applied when allowed_instrumentations is None.
            custom_span_exporter: Optional custom span exporter (for testing)
            custom_log_exporter: Optional custom log exporter (for testing)
            custom_metric_reader: Optional custom metric reader (for testing)

        Raises:
            InitializationError: If initialization fails

        Example:
            ```python
            import brizz

            # Simple initialization
            brizz.Brizz.initialize(
                app_name="my-app",
                api_key="your-api-key"
            )

            # Advanced initialization with masking
            brizz.Brizz.initialize(
                app_name="my-app",
                api_key="your-api-key",
                masking=True  # Enable default PII masking
            )
            ```
        """
        # for openinference-instrumentation-openai to capture message content
        os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")

        if self._config is not None:
            logger.debug("Brizz SDK already initialized, skipping")
            return

        try:
            logger.info("Starting Brizz SDK initialization")

            # Resolve configuration with environment overrides
            self._config = resolve_config(
                app_name=app_name or sys.argv[0],
                base_url=base_url,
                api_key=api_key,
                headers=headers,
                disable_batch=disable_batch,
                resource_attributes=resource_attributes,
                environment=environment,
                masking=masking,
                log_level=log_level,
                allowed_instrumentations=allowed_instrumentations,
                blocked_instrumentations=blocked_instrumentations,
                custom_span_exporter=custom_span_exporter,
                custom_log_exporter=custom_log_exporter,
                custom_metric_reader=custom_metric_reader,
            )

            logger.info(f"Initializing Brizz SDK - exporting to {self._config.base_url}")

            # Initialize telemetry modules
            self._initialize_modules()

            # Set as module instance for standalone functions
            _Brizz._instance = self

            logger.info("Brizz SDK initialization completed successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Brizz SDK: {e}")
            raise InitializationError(f"Failed to initialize SDK: {e}") from e

    def _initialize_modules(self) -> None:
        """Initialize all telemetry modules."""
        if not self._config:
            raise RuntimeError("Configuration not available for module initialization")

        logger.info("Initializing telemetry modules")

        # Initialize tracing module
        logger.debug("Initializing tracing module")
        self._tracing_module = TracingModule()
        self._tracing_module.setup(self._config)

        # Initialize metrics module
        logger.debug("Initializing metrics module")
        self._metrics_module = MetricsModule()
        self._metrics_module.setup(self._config)

        # Initialize logging module
        logger.debug("Initializing logging module")
        self._logging_module = LoggingModule()
        self._logging_module.setup(self._config)

        # Auto-instrument AI libraries first
        # Must happen after setup of otel modules setup to ensure not auto providers will be registered
        # from instrumentation
        logger.debug("Auto-instrumenting AI libraries")
        try:
            # Log instrumentation configuration
            if self._config.allowed_instrumentations is not None:
                logger.debug(f"Allowed instrumentations: {', '.join(self._config.allowed_instrumentations)}")
            if self._config.blocked_instrumentations:
                logger.debug(f"Blocked instrumentations: {', '.join(self._config.blocked_instrumentations)}")

            auto_instrument(
                allowed_instrumentations=self._config.allowed_instrumentations,
                blocked_instrumentations=self._config.blocked_instrumentations,
            )
        except Exception as e:
            logger.exception(f"Failed to auto-instrument AI libraries: {e}")
        else:
            logger.info("All telemetry modules initialized successfully")

    def is_initialized(self) -> bool:
        """Check if the Brizz SDK is initialized."""
        return (
            self._config is not None
            and self._tracing_module is not None
            and self._metrics_module is not None
            and self._logging_module is not None
            and self._logging_module.is_initialized()
        )

    def emit_event(
        self,
        name: str,
        attributes: dict[str, str | int | float | bool] | None = None,
        body: Any = None,
        severity_number: SeverityNumber = SeverityNumber.INFO,
    ) -> None:
        """Emit an OpenTelemetry event as a LogRecord.

        This function creates and emits an OpenTelemetry LogRecord representing
        the provided event. The event follows OpenTelemetry semantic conventions
        and is sent through the configured logger provider.

        Args:
            name: The name of the event (required)
            attributes: Optional attributes for the event
            body: Optional body content for the event
            severity_number: Severity level of the event, defaults to INFO

        Raises:
            NotInitializedError: If SDK is not initialized

        Example:
            ```python
            import brizz

            # Initialize the SDK
            brizz.Brizz.initialize(api_key="your-api-key")

            # Emit an event
            brizz.Brizz.emit_event(
                name="user.login",
                attributes={"user_id": "123", "method": "oauth"},
                body={"success": True, "duration_ms": 245}
            )
            ```
        """
        if not self.is_initialized():
            raise NotInitializedError("Brizz SDK not initialized. Call initialize() first.")

        if not self._logging_module:
            raise RuntimeError("Logging module not initialized")

        self._logging_module.emit_event(name, attributes, body, severity_number)

    def shutdown(self) -> None:
        """Gracefully shutdown the Brizz SDK.

        This method stops all telemetry collection, flushes any pending data,
        and releases resources. Should be called before application termination.

        Raises:
            RuntimeError: If shutdown fails

        Example:
            ```python
            import brizz

            # Shutdown before app exit
            await brizz.Brizz.shutdown()
            ```
        """
        if not self.is_initialized():
            logger.debug("Brizz SDK not initialized, nothing to shutdown")
            return

        logger.info("Shutting down Brizz SDK")

        try:
            # Shutdown all modules
            self._shutdown_modules()

            # Clear all references
            self._config = None
            self._tracing_module = None
            self._metrics_module = None
            self._logging_module = None

            # Reset singleton state
            _Brizz._instance = None
            _Brizz._initialized = False

            logger.info("Brizz SDK shut down successfully")

        except Exception as e:
            logger.error(f"Failed to shutdown Brizz SDK: {e}")
            raise RuntimeError(f"Failed to shutdown SDK: {e}") from e

    def _shutdown_modules(self) -> None:
        """Shutdown all telemetry modules."""
        logger.info("Shutting down telemetry modules")

        try:
            # Shutdown tracing module
            if self._tracing_module:
                try:
                    self._tracing_module.shutdown()
                except Exception as e:
                    logger.debug(f"Error shutting down tracing module: {e}")

            # Shutdown metrics module
            if self._metrics_module:
                try:
                    self._metrics_module.shutdown()
                except Exception as e:
                    logger.debug(f"Error shutting down metrics module: {e}")

            # Shutdown logging module
            if self._logging_module:
                try:
                    self._logging_module.shutdown()
                except Exception as e:
                    logger.debug(f"Error shutting down logging module: {e}")

            logger.info("All telemetry modules shut down successfully")

        except Exception as e:
            logger.error(f"Error shutting down modules: {e}")


# Global SDK instance
Brizz = _Brizz()
