"""Tests for the StrandsAgentInstrumentor."""

from unittest.mock import Mock, patch

import pytest

from fiddler_strandsagents import StrandsAgentInstrumentor


class TestStrandsAgentInstrumentor:
    """Test cases for StrandsAgentInstrumentor."""

    @pytest.fixture
    def strands_telemetry(self):
        """Create a StrandsTelemetry fixture with mocked tracer_provider."""
        from strands.telemetry import StrandsTelemetry

        telemetry = StrandsTelemetry()
        # Mock the tracer_provider to avoid actual OpenTelemetry setup
        telemetry.tracer_provider = Mock()
        return telemetry

    def test_instrumentation_dependencies(self, strands_telemetry):
        """Test that instrumentation dependencies are correctly specified."""
        instrumentor = StrandsAgentInstrumentor(strands_telemetry)
        deps = instrumentor.instrumentation_dependencies()
        assert 'strands-agents' in deps

    def test_instrumentor_initialization(self, strands_telemetry):
        """Test that instrumentor initializes correctly."""
        instrumentor = StrandsAgentInstrumentor(strands_telemetry)
        assert instrumentor.strands_telemetry == strands_telemetry
        assert not instrumentor.is_instrumented_by_opentelemetry

    def test_instrument_method(self, strands_telemetry):
        """Test that instrument method patches Agent.__init__."""
        instrumentor = StrandsAgentInstrumentor(strands_telemetry)

        # Store the original __init__ before patching
        original_agent_init = instrumentor._original_agent_init

        # Mock the wrap_function_wrapper to avoid actual patching
        with patch(
            'fiddler_strandsagents.instrumentation.wrap_function_wrapper'
        ) as mock_wrap:
            instrumentor._instrument()

            # Verify that wrap_function_wrapper was called
            mock_wrap.assert_called_once()

            # Verify that the original init was stored
            assert instrumentor._original_agent_init == original_agent_init

    def test_uninstrument_method(self, strands_telemetry):
        """Test that uninstrument method restores original Agent.__init__."""
        instrumentor = StrandsAgentInstrumentor(strands_telemetry)

        # Store the original __init__ before patching
        original_agent_init = instrumentor._original_agent_init

        # Mock the wrap_function_wrapper to avoid actual patching
        with patch('fiddler_strandsagents.instrumentation.wrap_function_wrapper'):
            # First instrument
            instrumentor._instrument()

            # Then uninstrument
            instrumentor._uninstrument()

            # Verify that the original __init__ was restored
            assert instrumentor._original_agent_init == original_agent_init
