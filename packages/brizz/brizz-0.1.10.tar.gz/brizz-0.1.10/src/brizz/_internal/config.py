"""Configuration management for Brizz SDK."""

import json
import logging
import os
import sys
from typing import Any

from opentelemetry.sdk._logs.export import LogExporter, LogRecordExporter
from opentelemetry.sdk.metrics.export import MetricReader
from opentelemetry.sdk.trace.export import SpanExporter
from pydantic import BaseModel, Field, PrivateAttr, SecretStr, field_validator, model_validator

from brizz._internal.models import MaskingConfig

logger = logging.getLogger("brizz._internal.config")


class BrizzConfig(BaseModel):
    """Brizz SDK configuration with environment variable resolution."""

    app_name: str = Field(..., description="Application name")
    base_url: str = Field(..., description="Base URL for telemetry endpoints")
    api_key: SecretStr | None = Field(default=None, description="Brizz API key", exclude=True)
    headers: dict[str, str] = Field(default_factory=dict, description="Additional headers")
    disable_batch: bool = Field(default=False, description="Whether to disable batch processing")
    resource_attributes: dict[str, Any] = Field(default_factory=dict, description="Additional resource attributes")
    environment: str | None = Field(
        default=None, description="Deployment environment (e.g., 'production', 'staging', 'development')"
    )
    masking: MaskingConfig | bool = Field(default=False, description="Masking configuration")
    _masking: MaskingConfig = PrivateAttr(default_factory=MaskingConfig)
    log_level: int = Field(default=logging.INFO, description="Python logging level")
    allowed_instrumentations: list[str] | None = Field(
        default=None,
        description="Explicit whitelist of instrumentation names to enable. "
        "If set, blocked_instrumentations is ignored. "
        "If None, uses default AI packages with blocked_instrumentations applied. "
        "If empty list, disables all instrumentation.",
    )
    blocked_instrumentations: list[str] = Field(
        default=["urllib", "urllib3", "requests", "httpx", "aiohttp_client"],
        description="List of instrumentation module names to block (e.g., 'urllib', 'requests'). "
        "Only applied when allowed_instrumentations is None.",
    )
    custom_span_exporter: SpanExporter | None = Field(default=None, description="Custom span exporter for testing")
    custom_log_exporter: LogExporter | LogRecordExporter | None = Field(
        default=None, description="Custom log exporter for testing"
    )
    custom_metric_reader: MetricReader | None = Field(default=None, description="Custom metric reader for testing")

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, v: str) -> str:
        """Validate app_name is not empty."""
        if not v.strip():
            raise ValueError("app_name cannot be empty")
        return v

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base_url is not empty and is a valid HTTP/HTTPS URL."""
        if not v.strip():
            raise ValueError("base_url cannot be empty")
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("base_url must be a valid HTTP/HTTPS URL")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: int) -> int:
        """Validate log_level is a valid Python logging level."""
        valid_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v

    @model_validator(mode="after")
    def resolve_masking_and_auth(self) -> "BrizzConfig":
        """Resolve masking config and add Authorization header if API key is present."""
        # Resolve masking configuration
        if isinstance(self.masking, bool):
            self._masking = MaskingConfig.from_bool(self.masking)
        elif isinstance(self.masking, MaskingConfig):
            self._masking = self.masking
        else:
            self._masking = MaskingConfig()

        # Add Authorization header if API key is present
        if self.api_key:
            self.headers = dict(self.headers)  # Make a copy to avoid mutating default
            self.headers["Authorization"] = f"Bearer {self.api_key.get_secret_value()}"
        return self

    @property
    def traces_endpoint(self) -> str:
        """Get the traces endpoint URL."""
        return self.base_url.rstrip("/") + "/v1/traces"

    @property
    def logs_endpoint(self) -> str:
        """Get the log endpoint URL."""
        return self.base_url.rstrip("/") + "/v1/logs"


def _parse_log_level(level_str: str) -> int:
    """Parse a string log level into Python logging level constant.

    Args:
        level_str: Log level string (case insensitive)

    Returns:
        Python logging level constant

    Raises:
        ValueError: If log level is not recognized
    """
    level_lower = level_str.lower().strip()

    level_mapping = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "warn": logging.WARNING,  # Alias
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    if level_lower in level_mapping:
        return level_mapping[level_lower]
    else:
        raise ValueError(f"Invalid log level: {level_str}")


def resolve_config(
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
    custom_span_exporter: SpanExporter | None = None,
    custom_log_exporter: LogExporter | LogRecordExporter | None = None,
    custom_metric_reader: MetricReader | None = None,
    **kwargs: Any,  # Accept additional options for future compatibility
) -> BrizzConfig:
    """Create configuration with environment variable overrides.

    Environment variables have highest precedence, followed by explicit parameters,
    then defaults.

    Args:
        app_name: Application name (defaults to sys.argv[0])
        base_url: Base URL for telemetry endpoints
        api_key: Brizz API key
        headers: Additional headers
        disable_batch: Whether to disable batch processing
        resource_attributes: Additional resource attributes
        environment: Deployment environment (e.g., 'production', 'staging', 'development')
        masking: Masking configuration (bool or MaskingConfig)
        log_level: Log level as string or int constant from logging module
        allowed_instrumentations: Explicit whitelist of instrumentation names to enable.
            If set, blocked_instrumentations is ignored.
            If None, uses default AI packages with blocked_instrumentations applied.
            If empty list, disables all instrumentation.
        blocked_instrumentations: List of instrumentation names to block.
            Only applied when allowed_instrumentations is None.
        custom_span_exporter: Custom span exporter for testing
        custom_log_exporter: Custom log exporter for testing
        custom_metric_reader: Custom metric reader for testing
        **kwargs: Additional options for future compatibility

    Returns:
        BrizzConfig instance with resolved values

    Raises:
        ValueError: If required configuration is missing or invalid
    """
    # Resolve log level first so we can initialize logging before any debug logs
    # This ensures config resolution logs will be visible
    env_log_level = os.getenv("BRIZZ_LOG_LEVEL")
    resolved_log_level = logging.INFO  # Default

    if env_log_level:
        resolved_log_level = _parse_log_level(env_log_level)
    elif isinstance(log_level, str):
        resolved_log_level = _parse_log_level(log_level)
    elif isinstance(log_level, int):
        resolved_log_level = log_level

    # Set the global log level for the brizz logger
    logging.getLogger("brizz").setLevel(resolved_log_level)
    logging.getLogger("opentelemetry").setLevel(resolved_log_level)

    # Log configuration parameters before resolving (excluding sensitive data)
    logger.debug(
        "Resolving configuration with parameters: %s",
        {
            "app_name": app_name,
            "base_url": base_url,
            "api_key_provided": api_key is not None,
            "headers_count": len(headers) if headers else 0,
            "disable_batch": disable_batch,
            "resource_attributes_count": len(resource_attributes) if resource_attributes else 0,
            "masking_type": type(masking).__name__ if masking is not None else None,
            "log_level": log_level,
            "resolved_log_level": resolved_log_level,
            "allowed_instrumentations": allowed_instrumentations,
            "blocked_instrumentations_count": len(blocked_instrumentations) if blocked_instrumentations else 0,
            "custom_exporters": {
                "span_exporter": custom_span_exporter is not None,
                "log_exporter": custom_log_exporter is not None,
                "metric_reader": custom_metric_reader is not None,
            },
        },
    )

    # Resolve masking configuration
    resolved_masking: MaskingConfig | bool
    if masking is True:
        # Enable masking with all defaults
        resolved_masking = True
    elif isinstance(masking, MaskingConfig):
        # Use provided masking config
        resolved_masking = masking
    elif masking is False:
        # Explicitly disable masking
        resolved_masking = False
    else:
        # Default masking (disabled)
        resolved_masking = False

    # Resolve app_name with environment override
    final_app_name = os.getenv("BRIZZ_APP_NAME") or app_name or sys.argv[0]

    # Resolve base URL
    final_base_url = os.getenv("BRIZZ_BASE_URL") or base_url

    # Resolve API key
    final_api_key_str = os.getenv("BRIZZ_API_KEY") or api_key
    final_api_key = SecretStr(final_api_key_str) if final_api_key_str is not None else None

    # Resolve headers
    final_headers = (headers or {}).copy()
    if headers_env := os.getenv("BRIZZ_HEADERS"):
        try:
            env_headers = json.loads(headers_env)
            if isinstance(env_headers, dict):
                final_headers.update(env_headers)
            else:
                raise ValueError("BRIZZ_HEADERS must be a JSON object")
        except json.JSONDecodeError as e:
            logger.error("Failed to parse BRIZZ_HEADERS environment variable: %s", e)
            raise ValueError("Invalid JSON in BRIZZ_HEADERS environment variable") from e

    # Resolve disable_batch
    final_disable_batch = disable_batch
    if batch_env := os.getenv("BRIZZ_DISABLE_BATCH"):
        final_disable_batch = batch_env.lower() == "true"

    # Resolve blocked_instrumentations
    final_blocked_instrumentations = (
        blocked_instrumentations
        if blocked_instrumentations is not None
        else ["urllib", "urllib3", "requests", "httpx", "aiohttp_client"]
    )

    # Resolve environment
    final_environment = os.getenv("BRIZZ_ENVIRONMENT") or environment

    # Resolve resource attributes
    final_resource_attributes = resource_attributes or {}

    config = BrizzConfig(
        app_name=final_app_name,
        base_url=final_base_url,
        api_key=final_api_key,
        headers=final_headers,
        disable_batch=final_disable_batch,
        resource_attributes=final_resource_attributes,
        environment=final_environment,
        masking=resolved_masking,
        log_level=resolved_log_level,
        allowed_instrumentations=allowed_instrumentations,
        blocked_instrumentations=final_blocked_instrumentations,
        custom_span_exporter=custom_span_exporter,
        custom_log_exporter=custom_log_exporter,
        custom_metric_reader=custom_metric_reader,
    )

    logger.debug(
        "Configuration resolved successfully: %s",
        config.model_dump(exclude={"custom_span_exporter", "custom_log_exporter", "custom_metric_reader"}),
    )

    return config
