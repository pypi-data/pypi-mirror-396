"""Tests for the FiddlerSpanProcessor."""

from unittest.mock import Mock, call, patch

import pytest
from opentelemetry import context
from opentelemetry.sdk.trace import Span

from fiddler_strandsagents.constants import (
    FIDDLER_CONVERSATION_ID,
    GEN_AI_TOOL_DEFINITIONS,
)
from fiddler_strandsagents.span_processor import FiddlerSpanProcessor


class TestFiddlerSpanProcessor:
    """Test cases for FiddlerSpanProcessor."""

    @pytest.fixture
    def processor(self):
        """Create a FiddlerSpanProcessor instance."""
        return FiddlerSpanProcessor()

    @pytest.fixture
    def mock_span(self):
        """Create a mock span for testing."""
        span = Mock(spec=Span)
        span.set_attribute = Mock()
        return span

    @pytest.fixture
    def mock_parent_span(self):
        """Create a mock parent span with attributes."""
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = True
        parent_span.attributes = {
            'gen_ai.agent.name': 'test-agent',
            'gen_ai.agent.id': 'agent-123',
            FIDDLER_CONVERSATION_ID: 'conv-456',
            'system_prompt': 'You are a helpful assistant',
            GEN_AI_TOOL_DEFINITIONS: '[{"name": "add", "description": "Adds two numbers."}]',
            'fiddler.session.user.user_id': 'user-789',
            'fiddler.session.user.session_id': 'session-abc',
            'other.attribute': 'should-not-copy',
        }
        return parent_span

    @pytest.fixture
    def mock_non_recording_parent_span(self):
        """Create a mock non-recording parent span."""
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = False
        parent_span.attributes = {
            'gen_ai.agent.name': 'test-agent',
        }
        return parent_span

    @pytest.fixture
    def mock_parent_span_no_attributes(self):
        """Create a mock parent span without attributes."""
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = True
        parent_span.attributes = {}
        return parent_span

    # def test_denormalized_attributes_constant(self, processor):
    #     """Test that DENORMALIZED_ATTRIBUTES contains expected attributes."""
    #     expected_attributes = [
    #         "gen_ai.agent.name",
    #         "gen_ai.agent.id",
    #         FIDDLER_CONVERSATION_ID,
    #         "system_prompt",
    #     ]
    #     assert processor.DENORMALIZED_ATTRIBUTES == expected_attributes

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_valid_parent_span(
        self, mock_get_current_span, processor, mock_span, mock_parent_span
    ):
        """Test on_start with a valid parent span copies all expected attributes."""
        mock_get_current_span.return_value = mock_parent_span

        processor.on_start(mock_span)

        # Verify that all denormalized attributes were copied
        expected_calls = [
            ('gen_ai.agent.name', 'test-agent'),
            ('gen_ai.agent.id', 'agent-123'),
            (FIDDLER_CONVERSATION_ID, 'conv-456'),
            ('system_prompt', 'You are a helpful assistant'),
            (
                GEN_AI_TOOL_DEFINITIONS,
                '[{"name": "add", "description": "Adds two numbers."}]',
            ),
            ('fiddler.session.user.user_id', 'user-789'),
            ('fiddler.session.user.session_id', 'session-abc'),
        ]

        assert mock_span.set_attribute.call_count == len(expected_calls)
        mock_span.set_attribute.assert_has_calls(
            [call(attr, value) for attr, value in expected_calls], any_order=True
        )

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_no_parent_span(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test on_start with no parent span does not copy any attributes."""
        mock_get_current_span.return_value = None

        processor.on_start(mock_span)

        mock_span.set_attribute.assert_not_called()

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_non_recording_parent_span(
        self,
        mock_get_current_span,
        processor,
        mock_span,
        mock_non_recording_parent_span,
    ):
        """Test on_start with non-recording parent span does not copy attributes."""
        mock_get_current_span.return_value = mock_non_recording_parent_span

        processor.on_start(mock_span)

        mock_span.set_attribute.assert_not_called()

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_parent_span_no_attributes(
        self,
        mock_get_current_span,
        processor,
        mock_span,
        mock_parent_span_no_attributes,
    ):
        """Test on_start with parent span having no attributes."""
        mock_get_current_span.return_value = mock_parent_span_no_attributes

        processor.on_start(mock_span)

        mock_span.set_attribute.assert_not_called()

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_parent_span_missing_attributes(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test on_start with parent span missing some denormalized attributes."""
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = True
        parent_span.attributes = {
            'gen_ai.agent.name': 'test-agent',
            # Missing other denormalized attributes
            'fiddler.session.user.user_id': 'user-789',
        }
        mock_get_current_span.return_value = parent_span

        processor.on_start(mock_span)

        # Should only copy the attributes that exist
        expected_calls = [
            ('gen_ai.agent.name', 'test-agent'),
            ('fiddler.session.user.user_id', 'user-789'),
        ]

        assert mock_span.set_attribute.call_count == len(expected_calls)
        mock_span.set_attribute.assert_has_calls(
            [call(attr, value) for attr, value in expected_calls], any_order=True
        )

    # @patch("fiddler_strandsagents.span_processor.get_current_span")
    # def test_on_start_with_empty_attribute_values(
    #     self, mock_get_current_span, processor, mock_span
    # ):
    #     """Test on_start skips attributes with empty/falsy values."""
    #     parent_span = Mock(spec=Span)
    #     parent_span.is_recording.return_value = True
    #     parent_span.attributes = {
    #         "gen_ai.agent.name": "",  # Empty string
    #         "gen_ai.agent.id": None,  # None value
    #         FIDDLER_CONVERSATION_ID: 0,  # Falsy value
    #         "system_prompt": "Valid prompt",
    #         "fiddler.session.user.user_id": None,  # None value
    #         "fiddler.session.user.session_id": "valid-session",
    #     }
    #     mock_get_current_span.return_value = parent_span

    #     processor.on_start(mock_span)

    #     # Should only copy attributes with truthy values
    #     expected_calls = [
    #         ("system_prompt", "Valid prompt"),
    #         ("fiddler.session.user.session_id", "valid-session"),
    #     ]

    #     assert mock_span.set_attribute.call_count == len(expected_calls)
    #     mock_span.set_attribute.assert_has_calls(
    #         [call(attr, value) for attr, value in expected_calls], any_order=True
    #     )

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_parent_span_no_attributes_property(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test on_start with parent span that doesn't have attributes property."""
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = True
        # Remove the attributes property
        del parent_span.attributes
        mock_get_current_span.return_value = parent_span

        processor.on_start(mock_span)

        mock_span.set_attribute.assert_not_called()

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_parent_context(
        self, mock_get_current_span, processor, mock_span, mock_parent_span
    ):
        """Test on_start with explicit parent context."""
        mock_context = Mock(spec=context.Context)
        mock_get_current_span.return_value = mock_parent_span

        processor.on_start(mock_span, mock_context)

        mock_get_current_span.assert_called_once_with(mock_context)
        assert mock_span.set_attribute.call_count > 0

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_user_session_attribute_prefix_extraction(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test that user session attribute prefix is correctly extracted."""
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = True
        parent_span.attributes = {
            'fiddler.session.user.custom_key': 'custom_value',
            'fiddler.session.user.another_key': 'another_value',
            'fiddler.session.other.prefix': 'should_not_copy',  # Different prefix
        }
        mock_get_current_span.return_value = parent_span

        processor.on_start(mock_span)

        # Should only copy attributes with the correct prefix
        expected_calls = [
            ('fiddler.session.user.custom_key', 'custom_value'),
            ('fiddler.session.user.another_key', 'another_value'),
        ]

        assert mock_span.set_attribute.call_count == len(expected_calls)
        mock_span.set_attribute.assert_has_calls(
            [call(attr, value) for attr, value in expected_calls], any_order=True
        )

    def test_force_flush_returns_true(self, processor):
        """Test that force_flush always returns True."""
        assert processor.force_flush() is True
        assert processor.force_flush(timeout_millis=1000) is True
        assert processor.force_flush(timeout_millis=0) is True

    def test_force_flush_with_different_timeouts(self, processor):
        """Test force_flush with different timeout values."""
        # Test with default timeout
        assert processor.force_flush() is True

        # Test with custom timeout
        assert processor.force_flush(timeout_millis=5000) is True

        # Test with zero timeout
        assert processor.force_flush(timeout_millis=0) is True

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_edge_case_parent_span_not_span_instance(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test on_start handles case where get_current_span returns non-Span object."""
        # Return an object that doesn't have is_recording method
        mock_get_current_span.return_value = 'not_a_span'

        # This should not raise an exception
        processor.on_start(mock_span)

        mock_span.set_attribute.assert_not_called()

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_exception_in_parent_span_access(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test on_start handles exceptions when accessing parent span properties."""
        parent_span = Mock(spec=Span)
        parent_span.is_recording.side_effect = Exception('Test exception')
        mock_get_current_span.return_value = parent_span

        # This should not raise an exception
        processor.on_start(mock_span)

        mock_span.set_attribute.assert_not_called()

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_on_start_with_exception_in_span_set_attribute(
        self, mock_get_current_span, processor, mock_span, mock_parent_span
    ):
        """Test on_start handles exceptions when setting span attributes."""
        mock_get_current_span.return_value = mock_parent_span
        mock_span.set_attribute.side_effect = Exception('Test exception')

        # This should not raise an exception
        processor.on_start(mock_span)

        # Should have attempted to set attributes
        assert mock_span.set_attribute.call_count > 0

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_tool_definitions_denormalization(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test that gen_ai.tool.definitions is properly denormalized from parent to child spans."""
        # Create parent span with tool definitions
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = True
        tool_definitions = (
            '[{"name": "add", "description": "Adds two numbers.", '
            '"inputSchema": {"json": {"properties": {"a": {"type": "number"}, '
            '"b": {"type": "number"}}, "required": ["a", "b"], "type": "object"}}}, '
            '{"name": "multiply", "description": "Multiplies two numbers.", '
            '"inputSchema": {"json": {"properties": {"a": {"type": "number"}, '
            '"b": {"type": "number"}}, "required": ["a", "b"], "type": "object"}}}]'
        )
        parent_span.attributes = {
            'gen_ai.agent.name': 'Math Agent',
            GEN_AI_TOOL_DEFINITIONS: tool_definitions,
        }
        mock_get_current_span.return_value = parent_span

        processor.on_start(mock_span)

        # Verify tool definitions were copied to child span
        mock_span.set_attribute.assert_any_call(
            GEN_AI_TOOL_DEFINITIONS, tool_definitions
        )

    @patch('fiddler_strandsagents.span_processor.get_current_span')
    def test_tool_definitions_not_copied_when_missing(
        self, mock_get_current_span, processor, mock_span
    ):
        """Test that child span doesn't get tool definitions when parent doesn't have them."""
        # Create parent span WITHOUT tool definitions
        parent_span = Mock(spec=Span)
        parent_span.is_recording.return_value = True
        parent_span.attributes = {
            'gen_ai.agent.name': 'Test Agent',
            'system_prompt': 'You are helpful',
        }
        mock_get_current_span.return_value = parent_span

        processor.on_start(mock_span)

        # Verify tool definitions were NOT copied
        tool_def_calls = [
            call_args
            for call_args in mock_span.set_attribute.call_args_list
            if call_args[0][0] == GEN_AI_TOOL_DEFINITIONS
        ]
        assert len(tool_def_calls) == 0

    def test_tool_definitions_in_denormalized_attributes_list(self, processor):
        """Test that GEN_AI_TOOL_DEFINITIONS is included in DENORMALIZED_ATTRIBUTES."""
        assert GEN_AI_TOOL_DEFINITIONS in processor.DENORMALIZED_ATTRIBUTES
