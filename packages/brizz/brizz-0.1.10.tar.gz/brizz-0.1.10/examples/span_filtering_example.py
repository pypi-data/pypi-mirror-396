"""Simple span filtering and PII masking example for Brizz SDK."""

import os
import sys

from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from brizz import AttributesMaskingRule, Brizz, MaskingConfig, SpanMaskingConfig

# Option 1: Enable default masking (emails, phones, API keys, etc.)
# Brizz.initialize(
#     base_url="http://localhost:4318",
#     app_name="pii-masking-example",
#     masking=True,  # Simple boolean - enables all default patterns
# )

# Option 2: Custom masking configuration
masking_config = MaskingConfig(
    span_masking=SpanMaskingConfig(
        disable_default_rules=False,  # Keep built-in PII patterns
        rules=[
            AttributesMaskingRule(
                attribute_pattern=r"gen_ai\.(prompt|completion)",
                mode="partial",
                patterns=[r"REF-\d{4}-\d{4}", r"TKT-\d{4}-\d{3}"],
            )
        ],
    )
)

# Initialize SDK with custom masking config
Brizz.initialize(
    base_url="http://localhost:4318",
    app_name="pii-masking-example",
    disable_batch=True,
    masking=masking_config,
)

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("Set OPENAI_API_KEY environment variable")
    sys.exit(1)

# Create OpenAI client
client = OpenAI()

# AI request with PII - will be automatically masked in telemetry
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        ChatCompletionUserMessageParam(
            role="user", content="Help customer john.doe@company.com with ticket REF-2024-1234. Phone: 555-123-4567"
        )
    ],
)

print(f"AI Response: {response.choices[0].message.content}")
print("✓ PII in prompts/responses automatically masked in telemetry")
