"""Phoenix tracing configuration for RealTimeX services."""

from __future__ import annotations

import logging
from typing import Final

from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from phoenix.otel import register

_LOGGER = logging.getLogger(__name__)

_PHOENIX_ENDPOINT: Final = "https://llmtracing.realtimex.co/v1/traces"
_PHOENIX_PROJECT: Final = "realtimex-agents"
_PHOENIX_API_KEY: Final = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJBcGlLZXk6NyJ9.jdOKz5BgdfniazLE-xSVaXGlJsbYAd26O7ulCOYiFMs"

_LANGCHAIN_INSTRUMENTED = False


def initialize_tracing(*, auto_instrument: bool = True) -> TracerProvider:
    """Ensure Phoenix tracing is configured and LangChain is instrumented.

    Registers the Phoenix tracer provider with the standard RealTimeX
    endpoint, project, and API key.
    """
    tracer_provider = register(
        endpoint=_PHOENIX_ENDPOINT,
        project_name=_PHOENIX_PROJECT,
        api_key=_PHOENIX_API_KEY,
        auto_instrument=auto_instrument,
    )

    _LOGGER.info(
        "Phoenix tracing configured for project '%s' targeting '%s'",
        _PHOENIX_PROJECT,
        _PHOENIX_ENDPOINT,
    )

    _instrument_langchain(tracer_provider)
    return tracer_provider


def _instrument_langchain(tracer_provider: TracerProvider) -> None:
    """Instrument LangChain exactly once per process."""
    global _LANGCHAIN_INSTRUMENTED  # noqa: PLW0603

    if _LANGCHAIN_INSTRUMENTED:
        return

    LangChainInstrumentor().instrument(
        tracer_provider=tracer_provider,
        skip_dep_check=True,
    )
    _LANGCHAIN_INSTRUMENTED = True


__all__ = ["initialize_tracing"]
