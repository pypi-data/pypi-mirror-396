"""
OpenTelemetry span processors for Fiddler integration.

This module provides custom span processors that enhance OpenTelemetry
traces with Fiddler-specific attributes and functionality.
"""

import logging
from typing import List, Optional

from opentelemetry import context
from opentelemetry.sdk.trace import Span, SpanProcessor
from opentelemetry.trace import get_current_span

from fiddler_strandsagents.constants import (
    FIDDLER_CONVERSATION_ID,
    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE,
    GEN_AI_AGENT_ID,
    GEN_AI_AGENT_NAME,
    GEN_AI_TOOL_DEFINITIONS,
    GENAI_SYSTEM_MESSAGE,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


class FiddlerSpanProcessor(SpanProcessor):
    """
    Span processor for Fiddler that denormalizes attributes from parent spans.

    This processor copies specific attributes from parent spans to child spans,
    enabling better trace analysis and monitoring in Fiddler's observability platform.
    """

    DENORMALIZED_ATTRIBUTES: List[str] = [
        GEN_AI_AGENT_NAME,
        GEN_AI_AGENT_ID,
        FIDDLER_CONVERSATION_ID,
        SYSTEM_PROMPT,
        GEN_AI_TOOL_DEFINITIONS,
    ]

    def on_start(self, span: Span, parent_context: Optional[context.Context] = None):
        """
        Called when a span is started.

        Copies denormalized attributes from the parent span to the current span.

        Args:
            span: The span that is being started
            parent_context: The parent context, if any
        """
        # Get the parent span from the context
        parent_span = get_current_span(parent_context)

        # Check if parent span is valid and has attributes
        try:
            if (
                parent_span
                and hasattr(parent_span, 'is_recording')
                and parent_span.is_recording()
                and hasattr(parent_span, 'attributes')
            ):
                # Get all attributes from the parent span
                parent_attributes = parent_span.attributes

                # Copy predefined denormalized attributes
                for attr in self.DENORMALIZED_ATTRIBUTES:
                    if attr in parent_attributes:
                        span.set_attribute(attr, parent_attributes.get(attr))

                # if span type is chat, add the system message to the span
                # as per gen_ai convention, this should have been added by strands itself
                # an issue is open in github for the same
                # https://github.com/strands-agents/sdk-python/issues/822
                if span.name == 'chat':
                    span.add_event(
                        GENAI_SYSTEM_MESSAGE,
                        attributes={
                            'content': parent_attributes.get(SYSTEM_PROMPT, '')
                        },
                    )

                # Copy any attributes with FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE prefix
                # Extract the prefix pattern by removing '{key}' placeholder.
                # This is necessary because startswith() matches literal strings, not templates.
                # Template: 'fiddler.session.user.{key}' -> Prefix: 'fiddler.session.user.'
                # This allows matching attributes like 'fiddler.session.user.user_id',
                # 'fiddler.session.user.session_id', etc.
                prefix_pattern = FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.replace(
                    '{key}', ''
                )

                for attr_name, attr_value in parent_attributes.items():
                    if attr_name.startswith(prefix_pattern) and attr_value is not None:
                        span.set_attribute(attr_name, attr_value)
        except Exception as e:  # pylint: disable=broad-except
            # Log but don't raise - we don't want attribute copying failures to break tracing
            logger.debug(
                'Failed to copy attributes from parent span: %s', str(e), exc_info=True
            )

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Force flush any pending spans. No-op for this processor.

        This method is required by the SpanProcessor interface but is not needed
        for FiddlerSpanProcessor since it processes spans synchronously on_start.

        Args:
            timeout_millis: Maximum time in milliseconds to wait for flush completion.
                Not used in this implementation. Defaults to 30000.

        Returns:
            Always returns True since this is a no-op implementation
        """
        return True
