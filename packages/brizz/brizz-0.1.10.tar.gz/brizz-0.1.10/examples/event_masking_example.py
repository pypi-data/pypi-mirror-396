"""Simple event masking example for Brizz SDK."""

from brizz import Brizz
from brizz._internal.models import (
    EventMaskingConfig,
    EventMaskingRule,
    MaskingConfig,
)

# Option 1: Enable default masking (emails, phones, API keys, etc.)
# Brizz.initialize(
#     base_url="http://localhost:4318",
#     app_name="event-masking-example",
#     masking=True,  # Simple boolean - enables all default patterns
# )

# Option 2: Custom masking configuration
masking_config = MaskingConfig(
    event_masking=EventMaskingConfig(
        disable_default_rules=False,  # Keep built-in patterns
        rules=[
            EventMaskingRule(
                attribute_pattern=r"customer\.data",
                mode="partial",
                patterns=[r"CUST\d{6}"],
            )
        ],
    )
)

# Initialize SDK with custom masking config
Brizz.initialize(
    base_url="http://localhost:4318",
    disable_batch=True,
    app_name="event-masking-example",
    masking=masking_config,
)

# Event with PII that will be masked
Brizz.emit_event(
    name="customer.processed",
    attributes={
        "user.email": "user@example.com",  # Built-in PII masking
        "customer.data": "CUST123456",  # Custom pattern masking
    },
    body={
        "name": "John Doe",
        "phone": "555-123-4567",  # Built-in PII masking in body
    },
)
