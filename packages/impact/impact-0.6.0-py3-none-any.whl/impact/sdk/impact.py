from __future__ import annotations
import os
import sys
from typing import Any, TYPE_CHECKING

from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from .otel import setup_tracing
from .context import enable_context_processor, merge_context_properties
from .registry import auto_instrument_all, instrument_httpx
from .decorators import workflow, task, agent, tool

if TYPE_CHECKING:
    from typing import Protocol
    
    class ASGIApp(Protocol):
        async def __call__(self, scope, receive, send): ...

def init(
    *,
    api_key: str | None = None,
    api_endpoint: str | None = None,
    project_id: str | None = None,
    disable_batch: bool = False,
    disable_logs: bool = False,
) -> None:
    """Initialize OpenTelemetry tracing and auto-instrument GenAI SDKs.

    Uses HTTP-only OTLP transport to the specified endpoint.

    Args:
        api_key: API key for authentication (sets Authorization: Bearer header).
            Falls back to IMPACT_API_KEY environment variable.
        api_endpoint: Base API endpoint (REQUIRED). /v1/traces will be appended.
            Falls back to IMPACT_BASE_URL environment variable.
            Either this argument or IMPACT_BASE_URL must be specified.
        project_id: Project ID. Falls back to IMPACT_PROJECT_ID environment variable.
        disable_batch: If True, use SimpleSpanProcessor instead of BatchSpanProcessor.
        disable_logs: Skip setting up log exporter (disables GenAI message content capture).

    Raises:
        ValueError: If api_endpoint is not provided and IMPACT_BASE_URL is not set.

    Example:
        Using argument:
            impact.init(api_endpoint="https://your-endpoint.example.com")

        Using environment variable:
            export IMPACT_BASE_URL="https://your-endpoint.example.com"
            impact.init()
    """
    # Default latest GenAI semantics + Capture message content in spans and events
    os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental")
    os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")  # TODO: For Google needs to be SPAN_AND_EVENT
    os.environ.setdefault("OTEL_INSTRUMENTATION_OPENAI_AGENTS_CAPTURE_CONTENT", "true")  # Ensure Agents SDK respects content capture on spans
    os.environ.setdefault("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "true")

    # Environment variable fallbacks (explicit parameters take precedence)
    api_key = api_key or os.getenv("IMPACT_API_KEY")
    api_endpoint = api_endpoint or os.getenv("IMPACT_BASE_URL")
    project_id = project_id or os.getenv("IMPACT_PROJECT_ID")

    # Validate required api_endpoint
    if not api_endpoint:
        raise ValueError(
            "api_endpoint is required. Either pass it as an argument to init() "
            "or set the IMPACT_BASE_URL environment variable."
        )

    # Programmatic headers
    headers = {}
    if api_key:
        headers["authorization"] = f"Bearer {api_key}"

    # Setup tracing
    setup_tracing(
        service_name=os.getenv("OTEL_SERVICE_NAME") or (sys.argv[0] or "impact-app"),
        service_version=None,
        environment=os.getenv("DEPLOYMENT_ENVIRONMENT") or os.getenv("ENVIRONMENT") or "prod",
        api_endpoint=api_endpoint,
        headers=headers,
        disable_batch=disable_batch,
        disable_logs=disable_logs,
    )

    # Enable HTTP context propagation (W3C Trace Context)
    set_global_textmap(TraceContextTextMapPropagator())

    # Enable context propagation
    enable_context_processor()

    # Enable thread context propagation
    ThreadingInstrumentor().instrument()

    # Auto-instrument HTTPX HTTP client for outbound requests
    instrument_httpx()

    # Auto-instrument supported GenAI SDKs
    auto_instrument_all()

def impact_context(*, user_id: str | None = None, interaction_id: str | None = None, version_id: str | None = None, **extras: Any) -> None:
    """Attach context for all spans in current execution context.
    Stored as impact.context.<key>=<value>
    """
    props = {}
    if user_id is not None:
        props["user_id"] = user_id
    if interaction_id is not None:
        props["interaction_id"] = interaction_id
    if version_id is not None:
        props["version_id"] = version_id
    if extras:
        props.update(extras)

    if props:
        merge_context_properties(props)

def instrument_asgi_app(app: Any) -> Any:
    """Wrap an ASGI application with OpenTelemetry middleware.
    
    This creates root spans for incoming HTTP requests, enabling proper context
    propagation for all child spans (decorators, GenAI calls, etc.).
    
    Args:
        app: The ASGI application instance (FastAPI, Quart, Starlette, etc.)
        
    Returns:
        The wrapped application
        
    Example:
        ```python
        from quart import Quart
        import impact
        
        app = Quart(__name__)
        impact.init(api_key="...", api_endpoint="...")
        app = impact.instrument_asgi_app(app)
        ```
    
    For Quart apps, you can also wrap the asgi_app attribute:
        ```python
        app.asgi_app = impact.instrument_asgi_app(app.asgi_app)
        ```
    """
    try:
        from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
        return OpenTelemetryMiddleware(app)
    except ImportError:
        # If ASGI instrumentation not available, return app unchanged
        return app

def shutdown() -> None:
    """Flush and shutdown OpenTelemetry tracing."""
    from opentelemetry import trace
    tp = trace.get_tracer_provider()
    try:
        if hasattr(tp, 'shutdown'):
            tp.shutdown()
    except Exception:
        pass
