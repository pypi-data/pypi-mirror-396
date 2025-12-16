import asyncio
import contextvars
from typing import Union

from pydantic import ConfigDict, validate_call
from strands import Agent
from strands.models import Model
from strands.types.tools import AgentTool


def _in_asyncio_context() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def _get_or_create_context_var(
    obj: object, async_attr_name: str, default_value: Union[dict, str]
) -> contextvars.ContextVar:
    """Get or create a ContextVar for async attribute storage."""
    if not hasattr(obj, async_attr_name):
        setattr(
            obj,
            async_attr_name,
            contextvars.ContextVar(async_attr_name, default=default_value),
        )
    return getattr(obj, async_attr_name)


def _set_dict_attribute_async(
    obj: object, async_attr_name: str, **kwargs: Union[str, int, float, bool]
) -> None:
    """Set dictionary attributes in async context."""
    context_var = _get_or_create_context_var(obj, async_attr_name, {})
    updated_attributes = context_var.get().copy()
    updated_attributes.update(kwargs)
    context_var.set(updated_attributes)


def _set_dict_attribute_sync(
    obj: object, sync_attr_name: str, **kwargs: Union[str, int, float, bool]
) -> None:
    """Set dictionary attributes in sync context."""
    if not hasattr(obj, sync_attr_name):
        setattr(obj, sync_attr_name, {})
    getattr(obj, sync_attr_name).update(kwargs)


def _get_dict_attribute_async(
    obj: object, async_attr_name: str
) -> dict[str, Union[str, int, float, bool]]:
    """Get dictionary attributes from async context."""
    if hasattr(obj, async_attr_name):
        try:
            return getattr(obj, async_attr_name).get().copy()
        except LookupError:
            pass
    return {}


def _get_dict_attribute_sync(
    obj: object, sync_attr_name: str
) -> dict[str, Union[str, int, float, bool]]:
    """Get dictionary attributes from sync context."""
    if hasattr(obj, sync_attr_name):
        return getattr(obj, sync_attr_name).copy()
    return {}


def _set_string_attribute_async(obj: object, async_attr_name: str, value: str) -> None:
    """Set string attribute in async context."""
    context_var = _get_or_create_context_var(obj, async_attr_name, '')
    context_var.set(value)


def _set_string_attribute_sync(obj: object, sync_attr_name: str, value: str) -> None:
    """Set string attribute in sync context."""
    setattr(obj, sync_attr_name, value)


def _get_string_attribute_async(obj: object, async_attr_name: str) -> str:
    """Get string attribute from async context."""
    if hasattr(obj, async_attr_name):
        try:
            return getattr(obj, async_attr_name).get()
        except LookupError:
            pass
    return ''


def _get_string_attribute_sync(obj: object, sync_attr_name: str) -> str:
    """Get string attribute from sync context."""
    if hasattr(obj, sync_attr_name):
        return getattr(obj, sync_attr_name)
    return ''


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_span_attributes(
    obj: Union[Model, AgentTool], **kwargs: Union[str, int, float, bool]
) -> None:
    """
    Set custom attributes on a Model or AgentTool that can be accessed by logging hooks.

    This function stores key-value pairs as attributes on the object, making
    them accessible to hooks during model invocation events. Attributes are
    automatically scoped to async or sync contexts.

    Args:
        obj: The object to set the attribute on (Model or AgentTool instance)
        **kwargs: Key-value pairs of attributes to set (str, int, float, or bool values)

    Example:
        .. code-block:: python

            from strands.models.openai import OpenAIModel
            from fiddler_strandsagents import set_span_attributes

            model = OpenAIModel(api_key="...", model_id="gpt-4")
            set_span_attributes(model, model_id="gpt-4", temperature=0.7)
    """
    if _in_asyncio_context():
        _set_dict_attribute_async(obj, '_async_fiddler_span_attributes', **kwargs)
    else:
        _set_dict_attribute_sync(obj, '_sync_fiddler_span_attributes', **kwargs)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_span_attributes(
    obj: Union[Model, AgentTool],
) -> dict[str, Union[str, int, float, bool]]:
    """
    Get span attributes from a Model or AgentTool object.

    Retrieves custom attributes that were previously set using set_span_attributes().
    Returns an empty dictionary if no attributes have been set.

    Args:
        obj: The Model or AgentTool instance to retrieve attributes from

    Returns:
        Dictionary of attribute key-value pairs, or empty dict if none exist
    """
    if _in_asyncio_context() and hasattr(obj, '_async_fiddler_span_attributes'):
        return _get_dict_attribute_async(obj, '_async_fiddler_span_attributes')
    return _get_dict_attribute_sync(obj, '_sync_fiddler_span_attributes')


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_conversation_id(agent: Agent, conversation_id: str) -> None:
    """
    Set the conversation ID for the current agent invocation.

    The conversation ID is used to group related agent invocations together,
    enabling conversation-level tracing and monitoring in Fiddler's platform.
    This ID will persist until it is explicitly changed by calling this function
    again with a new value.

    Args:
        agent: The Strands Agent instance to associate with the conversation
        conversation_id: Unique identifier for the conversation (e.g., session ID, user ID)

    Example:
        .. code-block:: python

            from strands import Agent
            from fiddler_strandsagents import set_conversation_id

            agent = Agent(model=model, system_prompt="...")
            set_conversation_id(agent, "session_12345")
    """
    if _in_asyncio_context():
        _set_string_attribute_async(
            agent, '_async_fiddler_conversation_id', conversation_id
        )
    else:
        _set_string_attribute_sync(
            agent, '_sync_fiddler_conversation_id', conversation_id
        )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_conversation_id(agent: Agent) -> str:
    """
    Get the conversation ID for the current agent invocation.

    Retrieves the conversation ID that was previously set using set_conversation_id().
    Works in both synchronous and asynchronous contexts automatically.

    Args:
        agent: The Strands Agent instance to retrieve the conversation ID from

    Returns:
        The conversation ID string, or empty string if none has been set
    """
    if _in_asyncio_context() and hasattr(agent, '_async_fiddler_conversation_id'):
        return _get_string_attribute_async(agent, '_async_fiddler_conversation_id')
    return _get_string_attribute_sync(agent, '_sync_fiddler_conversation_id')


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_session_attributes(
    agent: Agent, **kwargs: Union[str, int, float, bool]
) -> None:
    """
    Add Fiddler-specific session attributes to an agent's metadata.

    Session attributes provide context about the agent's execution environment,
    such as user roles, cost centers, or any custom metadata that should be
    tracked across all invocations within a session.

    Args:
        agent: The Strands Agent instance to add session attributes to
        **kwargs: Key-value pairs of session attributes (str, int, float, or bool values)

    Example:
        .. code-block:: python

            from strands import Agent
            from fiddler_strandsagents import set_session_attributes

            agent = Agent(model=model, system_prompt="...")
            set_session_attributes(agent, role="customer_support", region="us-west")
    """
    if _in_asyncio_context():
        _set_dict_attribute_async(agent, '_async_fiddler_session_attributes', **kwargs)
    else:
        _set_dict_attribute_sync(agent, '_sync_fiddler_session_attributes', **kwargs)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_session_attributes(
    agent: Agent,
) -> dict[str, Union[str, int, float, bool]]:
    """
    Get the session attributes for the current agent invocation.

    Retrieves session attributes that were previously set using set_session_attributes().
    Works in both synchronous and asynchronous contexts automatically.

    Args:
        agent: The Strands Agent instance to retrieve session attributes from

    Returns:
        Dictionary of session attribute key-value pairs, or empty dict if none exist
    """
    if _in_asyncio_context() and hasattr(agent, '_async_fiddler_session_attributes'):
        return _get_dict_attribute_async(agent, '_async_fiddler_session_attributes')
    return _get_dict_attribute_sync(agent, '_sync_fiddler_session_attributes')


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_llm_context(model: Model, context: str) -> None:
    """
    Set additional context information for LLM interactions.

    The LLM context allows you to provide additional background information
    or available options that can be tracked alongside model invocations.
    This context will be added to telemetry spans as 'gen_ai.llm.context'
    and can be used for debugging or analysis in Fiddler's platform.

    The context persists until explicitly changed by calling this function
    again with a new value. Works automatically in both synchronous and
    asynchronous contexts.

    Args:
        model: The Model instance to attach context to
        context: Context string providing additional information about available
            options, constraints, or background for the LLM interaction

    Example:
        .. code-block:: python

            from strands.models.openai import OpenAIModel
            from fiddler_strandsagents import set_llm_context

            model = OpenAIModel(api_key="...", model_id="gpt-4")
            set_llm_context(
                model,
                'Available hotels: Hilton, Marriott, Hyatt...'
            )

            # Now when the model is invoked, the context will be
            # included in the telemetry span
            agent = Agent(model=model, system_prompt="You are a travel assistant")
            response = agent("Which hotel should I book?")
    """
    if _in_asyncio_context():
        _set_string_attribute_async(model, '_async_fiddler_llm_context', context)
    else:
        _set_string_attribute_sync(model, '_sync_fiddler_llm_context', context)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_llm_context(model: Model) -> str:
    """
    Get the LLM context for the current model.

    Retrieves the context string that was previously set using set_llm_context().
    Works automatically in both synchronous and asynchronous contexts.

    Args:
        model: The Model instance to retrieve context from

    Returns:
        The LLM context string, or empty string if none has been set

    Example:
        .. code-block:: python

            from fiddler_strandsagents import set_llm_context, get_llm_context

            set_llm_context(model, "Important background information")
            context = get_llm_context(model)
            print(context)  # "Important background information"
    """
    if _in_asyncio_context() and hasattr(model, '_async_fiddler_llm_context'):
        return _get_string_attribute_async(model, '_async_fiddler_llm_context')
    return _get_string_attribute_sync(model, '_sync_fiddler_llm_context')
