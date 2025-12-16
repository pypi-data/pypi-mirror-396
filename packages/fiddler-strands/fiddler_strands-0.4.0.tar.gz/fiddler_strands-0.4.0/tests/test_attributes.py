import asyncio
from unittest.mock import Mock

import pytest
from strands import Agent
from strands.models import Model

from fiddler_strandsagents.attributes import (
    get_conversation_id,
    get_llm_context,
    get_session_attributes,
    set_conversation_id,
    set_llm_context,
    set_session_attributes,
)


class TestAttributeFunctions:
    """Test cases for the standalone functions in attributes module."""

    def test_get_set_conversation_id(self):
        """Test get_conversation_id when agent has _sync_fiddler_conversation_id attribute."""

        agent = Mock(spec=Agent)

        # empty string is returned if the attribute is not set
        result = get_conversation_id(agent)
        assert result == ''

        set_conversation_id(agent, 'new-conv-789')

        result = get_conversation_id(agent)
        assert result == 'new-conv-789'

    def test_get_set_session_attributes(self):
        """Test get_session_attributes returns session attributes."""

        agent = Mock(spec=Agent)
        # empty dictionary is returned if the attribute is not set
        result = get_session_attributes(agent)
        assert result == {}

        # session attributes are returned if the attribute is set1
        agent._sync_fiddler_session_attributes = {
            'user_id': 'user-123',
            'session_id': 'session-456',
            'custom_key': 'custom-value',
        }
        set_session_attributes(
            agent,
            user_id='user-123',
            session_id='session-456',
            custom_key='custom-value',
        )

        result = get_session_attributes(agent)
        expected = {
            'user_id': 'user-123',
            'session_id': 'session-456',
            'custom_key': 'custom-value',
        }
        assert result == expected

    @pytest.mark.asyncio
    async def test_async_get_set_conversation_id(self):
        """Test async_get_conversation_id."""

        agent = Mock(spec=Agent)
        result = get_conversation_id(agent)
        assert result == ''
        set_conversation_id(agent, 'async-conv-123')
        result = get_conversation_id(agent)
        assert result == 'async-conv-123'

    @pytest.mark.asyncio
    async def test_async_conversation_id_race_condition(self):
        """Test async_get_conversation_id under multiple async execution ."""
        agent = Mock(spec=Agent)

        async def async_sleep_and_set_conversation_id_async(
            agent: Agent, conversation_id: str, sleep_time: float
        ) -> None:
            await asyncio.sleep(sleep_time)
            assert get_conversation_id(agent) == 'async-conv-000'
            set_conversation_id(agent, conversation_id)
            assert get_conversation_id(agent) == conversation_id

        set_conversation_id(agent, 'async-conv-000')
        await asyncio.gather(
            async_sleep_and_set_conversation_id_async(agent, 'async-conv-123', 0.2),
            async_sleep_and_set_conversation_id_async(agent, 'async-conv-456', 0.1),
        )
        result = get_conversation_id(agent)
        assert result == 'async-conv-000'

    @pytest.mark.asyncio
    async def test_async_get_set_session_attributes(self):
        """Test async_get_session_attributes."""

        agent = Mock(spec=Agent)
        result = get_session_attributes(agent)
        assert result == {}

        set_session_attributes(agent, user_id='async-user-123', async_key='async-value')
        result = get_session_attributes(agent)
        assert result == {'user_id': 'async-user-123', 'async_key': 'async-value'}

    @pytest.mark.asyncio
    async def test_async_session_attributes_race_condition(self):
        """Test async_get_conversation_id under multiple async execution ."""
        agent = Mock(spec=Agent)

        async def async_sleep_and_add_session_attributes_async(
            agent: Agent, async_key: str, sleep_time: float
        ) -> None:
            await asyncio.sleep(sleep_time)
            assert get_session_attributes(agent) == {'async_key': 'async-attr-000'}
            set_session_attributes(agent, async_key=async_key)
            assert get_session_attributes(agent) == {'async_key': async_key}

        set_session_attributes(agent, async_key='async-attr-000')
        await asyncio.gather(
            async_sleep_and_add_session_attributes_async(
                agent, async_key='async-attr-123', sleep_time=0.2
            ),
            async_sleep_and_add_session_attributes_async(
                agent, async_key='async-attr-456', sleep_time=0.1
            ),
        )
        result = get_session_attributes(agent)
        assert result == {'async_key': 'async-attr-000'}

    def test_get_set_llm_context(self):
        """Test get_llm_context when model has _sync_fiddler_llm_context attribute."""

        model = Mock(spec=Model)

        # empty string is returned if the attribute is not set
        result = get_llm_context(model)
        assert result == ''

        set_llm_context(model, 'test-context-123')
        result = get_llm_context(model)
        assert result == 'test-context-123'

    @pytest.mark.asyncio
    async def test_async_get_set_llm_context(self):
        """Test async_get_llm_context."""

        model = Mock(spec=Model)
        result = get_llm_context(model)
        assert result == ''
        set_llm_context(model, 'async-context-456')
        result = get_llm_context(model)
        assert result == 'async-context-456'

    @pytest.mark.asyncio
    async def test_async_llm_context_race_condition(self):
        """Test async_get_llm_context under multiple async execution."""
        model = Mock(spec=Model)

        async def async_sleep_and_set_llm_context_async(
            model: Model, context: str, sleep_time: float
        ) -> None:
            await asyncio.sleep(sleep_time)
            assert get_llm_context(model) == 'async-context-000'
            set_llm_context(model, context)
            assert get_llm_context(model) == context

        set_llm_context(model, 'async-context-000')
        await asyncio.gather(
            async_sleep_and_set_llm_context_async(model, 'async-context-123', 0.2),
            async_sleep_and_set_llm_context_async(model, 'async-context-456', 0.1),
        )
        result = get_llm_context(model)
        assert result == 'async-context-000'
