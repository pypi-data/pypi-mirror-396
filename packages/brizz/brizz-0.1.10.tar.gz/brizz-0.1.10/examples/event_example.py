"""Simple event emission example for Brizz Python SDK."""

from brizz import Brizz

# Initialize the SDK
Brizz.initialize(base_url="http://localhost:4318", disable_batch=True, app_name="my-python-app")

# Simple event
Brizz.emit_event(name="app.started")

# Event with attributes and body
Brizz.emit_event(
    name="user.action", attributes={"user_id": "123", "action": "login"}, body={"timestamp": "2024-01-15T10:30:00Z"}
)
