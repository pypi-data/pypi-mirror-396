"""Main metrics module for Brizz SDK."""

from typing import Optional, cast

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import MetricExporter, MetricReader, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from ..config import BrizzConfig
from ..log.logging import get_logger

logger = get_logger(__name__)


class MetricsModule:
    """Main metrics module for Brizz SDK with singleton pattern."""

    _instance: Optional["MetricsModule"] = None
    _initialized: bool = False

    def __new__(cls) -> "MetricsModule":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if not self._initialized:
            self._metrics_exporter: MetricExporter | None = None
            self._metrics_reader: MetricReader | None = None
            self._meter_provider: MeterProvider | None = None
            MetricsModule._initialized = True

    @classmethod
    def get_instance(cls) -> "MetricsModule":
        """Get the singleton instance of MetricsModule.

        Raises:
            RuntimeError: If Brizz SDK is not initialized
        """
        if cls._instance is None:
            raise RuntimeError("Brizz must be initialized before accessing MetricsModule")
        return cls._instance

    def setup(self, config: BrizzConfig) -> None:
        """Initialize the metrics module with the provided configuration.

        Args:
            config: Resolved Brizz SDK configuration
        """
        logger.info("Setting up metrics module")

        # Initialize reader (custom or default with exporter)
        self._init_metrics_reader(config)

        # Initialize MeterProvider
        self._init_meter_provider(config)

        # Set as module instance for standalone functions
        MetricsModule._instance = self

        logger.info("Metrics module setup completed")

    def _init_metrics_exporter(self, config: BrizzConfig) -> None:
        """Initialize the metrics exporter.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._metrics_exporter is not None:
            logger.debug("Metrics exporter already initialized, skipping re-initialization")
            return

        metrics_url = config.base_url.rstrip("/") + "/v1/metrics"
        logger.debug("Initializing metrics exporter", extra={"url": metrics_url})

        headers = dict(config.headers) if config.headers else {}

        self._metrics_exporter = OTLPMetricExporter(
            endpoint=metrics_url,
            headers=headers,
        )

        logger.debug("Metrics exporter initialized successfully")

    def _init_metrics_reader(self, config: BrizzConfig) -> None:
        """Initialize the metrics reader.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._metrics_reader is not None:
            logger.debug("Metrics reader already initialized, skipping re-initialization")
            return

        # Use custom metric reader if provided
        if hasattr(config, "custom_metric_reader") and config.custom_metric_reader is not None:
            logger.debug("Using custom metric reader")
            self._metrics_reader = config.custom_metric_reader
            logger.debug("Custom metric reader initialized successfully")
            return

        # Use default flow: create OTLP exporter and wrap it in PeriodicExportingMetricReader
        logger.debug("Using default metrics flow - creating OTLP exporter and PeriodicExportingMetricReader")
        self._init_metrics_exporter(config)

        if self._metrics_exporter is None:
            raise RuntimeError("Failed to initialize metrics exporter")

        self._metrics_reader = PeriodicExportingMetricReader(
            exporter=self._metrics_exporter,
        )

        logger.debug("Default metrics reader initialized successfully")

    def _init_meter_provider(self, config: BrizzConfig) -> None:
        """Initialize and register the MeterProvider globally.

        Args:
            config: Resolved Brizz SDK configuration
        """
        if self._meter_provider is not None:
            logger.debug("MeterProvider already initialized, skipping re-initialization")
            return

        if self._metrics_reader is None:
            raise RuntimeError("Metrics reader must be initialized before MeterProvider")

        logger.debug("Initializing MeterProvider")

        # Try to get existing MeterProvider from the SDK
        existing_provider = metrics.get_meter_provider()
        use_existing_provider = False

        # Check if it's a real MeterProvider from the SDK that we can add readers to
        if existing_provider and hasattr(existing_provider, "add_metric_reader"):
            logger.info("Existing SDK MeterProvider found - adding Brizz metric reader to it")
            try:
                existing_provider.add_metric_reader(self._metrics_reader)
                # Cast the generic MeterProvider interface to SDK MeterProvider
                self._meter_provider = cast(MeterProvider, existing_provider)
                use_existing_provider = True
                logger.info(f"Brizz metric reader added to existing MeterProvider for service: {config.app_name}")
            except Exception as e:
                logger.warning(f"Failed to add metric reader to existing provider: {e}")
                logger.info("Creating new MeterProvider instead")

        if not use_existing_provider:
            logger.debug("No existing SDK MeterProvider found - creating new one")

            # Create resource with app_name and additional attributes
            resource_attrs = {SERVICE_NAME: config.app_name}
            resource_attrs.update(config.resource_attributes)
            resource = Resource.create(resource_attrs)

            # Create MeterProvider with resource and metric reader
            self._meter_provider = MeterProvider(resource=resource, metric_readers=[self._metrics_reader])

            # Set as global MeterProvider
            metrics.set_meter_provider(self._meter_provider)
            logger.info(f"New MeterProvider initialized and registered globally for service: {config.app_name}")

    def get_metrics_exporter(self) -> MetricExporter:
        """Get the metrics exporter.

        Returns:
            The initialized metrics exporter

        Raises:
            RuntimeError: If metrics module is not initialized
        """
        if self._metrics_exporter is None:
            raise RuntimeError("Metrics module not initialized")
        return self._metrics_exporter

    def get_metrics_reader(self) -> MetricReader:
        """Get the metrics reader.

        Returns:
            The initialized metrics reader

        Raises:
            RuntimeError: If metrics module is not initialized
        """
        if self._metrics_reader is None:
            raise RuntimeError("Metrics module not initialized")
        return self._metrics_reader

    def shutdown(self) -> None:
        """Shutdown the metrics module."""
        logger.debug("Shutting down metrics module")

        if self._meter_provider and hasattr(self._meter_provider, "shutdown"):
            self._meter_provider.shutdown()

        if self._metrics_reader and hasattr(self._metrics_reader, "shutdown"):
            self._metrics_reader.shutdown()

        if self._metrics_exporter and hasattr(self._metrics_exporter, "shutdown"):
            self._metrics_exporter.shutdown()

        self._meter_provider = None
        self._metrics_exporter = None
        self._metrics_reader = None

        # Reset singleton state
        MetricsModule._instance = None
        MetricsModule._initialized = False

        logger.debug("Metrics module shutdown completed")


def get_metrics_exporter() -> MetricExporter:
    """Get the OpenTelemetry Metrics Exporter configured for Brizz.

    Returns:
        The configured metrics exporter

    Raises:
        RuntimeError: If SDK is not initialized
    """
    return MetricsModule.get_instance().get_metrics_exporter()


def get_metrics_reader() -> MetricReader:
    """Get the Metrics Reader configured for Brizz.

    Returns:
        The configured metrics reader

    Raises:
        RuntimeError: If SDK is not initialized
    """
    return MetricsModule.get_instance().get_metrics_reader()
