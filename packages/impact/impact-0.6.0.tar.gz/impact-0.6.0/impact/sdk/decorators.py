from __future__ import annotations
from functools import wraps
from typing import Callable, TypeVar, Any
from collections.abc import Mapping
import inspect, json, types

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from .context import push_entity, pop_entity, current_entity_path

F = TypeVar("F", bound=Callable[..., Any])

class ImpactAttributes:
    """Impact-specific attributes that complement official GenAI conventions."""
    DECORATOR_TYPE = "impact.decorator.type"  # workflow | task | agent | tool
    ENTITY_PATH = "impact.decorator.path"
    DECORATOR_PREFIX = "impact.decorator."

IA = ImpactAttributes

def _start_span(span_name: str, span_type: str, attributes: Mapping[str, Any] | None = None):
    tracer = trace.get_tracer("impact.sdk")
    attrs = {IA.DECORATOR_TYPE: span_type}
    if attributes:
        attrs.update(attributes)
    return tracer.start_as_current_span(span_name, attributes=attrs)
 

def _capture_io(span, args, kwargs, result_marker=None):
    try:
        span.set_attribute("impact.decorator.input", json.dumps({"args": args, "kwargs": kwargs}, default=str))
        if result_marker is not None:
            span.set_attribute("impact.decorator.output", json.dumps(result_marker, default=str))
    except Exception:
        # best-effort only
        pass

def _wrap_body(span_name: str, span_type: str, func: F, custom_attributes: Mapping[str, Any] | None = None):
    is_async = inspect.iscoroutinefunction(func)
    is_async_gen = inspect.isasyncgenfunction(func)
    is_gen = inspect.isgeneratorfunction(func)

    if custom_attributes:
        attrs = {f"{IA.DECORATOR_PREFIX}{k}": v for k, v in custom_attributes.items()}
    else:
        attrs = {}
    attrs[f"{IA.DECORATOR_PREFIX}name"] = span_name

    if is_async_gen:
        @wraps(func)
        async def async_gen_wrapper(*args, **kwargs):
            with _start_span(span_name, span_type, attributes=attrs) as span:
                token = push_entity(span_name)
                # Set the path attribute after pushing entity so it includes current span
                path = current_entity_path()
                if path is not None:
                    span.set_attribute(IA.ENTITY_PATH, path)
                _capture_io(span, args, kwargs)
                try:
                    async for item in func(*args, **kwargs):
                        yield item
                    _capture_io(span, args, kwargs, result_marker={"generator": True})
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
                finally:
                    pop_entity(token)
        return async_gen_wrapper  # type: ignore[misc]

    if is_async:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with _start_span(span_name, span_type, attributes=attrs) as span:
                token = push_entity(span_name)
                # Set the path attribute after pushing entity so it includes current span
                path = current_entity_path()
                if path is not None:
                    span.set_attribute(IA.ENTITY_PATH, path)
                _capture_io(span, args, kwargs)
                try:
                    result = await func(*args, **kwargs)
                    _capture_io(span, args, kwargs, result_marker=result)
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
                finally:
                    pop_entity(token)
        return async_wrapper  # type: ignore[misc]

    if is_gen:
        @wraps(func)
        def gen_wrapper(*args, **kwargs):
            with _start_span(span_name, span_type, attributes=attrs) as span:
                token = push_entity(span_name)
                # Set the path attribute after pushing entity so it includes current span
                path = current_entity_path()
                if path is not None:
                    span.set_attribute(IA.ENTITY_PATH, path)
                _capture_io(span, args, kwargs)
                try:
                    gen = func(*args, **kwargs)
                    assert isinstance(gen, types.GeneratorType)
                    for item in gen:
                        yield item
                    _capture_io(span, args, kwargs, result_marker={"generator": True})
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
                finally:
                    pop_entity(token)
        return gen_wrapper  # type: ignore[misc]

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        with _start_span(span_name, span_type, attributes=attrs) as span:
            token = push_entity(span_name)
            # Set the path attribute after pushing entity so it includes current span
            path = current_entity_path()
            if path is not None:
                span.set_attribute(IA.ENTITY_PATH, path)
            _capture_io(span, args, kwargs)
            try:
                result = func(*args, **kwargs)
                _capture_io(span, args, kwargs, result_marker=result)
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
            finally:
                pop_entity(token)
    return sync_wrapper  # type: ignore[misc]

def workflow(name: str | None = None, *, attributes: Mapping[str, Any] | None = None):
    def decorator(func: F) -> F:
        span_name = name or func.__qualname__
        return _wrap_body(span_name, "workflow", func, attributes)
    return decorator

def task(name: str | None = None, *, attributes: Mapping[str, Any] | None = None):
    def decorator(func: F) -> F:
        span_name = name or func.__qualname__
        return _wrap_body(span_name, "task", func, attributes)
    return decorator

def agent(name: str | None = None, *, attributes: Mapping[str, Any] | None = None):
    def decorator(func: F) -> F:
        span_name = name or func.__qualname__
        return _wrap_body(span_name, "agent", func, attributes)
    return decorator

def tool(name: str | None = None, *, attributes: Mapping[str, Any] | None = None):
    def decorator(func: F) -> F:
        span_name = name or func.__qualname__
        return _wrap_body(span_name, "tool", func, attributes)
    return decorator
