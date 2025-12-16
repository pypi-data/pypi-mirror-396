from unittest.mock import MagicMock, Mock, patch

import pytest
from strands import Agent
from strands.experimental.hooks import (
    AfterModelInvocationEvent,
    AfterToolInvocationEvent,
)
from strands.hooks import BeforeInvocationEvent, HookRegistry
from strands.models import Model
from strands.types.tools import AgentTool

from fiddler_strandsagents.attributes import (
    get_span_attributes,
    set_conversation_id,
    set_session_attributes,
    set_span_attributes,
)
from fiddler_strandsagents.constants import (
    FIDDLER_CONVERSATION_ID,
    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE,
)
from fiddler_strandsagents.hooks import FiddlerInstrumentationHook


class TestLoggingHook:
    """Test cases for the LoggingHook class."""

    def test_register_hooks(self):
        """Test that LoggingHook registers all callbacks correctly."""
        hook = FiddlerInstrumentationHook()
        registry = Mock(spec=HookRegistry)

        hook.register_hooks(registry)

        # Verify all callbacks are registered
        assert registry.add_callback.call_count == 3
        registry.add_callback.assert_any_call(AfterToolInvocationEvent, hook.tool_end)
        registry.add_callback.assert_any_call(AfterModelInvocationEvent, hook.model_end)
        registry.add_callback.assert_any_call(
            BeforeInvocationEvent, hook.before_invocation
        )

    def test_tool_end_with_attributes(self, capsys):
        """Test tool_end callback with custom tool attributes."""
        hook = FiddlerInstrumentationHook()

        # Create a mock tool with custom attributes
        mock_tool = Mock(spec=AgentTool)
        set_span_attributes(mock_tool, tool_name='test_tool', version='1.0')

        # Create mock event
        event = Mock(spec=AfterToolInvocationEvent)
        event.selected_tool = mock_tool

        # Create mock span
        mock_span = MagicMock()
        with patch(
            'fiddler_strandsagents.hooks.trace.get_current_span', return_value=mock_span
        ):
            hook.tool_end(event)

        # Verify span attributes were set correctly
        expected_attributes = {
            'fiddler.span.user.tool_name': 'test_tool',
            'fiddler.span.user.version': '1.0',
        }
        mock_span.set_attributes.assert_called_once_with(expected_attributes)

    def test_tool_end_without_attributes(self, capsys):
        """Test tool_end callback without custom tool attributes."""
        hook = FiddlerInstrumentationHook()

        # Create a mock tool without custom attributes
        mock_tool = Mock(spec=AgentTool)

        # Create mock event
        event = Mock(spec=AfterToolInvocationEvent)
        event.selected_tool = mock_tool

        # Create mock span
        mock_span = MagicMock()
        with patch(
            'fiddler_strandsagents.hooks.trace.get_current_span', return_value=mock_span
        ):
            hook.tool_end(event)

        # Verify span attributes were not set
        mock_span.set_attributes.assert_not_called()

    def test_model_end_with_attributes(self, capsys):
        """Test model_end callback with custom model attributes."""
        hook = FiddlerInstrumentationHook()

        # Create a mock agent with a model that has custom attributes
        mock_model = Mock(spec=Model)
        set_span_attributes(mock_model, model_name='gpt-4', temperature=0.7)

        mock_agent = Mock(spec=Agent)
        mock_agent.model = mock_model
        mock_agent.name = 'TestAgent'

        # Create mock event
        event = Mock(spec=AfterModelInvocationEvent)
        event.agent = mock_agent

        # Create mock span
        mock_span = MagicMock()
        with patch(
            'fiddler_strandsagents.hooks.trace.get_current_span', return_value=mock_span
        ):
            hook.model_end(event)

        # Verify span attributes were set correctly
        expected_attributes = {
            'fiddler.span.user.model_name': 'gpt-4',
            'fiddler.span.user.temperature': 0.7,
        }
        mock_span.set_attributes.assert_called_once_with(expected_attributes)

    def test_model_end_without_attributes(self, capsys):
        """Test model_end callback without custom model attributes."""
        hook = FiddlerInstrumentationHook()

        # Create a mock agent with a model without custom attributes
        mock_model = Mock(spec=Model)
        mock_agent = Mock(spec=Agent)
        mock_agent.model = mock_model
        mock_agent.name = 'TestAgent'

        # Create mock event
        event = Mock(spec=AfterModelInvocationEvent)
        event.agent = mock_agent

        # Create mock span
        mock_span = MagicMock()
        with patch(
            'fiddler_strandsagents.hooks.trace.get_current_span', return_value=mock_span
        ):
            hook.model_end(event)

        # Verify span attributes were not set
        mock_span.set_attributes.assert_not_called()

    def test_before_invocation_with_conversation_id_and_session_attributes(self):
        """Test before_invocation sets conversation ID and session attributes."""
        hook = FiddlerInstrumentationHook()

        # Create a mock agent with trace_attributes
        mock_agent = Mock(spec=Agent)
        # Set conversation ID and session attributes
        set_conversation_id(mock_agent, 'conv-123')
        set_session_attributes(mock_agent, user_id='user-456', session_type='test')

        # Create mock event
        event = Mock(spec=BeforeInvocationEvent)
        event.agent = mock_agent

        # Create mock span
        mock_span = MagicMock()
        with patch(
            'fiddler_strandsagents.hooks.trace.get_current_span', return_value=mock_span
        ):
            hook.before_invocation(event)

        # Verify agent span attributes were updated
        assert mock_span.set_attribute.call_count == 1
        mock_span.set_attribute.assert_any_call(FIDDLER_CONVERSATION_ID, 'conv-123')

        assert mock_span.set_attributes.call_count == 1
        mock_span.set_attributes.assert_any_call(
            {
                FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.format(
                    key='user_id'
                ): 'user-456',
                FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.format(
                    key='session_type'
                ): 'test',
            }
        )

    def test_before_invocation_without_conversation_id(self):
        """Test before_invocation when no conversation ID is set."""
        hook = FiddlerInstrumentationHook()

        # Create a mock agent without conversation ID
        mock_agent = Mock(spec=Agent)

        # Create mock event
        event = Mock(spec=BeforeInvocationEvent)
        event.agent = mock_agent

        # Create mock span
        mock_span = MagicMock()
        with patch(
            'fiddler_strandsagents.hooks.trace.get_current_span', return_value=mock_span
        ):
            hook.before_invocation(event)

        # Verify agent span attributes were updated
        assert mock_span.set_attribute.call_count == 0
        mock_span.set_attributes.assert_not_called()

    @pytest.mark.asyncio
    async def test_tool_end_async_context(self, capsys):
        """Test tool_end callback in async context with custom tool attributes."""
        hook = FiddlerInstrumentationHook()

        async def async_test():
            # Create a mock tool with custom attributes in async context
            mock_tool = Mock(spec=AgentTool)
            set_span_attributes(mock_tool, tool_name='async_tool', async_attr=True)

            # Create mock event
            event = Mock(spec=AfterToolInvocationEvent)
            event.selected_tool = mock_tool

            # Create mock span
            mock_span = MagicMock()
            with patch(
                'fiddler_strandsagents.hooks.trace.get_current_span',
                return_value=mock_span,
            ):
                hook.tool_end(event)

            # Verify span attributes were set correctly
            expected_attributes = {
                'fiddler.span.user.tool_name': 'async_tool',
                'fiddler.span.user.async_attr': True,
            }
            mock_span.set_attributes.assert_called_once_with(expected_attributes)

        await async_test()

    @pytest.mark.asyncio
    async def test_model_end_async_context(self, capsys):
        """Test model_end callback in async context with custom model attributes."""
        hook = FiddlerInstrumentationHook()

        async def async_test():
            # Create a mock agent with a model that has custom attributes in async context
            mock_model = Mock(spec=Model)
            set_span_attributes(mock_model, model_name='async-gpt-4', async_mode=True)

            mock_agent = Mock(spec=Agent)
            mock_agent.model = mock_model
            mock_agent.name = 'AsyncTestAgent'

            # Create mock event
            event = Mock(spec=AfterModelInvocationEvent)
            event.agent = mock_agent

            # Create mock span
            mock_span = MagicMock()
            with patch(
                'fiddler_strandsagents.hooks.trace.get_current_span',
                return_value=mock_span,
            ):
                hook.model_end(event)

            # Verify span attributes were set correctly
            expected_attributes = {
                'fiddler.span.user.model_name': 'async-gpt-4',
                'fiddler.span.user.async_mode': True,
            }
            mock_span.set_attributes.assert_called_once_with(expected_attributes)

        await async_test()

    @pytest.mark.asyncio
    async def test_before_invocation_async_context(self):
        """Test before_invocation in async context sets conversation ID and session attributes."""
        hook = FiddlerInstrumentationHook()

        async def async_test():
            # Create a mock agent with trace_attributes
            mock_agent = Mock(spec=Agent)
            mock_agent.trace_attributes = {}

            # Set conversation ID and session attributes in async context
            set_conversation_id(mock_agent, 'async-conv-789')
            set_session_attributes(
                mock_agent, user_id='async-user-999', session_type='async-test'
            )

            # Create mock event
            event = Mock(spec=BeforeInvocationEvent)
            event.agent = mock_agent

            # Create mock span
            mock_span = MagicMock()
            with patch(
                'fiddler_strandsagents.hooks.trace.get_current_span',
                return_value=mock_span,
            ):
                hook.before_invocation(event)

            # Verify trace_attributes were updated
            assert mock_span.set_attribute.call_count == 1
            mock_span.set_attribute.assert_any_call(
                FIDDLER_CONVERSATION_ID, 'async-conv-789'
            )
            assert mock_span.set_attributes.call_count == 1
            mock_span.set_attributes.assert_any_call(
                {
                    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.format(
                        key='user_id'
                    ): 'async-user-999',
                    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.format(
                        key='session_type'
                    ): 'async-test',
                }
            )

        await async_test()

    def test_multiple_span_attributes_updates(self):
        """Test that span attributes can be updated multiple times."""
        mock_tool = Mock(spec=AgentTool)

        # Set initial attributes
        set_span_attributes(mock_tool, tool_name='test_tool', version='1.0')
        attrs = get_span_attributes(mock_tool)
        assert attrs == {'tool_name': 'test_tool', 'version': '1.0'}

        # Update with additional attributes
        set_span_attributes(mock_tool, status='active')
        attrs = get_span_attributes(mock_tool)
        assert attrs == {'tool_name': 'test_tool', 'version': '1.0', 'status': 'active'}

        # Update existing attribute
        set_span_attributes(mock_tool, version='2.0')
        attrs = get_span_attributes(mock_tool)
        assert attrs == {'tool_name': 'test_tool', 'version': '2.0', 'status': 'active'}
