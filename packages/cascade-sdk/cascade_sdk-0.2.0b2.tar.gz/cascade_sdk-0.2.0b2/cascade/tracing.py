"""
Core tracing primitives for Cascade SDK
"""
import os
import contextvars
from typing import Optional, Dict, Any
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import Tracer, Status, StatusCode

# Global tracer instance
_tracer: Optional[Tracer] = None
_tracer_provider: Optional[TracerProvider] = None

# Context variable for trace metadata
_trace_metadata: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "trace_metadata", default={}
)


def init_tracing(
    project: str,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    environment: Optional[str] = None,
    version: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """
    Initialize OpenTelemetry tracing for Cascade SDK.
    
    Args:
        project: Project name (used for filtering traces)
        endpoint: OTLP endpoint URL (default: https://api.runcascade.com/v1/traces, or CASCADE_ENDPOINT env var)
        api_key: API key for authentication (optional, can also use CASCADE_API_KEY env var)
        metadata: Generic metadata dictionary for any key-value pairs (e.g., {"competition_id": "comp-123"})
        environment: Environment name (e.g., 'dev', 'prod')
        version: Application version
        user_id: User identifier for multi-user scenarios
    """
    global _tracer, _tracer_provider
    
    # Use environment variable or parameter for endpoint
    endpoint = endpoint or os.getenv("CASCADE_ENDPOINT", "https://api.runcascade.com/v1/traces")
    
    # Use environment variable or parameter for API key
    api_key = api_key or os.getenv("CASCADE_API_KEY")
    
    # Detect Modal environment
    is_modal = os.getenv("MODAL_ENVIRONMENT") is not None
    if is_modal and endpoint == "http://localhost:8000/v1/traces":
        import warnings
        warnings.warn(
            "Running in Modal environment but no CASCADE_ENDPOINT configured. "
            "Traces will not be sent. Set CASCADE_ENDPOINT to your tunnel URL.",
            UserWarning
        )
    
    # Build resource attributes
    resource_attributes = {
        "service.name": project,
        "cascade.project": project,
        "cascade.environment": environment or "local",
    }
    
    if environment:
        resource_attributes["deployment.environment"] = environment
    if version:
        resource_attributes["service.version"] = version
    if user_id:
        resource_attributes["cascade.user_id"] = user_id
    
    # Add all metadata as resource attributes with cascade. prefix
    # This allows any customer to pass any metadata they need
    if metadata:
        for key, value in metadata.items():
            resource_attributes[f"cascade.{key}"] = str(value)
    
    # Create resource
    resource = Resource.create(resource_attributes)
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    
    # Build headers for API key authentication
    headers = None
    if api_key:
        headers = {"authorization": f"Bearer {api_key}"}
    
    # Create OTLP HTTP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers=headers,
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    _tracer_provider.add_span_processor(span_processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)
    
    # Get tracer instance
    _tracer = trace.get_tracer(__name__)


def get_tracer() -> Optional[Tracer]:
    """Get the global tracer instance."""
    return _tracer


@contextmanager
def trace_run(
    name: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for tracing agent execution.
    
    Creates a root span for the agent run and maintains trace context.
    
    Args:
        name: Name of the agent/function being traced
        metadata: Additional metadata to attach to the span (e.g., session_id, user_id, request_id)
    
    Example:
        ```python
        with trace_run("MyAgent", metadata={"task_id": "123"}):
            # Your agent code here
            pass
        ```
    """
    if _tracer is None:
        raise RuntimeError(
            "Tracing not initialized. Call init_tracing() first."
        )
    
    metadata = metadata or {}
    
    # Store metadata in context
    _trace_metadata.set(metadata)
    
    # Start root span - start_as_current_span returns a context manager
    with _tracer.start_as_current_span(name, kind=trace.SpanKind.SERVER) as span_context:
        # Get the actual span from the current context
        span = trace.get_current_span()
        
        try:
            # Add metadata as span attributes
            for key, value in metadata.items():
                if value is not None:
                    span.set_attribute(f"cascade.{key}", str(value))
            
            # Set span attributes
            span.set_attribute("cascade.span_type", "function")
            
            yield span
            
            # Mark span as successful
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            # Mark span as error
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise

