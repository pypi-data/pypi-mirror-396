import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from brizz._internal.models import AttributesMaskingRule, PatternEntry, _PatternBasedMaskingRule

logger = logging.getLogger("brizz.masking")


def _compile_pattern_entries(
    pattern_entries: Sequence[PatternEntry],
) -> re.Pattern[str]:
    """Compile a list of pattern entries into a single regex pattern."""
    pattern_groups = []
    for pattern_entry in pattern_entries:
        pattern_groups.append(pattern_entry.get_grouped_pattern())

    return re.compile("|".join(pattern_groups))


def mask_value_str_by_pattern(value: str, pattern: re.Pattern[str], mode: Literal["partial", "full"] = "full") -> str:
    """Mask a string value based on the pattern."""
    # Use finditer to find all matches and process them in reverse order
    # to avoid index shifting when replacing
    matches = list(pattern.finditer(value))

    # Process matches in reverse order to maintain correct indices
    for match in reversed(matches):
        # Get the pattern name from lastgroup
        pattern_name = match.lastgroup
        if pattern_name:
            # Remove any counter suffix for logging
            original_name = (
                pattern_name.split("_")[0] if "_" in pattern_name and pattern_name[-1].isdigit() else pattern_name
            )
            logger.info("Masking detected: pattern '%s' found match in value", original_name)

            # Apply masking based on mode
            start, end = match.span()
            masked = match.group(0)[0] + "*****" if mode == "partial" else "*****"

            # Replace the matched portion
            value = value[:start] + masked + value[end:]

    return value


def mask_value_str_by_pattern_based_rule(value: str, rule: _PatternBasedMaskingRule) -> str:
    """Mask a string value based on the rule."""
    pattern_entries = rule.get_pattern_entries()
    if not pattern_entries:
        # No patterns means mask entire value
        mode = rule.get_mode()
        return value[0] + "*****" if mode == "partial" and value else "*****"

    # Create the mega pattern
    compiled_pattern_entries = _compile_pattern_entries(pattern_entries)

    return mask_value_str_by_pattern(value, pattern=compiled_pattern_entries, mode=rule.get_mode())


def mask_value(
    value: Any,
    rule: _PatternBasedMaskingRule,
) -> Any:
    """Mask a value based on the rule."""
    if isinstance(value, str):
        return mask_value_str_by_pattern_based_rule(value, rule)
    elif isinstance(value, bool | int | float):
        return mask_value_str_by_pattern_based_rule(str(value), rule)
    elif isinstance(value, Mapping):
        # If the value is a dictionary, mask each value recursively
        return {k: mask_value(v, rule) for k, v in value.items()}
    elif isinstance(value, (list | tuple)):
        # If the value is a list or tuple, mask each item recursively
        return type(value)(mask_value(v, rule) for v in value)
    else:
        # For unsupported types, return the value as is
        logger.warning("Unsupported type for masking: %s", type(value))
        return value


def mask_attributes(
    attributes: Mapping[str, Any],
    rules: Sequence[AttributesMaskingRule],
    output_original_value: bool = False,
) -> dict[str, Any]:
    """Mask sensitive data in attributes based on masking rules.

    Args:
        attributes: Dictionary of attributes to mask
        rules: List of masking rules to apply
        output_original_value: Whether to log original values before masking

    Returns:
        A new dictionary with masked attributes
    """
    if not attributes:
        return {}

    # Create a copy to avoid modifying the original
    masked_attributes = dict(attributes)

    for rule in rules:
        attribute_pattern = rule._compiled_attribute_pattern
        if attribute_pattern:
            # Use regex pattern matching for attributes
            attributes_to_mask = [attr for attr in masked_attributes if attribute_pattern.search(attr)]
        else:
            # Apply to all attributes
            attributes_to_mask = list(masked_attributes.keys())

        for attribute in attributes_to_mask:
            value = masked_attributes.get(attribute)
            if value is None:
                continue

            if output_original_value:
                logger.debug("Masking attribute '%s' with original value: %s", attribute, value)

            masked_value = mask_value(value, rule)
            masked_attributes[attribute] = masked_value

    return masked_attributes
