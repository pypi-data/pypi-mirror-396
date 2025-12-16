"""Simple OpenAI integration example with Brizz SDK."""

import os
import sys

from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from brizz import Brizz

# Initialize SDK
Brizz.initialize(
    base_url="http://localhost:4318",
    disable_batch=True,
    app_name="openai-example",
)

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    print("Set OPENAI_API_KEY environment variable")
    sys.exit(1)

# Create OpenAI client
client = OpenAI()

# Make AI request with automatic instrumentation
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[ChatCompletionUserMessageParam(role="user", content="What is 2+2?")],
)

print(f"AI Response: {response.choices[0].message.content}")

# Emit custom event
Brizz.emit_event(
    name="ai.request_completed",
    attributes={"model": "gpt-3.5-turbo", "success": True},
)
