"""
Hook providers for Strands Agent instrumentation.

This module contains various hook implementations that can be used
with Strands agents for logging, monitoring, and observability.
"""

from opentelemetry import trace
from strands.experimental.hooks import (
    AfterModelInvocationEvent,
    AfterToolInvocationEvent,
)
from strands.hooks import BeforeInvocationEvent, HookProvider, HookRegistry

from fiddler_strandsagents.attributes import (
    get_conversation_id,
    get_llm_context,
    get_session_attributes,
    get_span_attributes,
)
from fiddler_strandsagents.constants import (
    FIDDLER_CONVERSATION_ID,
    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE,
    GEN_AI_LLM_CONTEXT,
)


class FiddlerInstrumentationHook(HookProvider):
    """
    Centralized instrumentation hook for Strands agents with Fiddler integration.

    This hook provider automatically captures telemetry data from Strands agents
    and enriches OpenTelemetry spans with Fiddler-specific attributes. It handles
    three key events: before invocation, after tool execution, and after model calls.

    The hook is automatically injected when using StrandsAgentInstrumentor, so
    users typically don't need to manually add it to their agents.

    Example:
        .. code-block:: python

            from strands import Agent
            from fiddler_strandsagents import FiddlerInstrumentationHook

            # Manual usage (not needed with StrandsAgentInstrumentor)
            agent = Agent(
                model=model,
                system_prompt="...",
                hooks=[FiddlerInstrumentationHook()]
            )
    """

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        """
        Register hook callbacks with the Strands agent registry.

        This method is called by the Strands framework to register callbacks
        for various agent lifecycle events.

        Args:
            registry: The HookRegistry to register callbacks with
            **kwargs: Additional registration configuration (unused)
        """
        registry.add_callback(AfterToolInvocationEvent, self.tool_end)
        registry.add_callback(AfterModelInvocationEvent, self.model_end)
        registry.add_callback(BeforeInvocationEvent, self.before_invocation)

    def tool_end(self, event: AfterToolInvocationEvent) -> None:
        """
        Handle the completion of a tool invocation.

        Enriches the current OpenTelemetry span with custom attributes that were
        set on the tool using set_span_attributes(). Attributes are prefixed with
        'fiddler.span.user.' for namespacing.

        Args:
            event: AfterToolInvocationEvent containing tool execution details
        """
        if not event.selected_tool:
            return

        tool_attributes = get_span_attributes(event.selected_tool)
        if tool_attributes:
            current_tool_span = trace.get_current_span()

            attributes = {
                f'fiddler.span.user.{k}': v for k, v in tool_attributes.items()
            }
            current_tool_span.set_attributes(attributes)

    def model_end(self, event: AfterModelInvocationEvent) -> None:
        """
        Handle the completion of a model invocation.

        Enriches the current OpenTelemetry span with custom attributes that were
        set on the model using set_span_attributes(). Attributes are prefixed with
        'fiddler.span.user.' for namespacing.

        Args:
            event: AfterModelInvocationEvent containing model execution details
        """
        # Set the LLM context for the current model invocation
        current_model_span = trace.get_current_span()

        llm_context = get_llm_context(event.agent.model)
        if llm_context:
            current_model_span.set_attribute(GEN_AI_LLM_CONTEXT, llm_context)

        # Access model attributes that were set using set_span_attributes
        model_attributes = get_span_attributes(event.agent.model)
        current_model_span = trace.get_current_span()
        if model_attributes:
            attributes = {
                f'fiddler.span.user.{k}': v for k, v in model_attributes.items()
            }
            current_model_span.set_attributes(attributes)

    def before_invocation(self, event: BeforeInvocationEvent) -> None:
        """
        Handle the start of an agent invocation.

        Enriches the current OpenTelemetry span with conversation ID and session
        attributes that were set using set_conversation_id() and set_session_attributes().
        This ensures trace-level context is available for all child spans.

        Args:
            event: BeforeInvocationEvent containing agent invocation details
        """
        # Set the conversation ID and session attributes on the span
        conversation_id = get_conversation_id(event.agent)
        session_attributes = get_session_attributes(event.agent)
        current_span = trace.get_current_span()
        if conversation_id:
            current_span.set_attribute(FIDDLER_CONVERSATION_ID, conversation_id)
        if session_attributes:
            current_span.set_attributes(
                {
                    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.format(key=k): v
                    for k, v in session_attributes.items()
                }
            )
