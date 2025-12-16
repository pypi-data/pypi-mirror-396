"""
Fiddler Strands SDK - OpenTelemetry instrumentation for Strands AI agents.

This package provides automatic instrumentation for Strands AI agents using
OpenTelemetry, enabling observability and monitoring capabilities.
"""

from pathlib import Path

from .attributes import (
    get_conversation_id,
    get_llm_context,
    get_session_attributes,
    get_span_attributes,
    set_conversation_id,
    set_llm_context,
    set_session_attributes,
    set_span_attributes,
)
from .hooks import FiddlerInstrumentationHook
from .instrumentation import StrandsAgentInstrumentor
from .span_processor import FiddlerSpanProcessor

# Read version from VERSION file
try:
    __version__ = (Path(__file__).parent / 'VERSION').read_text().strip()
except FileNotFoundError:
    __version__ = '0.0.0'  # Fallback version

__all__ = [
    'StrandsAgentInstrumentor',
    'FiddlerInstrumentationHook',
    'FiddlerSpanProcessor',
    'set_session_attributes',
    'get_session_attributes',
    'set_conversation_id',
    'get_conversation_id',
    'set_span_attributes',
    'get_span_attributes',
    'set_llm_context',
    'get_llm_context',
]
