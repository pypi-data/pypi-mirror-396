from __future__ import annotations

import importlib
import inspect
import logging
from collections.abc import Callable
from opentelemetry.instrumentation.dependencies import DependencyConflictError

logger = logging.getLogger("impact.sdk.registry")


def _supports_raise_exception_flag(instrument: Callable[..., object]) -> bool:
    """Return True if the instrument callable supports raise_exception_on_conflict."""
    signature = inspect.signature(instrument)
    parameters = signature.parameters
    if "raise_exception_on_conflict" in parameters:
        return True
    return any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values())


def _instrument(module: str, class_name: str) -> bool:
    """Try to import `module`, get `class_name`, and call `.instrument()`."""
    try:
        mod = importlib.import_module(module)
        cls = getattr(mod, class_name)
        inst = cls()
        instrument_kwargs = {}
        instrument_method = inst.instrument
        if _supports_raise_exception_flag(instrument_method):
            instrument_kwargs["raise_exception_on_conflict"] = True
        instrument_method(**instrument_kwargs)
        return True
    except ModuleNotFoundError as exc:
        logger.warning(
            "Skipping instrumentation for %s: dependency %s is not installed",
            module,
            exc.name,
        )
        return False
    except DependencyConflictError as conflict_error:
        conflict_details = getattr(conflict_error, "conflict", None)
        missing_dependency = False

        if conflict_details is not None:
            required_any = getattr(conflict_details, "required_any", None)
            found_any = getattr(conflict_details, "found_any", None)
            found_value = getattr(conflict_details, "found", None)

            if required_any:
                if not found_any or all(entry is None for entry in found_any):
                    missing_dependency = True
            elif found_value is None or str(found_value).lower() == "none":
                missing_dependency = True

        if missing_dependency:
            logger.warning(
                "Skipping instrumentation for %s due to missing dependency: %s",
                module,
                conflict_error,
            )
            return False

        logger.error("Instrumentation conflict for %s: %s", module, conflict_error)
        raise
    except Exception:
        logger.exception("Instrumentation for %s.%s failed", module, class_name)
        return False


# Official OTel GenAI providers

def instrument_openai() -> bool:
    # return _instrument("opentelemetry.instrumentation.openai_v2", "OpenAIInstrumentor")
    return _instrument("opentelemetry.instrumentation.openai", "OpenAIInstrumentor")

def instrument_openai_agents() -> bool:
    return _instrument("opentelemetry.instrumentation.openai_agents", "OpenAIAgentsInstrumentor")

def instrument_google_genai() -> bool:
    return _instrument("opentelemetry.instrumentation.google_genai", "GoogleGenAiSdkInstrumentor")

def instrument_vertexai() -> bool:
    # OTel ecosystem (Python contrib): opentelemetry-instrumentation-vertexai
    return _instrument("opentelemetry.instrumentation.vertexai", "VertexAIInstrumentor")


# Official instrumentors - Azure AI Inference and AWS Bedrock via Botocore

def instrument_azure_ai_inference() -> bool:
    try:
        from azure.core.settings import settings  # type: ignore[import]
        from azure.core.tracing.ext.opentelemetry_span import (  # type: ignore[import]
            OpenTelemetrySpan,
        )
    except ImportError:
        logger.debug(
            "Could not import azure core tracing bridge; proceeding without configuring tracing implementation",
        )
    else:
        try:
            current_impl = settings.tracing_implementation()
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to read azure.core tracing implementation")
        else:
            if current_impl is None:
                try:
                    settings.tracing_implementation = OpenTelemetrySpan
                    logger.debug(
                        "Configured azure.core tracing implementation to use OpenTelemetrySpan",
                    )
                except Exception:  # pragma: no cover - defensive
                    logger.exception(
                        "Failed to set azure.core tracing implementation to OpenTelemetrySpan",
                    )

    return _instrument("azure.ai.inference.tracing", "AIInferenceInstrumentor")

def instrument_aws_bedrock() -> bool:
    return _instrument("opentelemetry.instrumentation.botocore", "BotocoreInstrumentor")


# Community Instrumentors

def instrument_anthropic() -> bool:
    return _instrument("opentelemetry.instrumentation.anthropic", "AnthropicInstrumentor")

def instrument_ollama() -> bool:
    return _instrument("opentelemetry.instrumentation.ollama", "OllamaInstrumentor")

def instrument_mistral() -> bool:
    return _instrument("opentelemetry.instrumentation.mistralai", "MistralAiInstrumentor")

def instrument_cohere() -> bool:
    return _instrument("opentelemetry.instrumentation.cohere", "CohereInstrumentor")

def instrument_groq() -> bool:
    return _instrument("opentelemetry.instrumentation.groq", "GroqInstrumentor")

def instrument_langchain() -> bool:
    return _instrument("opentelemetry.instrumentation.langchain", "LangchainInstrumentor")

def instrument_llama_index() -> bool:
    return _instrument("opentelemetry.instrumentation.llamaindex", "LlamaIndexInstrumentor")


# Infrastructure Instrumentors

def instrument_httpx() -> bool:
    """Instrument HTTPX HTTP client library for outbound HTTP request tracing."""
    return _instrument("opentelemetry.instrumentation.httpx", "HTTPXClientInstrumentor")

def instrument_azure_aisearch() -> bool:
    """Instrument Azure AI Search SDK for search query tracing."""
    return _instrument("opentelemetry.instrumentation.azure_aisearch", "AzureSearchInstrumentor")


# Auto-instrument all available GenAI providers
def auto_instrument_all() -> list[bool]:
    """Auto-instrument all available GenAI providers."""
    results: list[bool] = []
    results.append(instrument_openai())
    results.append(instrument_openai_agents())
    results.append(instrument_azure_ai_inference())
    results.append(instrument_google_genai())
    results.append(instrument_vertexai())
    results.append(instrument_aws_bedrock())
    results.append(instrument_anthropic())
    results.append(instrument_ollama())
    results.append(instrument_cohere())
    results.append(instrument_mistral())
    results.append(instrument_groq())
    results.append(instrument_langchain())
    results.append(instrument_llama_index())
    results.append(instrument_azure_aisearch())
    return results

# Export all instrumentors
__all__ = [
    "instrument_openai", 
    "instrument_openai_agents", 
    "instrument_google_genai", 
    "instrument_vertexai", 
    "instrument_azure_ai_inference", 
    "instrument_aws_bedrock", 
    "instrument_anthropic", 
    "instrument_ollama", 
    "instrument_mistral", 
    "instrument_cohere", 
    "instrument_groq", 
    "instrument_langchain", 
    "instrument_llama_index",
    "instrument_httpx",
    "instrument_azure_aisearch",
    "auto_instrument_all"
]
