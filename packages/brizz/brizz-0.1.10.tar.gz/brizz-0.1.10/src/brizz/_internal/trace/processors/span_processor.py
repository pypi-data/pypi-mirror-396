"""Span processors with masking support for Brizz SDK."""

import logging

from opentelemetry import context
from opentelemetry.context import Context
from opentelemetry.sdk.trace import Span
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    SpanExporter,
)

from brizz._internal.models import AttributesMaskingRule, SpanMaskingConfig

from ...config import BrizzConfig
from ...masking.patterns import DEFAULT_PII_PATTERN_ENTRIES
from ...masking.utils import mask_attributes
from ...semantic_conventions import BRIZZ, PROPERTIES_CONTEXT_KEY

logger = logging.getLogger("brizz.masking")

# Default span masking rules
DEFAULT_MASKING_RULES = [
    AttributesMaskingRule(
        attribute_pattern="gen_ai.prompt",
        mode="partial",
        patterns=DEFAULT_PII_PATTERN_ENTRIES,
    ),
    AttributesMaskingRule(
        attribute_pattern="gen_ai.completion",
        mode="partial",
        patterns=DEFAULT_PII_PATTERN_ENTRIES,
    ),
    AttributesMaskingRule(
        attribute_pattern="traceloop.entity.input",
        mode="partial",
        patterns=DEFAULT_PII_PATTERN_ENTRIES,
    ),
    AttributesMaskingRule(
        attribute_pattern="traceloop.entity.output",
        mode="partial",
        patterns=DEFAULT_PII_PATTERN_ENTRIES,
    ),
]


class BrizzSimpleSpanProcessor(SimpleSpanProcessor):
    """Simple span processor with masking and context support."""

    def __init__(
        self,
        span_exporter: SpanExporter,
        config: BrizzConfig,
    ) -> None:
        super().__init__(span_exporter)
        self.config = config

    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        """Called when a span starts - applies masking and context association."""
        # Apply masking if configured
        masking_config = getattr(self.config.masking, "span_masking", None) if self.config.masking else None
        if masking_config:
            try:
                span = _mask_span(span, masking_config)
            except Exception as error:
                logger.error("Error in span masking during on_start: %s", error)

        # Add association properties from context
        association_properties = context.get_value(PROPERTIES_CONTEXT_KEY)
        if association_properties and hasattr(association_properties, "items"):
            for key, value in association_properties.items():
                span.set_attribute(f"{BRIZZ}.{key}", value)

        super().on_start(span, parent_context)


class BrizzBatchSpanProcessor(BatchSpanProcessor):
    """Batch span processor with masking and context support."""

    def __init__(
        self,
        span_exporter: SpanExporter,
        config: BrizzConfig,
    ) -> None:
        super().__init__(span_exporter)
        self.config = config

    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        """Called when a span starts - applies masking and context association."""
        # Apply masking if configured
        masking_config = getattr(self.config.masking, "span_masking", None) if self.config.masking else None
        if masking_config:
            try:
                span = _mask_span(span, masking_config)
            except Exception as error:
                logger.error("Error in span masking during on_start: %s", error)

        # Add association properties from context
        association_properties = context.get_value(PROPERTIES_CONTEXT_KEY)
        if association_properties and hasattr(association_properties, "items"):
            for key, value in association_properties.items():
                span.set_attribute(f"{BRIZZ}.{key}", value)

        super().on_start(span, parent_context)


def _mask_span(span: Span, config: SpanMaskingConfig) -> Span:
    """Apply masking to a span based on the provided configuration."""
    if not span.attributes:
        return span

    # Get masking rules
    rules = config.rules if config.rules else []
    if not getattr(config, "disable_default_rules", False):
        rules = rules + DEFAULT_MASKING_RULES

    try:
        # Apply masking to attributes
        masked_attributes = mask_attributes(span.attributes, rules, getattr(config, "_output_original_value", False))

        # Update span attributes
        span.set_attributes(masked_attributes)
        return span

    except Exception as error:
        logger.error("Error masking span: %s", error)
        return span
