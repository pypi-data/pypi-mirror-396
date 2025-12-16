"""Main logging module for Brizz SDK."""

import logging
from typing import Any, Optional

from opentelemetry import context
from opentelemetry._logs import SeverityNumber
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LogRecordProcessor
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, SERVICE_NAME, Resource

from ..config import BrizzConfig
from ..semantic_conventions import BRIZZ, BRIZZ_SDK_LANGUAGE, BRIZZ_SDK_VERSION, PROPERTIES_CONTEXT_KEY, SDK_LANGUAGE
from ..version import get_version
from .processors.log_processor import (
    BrizzBatchLogRecordProcessor,
    BrizzSimpleLogRecordProcessor,
)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


logger = get_logger(__name__)


class LoggingModule:
    """Main logging module for Brizz SDK with singleton pattern."""

    _instance: Optional["LoggingModule"] = None
    _initialized: bool = False

    def __new__(cls) -> "LoggingModule":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if not self._initialized:
            self._log_exporter: Any | None = None
            self._log_processor: LogRecordProcessor | None = None
            self._logger_provider: LoggerProvider | None = None
            LoggingModule._initialized = True

    @classmethod
    def get_instance(cls) -> "LoggingModule":
        """Get the singleton instance of LoggingModule.

        Raises:
            RuntimeError: If Brizz SDK is not initialized
        """
        if cls._instance is None or not cls._instance.is_initialized():
            raise RuntimeError("Brizz must be initialized before accessing LoggingModule")
        return cls._instance

    def setup(self, config: BrizzConfig) -> None:
        """Initialize the logging module with the provided configuration.

        Args:
            config: Resolved Brizz SDK configuration
        """
        logger.info("Setting up logging module")

        # Initialize exporter
        self._init_log_exporter(config)

        # Initialize processor with masking support
        self._init_log_processor(config)

        # Initialize logger provider
        self._init_logger_provider(config)

        # Set as module instance for standalone functions
        LoggingModule._instance = self

        logger.info("Logging module setup completed")

    def _init_log_exporter(self, config: BrizzConfig) -> None:
        """Initialize the log exporter.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._log_exporter is not None:
            logger.debug("Log exporter already initialized, skipping re-initialization")
            return

        # Use custom log exporter if provided
        if hasattr(config, "custom_log_exporter") and config.custom_log_exporter is not None:
            logger.debug("Using custom log exporter")
            self._log_exporter = config.custom_log_exporter
            logger.debug("Custom log exporter initialized successfully")
            return

        # Use default OTLP exporter
        logs_url = config.base_url.rstrip("/") + "/v1/logs"
        logger.debug("Initializing default OTLP log exporter", extra={"url": logs_url})

        headers = dict(config.headers) if config.headers else {}

        self._log_exporter = OTLPLogExporter(
            endpoint=logs_url,
            headers=headers,
        )

        logger.debug("OTLP log exporter initialized successfully")

    def _init_log_processor(self, config: BrizzConfig) -> None:
        """Initialize the log processor with masking support.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._log_processor is not None:
            logger.debug("Log processor already initialized, skipping re-initialization")
            return

        if self._log_exporter is None:
            raise RuntimeError("Log exporter must be initialized before processor")

        has_masking = (
            hasattr(config, "masking")
            and config.masking is not None
            and hasattr(config.masking, "event_masking")
            and config.masking.event_masking is not None
        )

        logger.debug(
            "Initializing log processor",
            extra={
                "disable_batch": config.disable_batch,
                "has_masking": has_masking,
            },
        )

        disable_batch = config.disable_batch
        if disable_batch:
            self._log_processor = BrizzSimpleLogRecordProcessor(self._log_exporter, config)
        else:
            self._log_processor = BrizzBatchLogRecordProcessor(self._log_exporter, config)

        logger.debug("Log processor initialized successfully")

    def _init_logger_provider(self, config: BrizzConfig) -> None:
        """Initialize the logger provider.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._logger_provider is not None:
            logger.debug("Logger provider already initialized, skipping re-initialization")
            return

        if self._log_processor is None:
            raise RuntimeError("Log processor must be initialized before logger provider")

        logger.debug("Creating resource with service name", extra={"service_name": config.app_name})

        resource_attrs = {SERVICE_NAME: config.app_name}

        # Add environment attribute if specified
        if config.environment:
            resource_attrs[DEPLOYMENT_ENVIRONMENT] = config.environment

        # Add SDK version and language
        resource_attrs[BRIZZ_SDK_VERSION] = get_version()
        resource_attrs[BRIZZ_SDK_LANGUAGE] = SDK_LANGUAGE

        resource = Resource.create(resource_attrs)

        logger.debug("Creating logger provider with resource")
        self._logger_provider = LoggerProvider(
            resource=resource,
        )
        self._logger_provider.add_log_record_processor(self._log_processor)

        logger.debug("Logger provider initialization completed")

    def emit_event(
        self,
        name: str,
        attributes: dict[str, str | int | float | bool] | None = None,
        body: Any = None,
        severity_number: SeverityNumber = SeverityNumber.INFO,
    ) -> None:
        """Emit a custom event to the telemetry pipeline.

        Args:
            name: Event name (required)
            attributes: Optional attributes for the event
            body: Optional body content for the event
            severity_number: Severity level of the event, defaults to INFO

        Raises:
            RuntimeError: If logging module is not initialized
        """
        logger.debug(
            "Attempting to emit event",
            extra={
                "event_name": name,
                "has_attributes": attributes is not None,
                "attributes_count": len(attributes) if attributes else 0,
                "has_body": body is not None,
                "severity_number": severity_number,
            },
        )

        if self._logger_provider is None:
            logger.error("Cannot emit event: Logger provider not initialized")
            raise RuntimeError("Logging module not initialized")

        # Prepare log attributes with event name as required field
        log_attributes: dict[str, str | int | float | bool] = {"event.name": name}
        if attributes:
            log_attributes.update(attributes)
            logger.debug("Combined log attributes", extra={"attributes": list(log_attributes.keys())})

        # Add association properties from current context directly
        association_properties = context.get_value(PROPERTIES_CONTEXT_KEY)
        if association_properties and hasattr(association_properties, "items"):
            for key, value in association_properties.items():
                log_attributes[f"{BRIZZ}.{key}"] = str(value)

        # Get logger instance for event emission
        logger.debug("Getting logger instance for brizz.events")
        event_logger = self._logger_provider.get_logger("brizz.events")

        # Emit the event
        logger.debug("Emitting log record with eventName", extra={"event_name": name})
        try:
            event_logger.emit(
                body=body,
                attributes=log_attributes,
                context=context.get_current(),
                severity_number=severity_number,
            )
            logger.debug("Event successfully emitted", extra={"event_name": name})
        except Exception as error:
            logger.error(f"Failed to emit event '{name}'", extra={"error": str(error), "event_name": name})
            logger.error(
                "Log record that failed",
                extra={
                    "event_name": name,
                    "attributes": log_attributes,
                    "severity_number": severity_number,
                    "has_body": body is not None,
                },
            )
            raise

    def is_initialized(self) -> bool:
        """Check if the module is initialized.

        Returns:
            True if logger provider is initialized, False otherwise
        """
        return self._logger_provider is not None

    def get_logger_provider(self) -> LoggerProvider | None:
        """Get the logger provider.

        Returns:
            Logger provider instance or None if not initialized
        """
        return self._logger_provider

    def shutdown(self) -> None:
        """Shutdown the logging module."""
        logger.debug("Shutting down logging module")

        if self._logger_provider:
            self._logger_provider.shutdown()  # type: ignore[no-untyped-call]

        if self._log_processor:
            self._log_processor.shutdown()  # type: ignore[no-untyped-call]

        if self._log_exporter:
            self._log_exporter.shutdown()

        self._logger_provider = None
        self._log_processor = None
        self._log_exporter = None
        # Reset singleton state
        LoggingModule._instance = None
        LoggingModule._initialized = False

        logger.debug("Logging module shutdown completed")


def emit_event(
    name: str,
    attributes: dict[str, str | int | float | bool] | None = None,
    body: Any = None,
    severity_number: SeverityNumber = SeverityNumber.INFO,
) -> None:
    """Emit a custom event to the telemetry pipeline.

    Args:
        name: Event name (required)
        attributes: Optional attributes for the event
        body: Optional body content for the event
        severity_number: Severity level of the event, defaults to INFO

    Raises:
        RuntimeError: If SDK is not initialized
    """
    return LoggingModule.get_instance().emit_event(name, attributes, body, severity_number)
