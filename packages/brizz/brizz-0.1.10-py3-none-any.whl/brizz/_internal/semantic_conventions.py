"""Semantic conventions for Brizz SDK."""

from opentelemetry.context import create_key

# Brizz namespace for attributes
BRIZZ = "brizz"

# Context key for association properties
PROPERTIES_CONTEXT_KEY = create_key("brizz.properties")

# Session ID key for context properties
SESSION_ID = "session.id"

# Session semantic conventions
SESSION_INPUT = "brizz.session.input"
SESSION_OUTPUT = "brizz.session.output"
SESSION_SPAN_NAME = "brizz.start_session"

# Brizz SDK attributes
BRIZZ_SDK_VERSION = "brizz.sdk.version"
BRIZZ_SDK_LANGUAGE = "brizz.sdk.language"

# SDK language value
SDK_LANGUAGE = "python"
