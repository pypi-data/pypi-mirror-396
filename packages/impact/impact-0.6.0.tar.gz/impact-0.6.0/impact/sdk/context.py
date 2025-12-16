from __future__ import annotations
from typing import Any
from contextvars import ContextVar, Token
from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor

# Context-scoped variables (safe for threads/async)
_assoc_props: ContextVar[dict[str, Any] | None] = ContextVar("impact.context", default=None)
_entity_path: ContextVar[str | None] = ContextVar("impact.decorator.path", default=None)

_enabled = False

class _ContextSpanProcessor(SpanProcessor):
    def on_start(self, span, parent_context):
        ep = _entity_path.get()
        if ep is not None:
            span.set_attribute("impact.decorator.path", ep)

        ap = _assoc_props.get()
        if ap:
            for k, v in ap.items():
                span.set_attribute(f"impact.context.{k}", v)

    def on_end(self, span: ReadableSpan):
        pass

def enable_context_processor():
    global _enabled
    if _enabled:
        return
    provider = trace.get_tracer_provider()
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(_ContextSpanProcessor())
        _enabled = True

def merge_context_properties(properties: dict[str, Any]):
    cur = _assoc_props.get() or {}
    new = dict(cur)
    new.update(properties)
    _assoc_props.set(new)

def current_entity_path() -> str | None:
    return _entity_path.get()

def push_entity(entity_name: str) -> Token:
    current = _entity_path.get()
    new_path = f"{current}.{entity_name}" if current else entity_name
    return _entity_path.set(new_path)

def pop_entity(token: Token):
    try:
        _entity_path.reset(token)
    except (ValueError, LookupError, RuntimeError):
        pass
