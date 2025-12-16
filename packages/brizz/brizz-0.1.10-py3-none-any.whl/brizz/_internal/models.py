import re
import uuid
from collections.abc import Sequence
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator


class PatternEntry(BaseModel):
    """A pattern entry for PII detection and masking."""

    pattern: str = Field(
        ...,
        description="Regex pattern for identifying sensitive data",
    )
    name: str | None = Field(
        default=None,
        description="Name of the pattern, used for identification in masking rules",
    )
    _name: str = PrivateAttr(default=str(uuid.uuid4().hex))

    def model_post_init(self, context: Any, /) -> None:
        """Post-initialization to set the name or generate a unique one."""
        if self.name:
            self._name = self.name
        else:
            # Generate a unique name with both UUID and counter to ensure uniqueness
            self._name = f"pattern_{uuid.uuid4().hex}"

    def get_grouped_pattern(self) -> str:
        """Return the pattern wrapped in a named group."""
        # Use the name or generate a unique one if not provided
        return f"(?P<{self._name}>{self.pattern})"

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, v: str) -> str:
        """Validate that the pattern is a valid regex."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern '{v}': {e}") from e
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate that the name only contains alphanumeric characters and underscores."""
        if v is None:
            return v
        if v == "":
            raise ValueError("Pattern name cannot be empty")
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError(
                f"Pattern name '{v}' must only contain alphanumeric characters and underscores, and start with a letter"
            )
        return v


class _PatternBasedMaskingRule(Protocol):
    def get_pattern_entries(self) -> list[PatternEntry]:
        """Return the pattern entry used for masking."""
        ...

    def get_mode(self) -> Literal["partial", "full"]:
        """Return the masking mode."""
        ...


class AttributesMaskingRule(BaseModel):
    """Configuration for a single span masking rule."""

    attribute_pattern: str | None = Field(
        default=None,
        description="Field name pattern for attribute-based masking. If not provided, applies to all attributes.",
    )
    patterns: Sequence[str | PatternEntry] = Field(
        default_factory=list,
        description="Regex patterns for pattern-based masking. If empty, masks entire value.",
    )
    mode: Literal["partial", "full"] = Field(
        default="full",
        description="Masking mode: partial (e.g., jo***@gmail.com), full (e.g., *****)",
    )
    _patterns: list[PatternEntry] = PrivateAttr(default_factory=list)
    _compiled_attribute_pattern: re.Pattern[str] | None = PrivateAttr(default=None)

    def model_post_init(self, __context: dict[str, object] | None = None) -> None:
        """Validate and compile the pattern after model initialization."""
        if self.attribute_pattern:
            if isinstance(self.attribute_pattern, str):
                self._compiled_attribute_pattern = re.compile(self.attribute_pattern)
            elif isinstance(self.attribute_pattern, re.Pattern):
                self._compiled_attribute_pattern = self.attribute_pattern
            else:
                raise ValueError("Attribute pattern must be a string or compiled regex pattern")

        for pattern in self.patterns:
            if isinstance(pattern, str):
                compiled_pattern = PatternEntry(pattern=pattern)
            elif isinstance(pattern, PatternEntry):
                compiled_pattern = pattern
            else:
                raise ValueError("Patterns must be either strings or PatternEntry instances")
            self._patterns.append(compiled_pattern)

    def get_pattern_entries(self) -> list[PatternEntry]:
        """Return the list of patterns used for masking."""
        return self._patterns

    def get_mode(self) -> Literal["partial", "full"]:
        """Return the masking mode."""
        return self.mode


class EventMaskingRule(AttributesMaskingRule):
    """Configuration for a single event masking rule."""

    event_name_pattern: str | None = Field(
        default=None,
        description="Event name pattern for event-based masking. If not provided, applies to all events.",
    )

    def model_post_init(self, __context: dict[str, object] | None = None) -> None:
        """Validate and compile the event name pattern after model initialization."""
        super().model_post_init(__context)
        if self.event_name_pattern:
            # add event name pattern to compiled attribute pattern, because event name is also an attribute
            # 'event.name'
            if isinstance(self.event_name_pattern, str):
                compiled_event_name_pattern = re.compile(self.event_name_pattern)
            elif isinstance(self.event_name_pattern, re.Pattern):
                compiled_event_name_pattern = self.event_name_pattern
            else:
                raise ValueError("Event name pattern must be a string or compiled regex pattern")
            # Combine the event name pattern with the attribute pattern
            if self._compiled_attribute_pattern:
                combined_pattern = (
                    f"({self._compiled_attribute_pattern.pattern})|({compiled_event_name_pattern.pattern})"
                )
                self._compiled_attribute_pattern = re.compile(combined_pattern)

            else:
                self._compiled_attribute_pattern = compiled_event_name_pattern


class SpanMaskingConfig(BaseModel):
    """Configuration for span masking behavior."""

    disable_default_rules: bool = False
    _output_original_value: bool = PrivateAttr(default=False)  # Test-only flag to output original value before masking
    rules: list[AttributesMaskingRule] = Field(default_factory=list)

    @classmethod
    def from_bool(cls, enabled: bool) -> "SpanMaskingConfig":
        """Create SpanMaskingConfig from boolean value."""
        if enabled:
            return cls()
        return cls(disable_default_rules=True)

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, v: list[AttributesMaskingRule]) -> list[AttributesMaskingRule]:
        """Validate rules."""
        # validate name uniqueness for pattern entries
        names: set[str] = set()
        for rule in v:
            # all patterns will be PatternEntry instances by model_post_init of AttributesMaskingRule
            for pattern in rule.patterns:
                if isinstance(pattern, PatternEntry):
                    if pattern._name in names:
                        raise ValueError(f"Pattern name '{pattern.name}' is not unique")
                    names.add(pattern._name)
        return v


class LogMaskingConfig(BaseModel):
    """Configuration for log masking behavior."""

    disable_default_rules: bool = False
    _output_original_value: bool = PrivateAttr(default=False)  # Test-only flag to output original value before masking
    rules: list[AttributesMaskingRule] = []
    mask_body: bool = Field(
        default=True,
        description="Whether to mask the body of events. If True, the body will be masked "
        "regardless of the rules defined.",
    )


class EventMaskingConfig(LogMaskingConfig):
    """Configuration for event masking behavior."""

    @classmethod
    def from_bool(cls, enabled: bool) -> "EventMaskingConfig":
        """Create EventMaskingConfig from boolean value."""
        if enabled:
            return cls()
        return cls(disable_default_rules=True)


class MaskingConfig(BaseModel):
    """Main configuration for data masking functionality."""

    span_masking: bool | SpanMaskingConfig | None = None
    event_masking: bool | EventMaskingConfig | None = None
    _span_masking: SpanMaskingConfig | None = PrivateAttr(default=None)
    _event_masking: EventMaskingConfig | None = PrivateAttr(default=None)

    @model_validator(mode="after")
    def resolve_masking_configs(self) -> "MaskingConfig":
        """Resolve boolean masking configs to actual config objects."""
        # Resolve span_masking
        if isinstance(self.span_masking, bool):
            self._span_masking = SpanMaskingConfig.from_bool(self.span_masking)
        elif isinstance(self.span_masking, SpanMaskingConfig):
            self._span_masking = self.span_masking
        else:
            self._span_masking = None

        # Resolve event_masking
        if isinstance(self.event_masking, bool):
            self._event_masking = EventMaskingConfig.from_bool(self.event_masking)
        elif isinstance(self.event_masking, EventMaskingConfig):
            self._event_masking = self.event_masking
        else:
            self._event_masking = None

        return self

    @classmethod
    def from_bool(cls, enabled: bool) -> "MaskingConfig":
        """Create MaskingConfig from boolean value."""
        if enabled:
            return cls(span_masking=True, event_masking=True)
        return cls(span_masking=False, event_masking=False)
