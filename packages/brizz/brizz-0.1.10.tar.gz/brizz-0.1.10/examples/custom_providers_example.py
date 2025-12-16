"""Simple custom providers example for Brizz SDK."""

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider

from brizz import Brizz

# Create custom TracerProvider
resource = Resource.create({SERVICE_NAME: "my-custom-app"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Initialize Brizz with existing provider
Brizz.initialize(
    app_name="my-custom-app",
    base_url="http://localhost:4318",
    disable_batch=True,
)

# Use custom provider
tracer = trace.get_tracer("my-custom-app")
with tracer.start_as_current_span("example.operation") as span:
    span.set_attribute("custom", "value")

    # Emit event
    Brizz.emit_event(
        name="custom.provider.example",
        attributes={"success": True},
    )
