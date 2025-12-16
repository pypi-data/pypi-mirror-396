#!/usr/bin/env python3
"""
OpenTelemetry instrumentation for automatically injecting logging hooks
into all Strands Agent instances.

This module uses OpenTelemetry's BaseInstrumentor to properly instrument
the Agent class and automatically add LoggingHook to all agents without
requiring manual specification.
"""

import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import (  # type: ignore[attr-defined]
    BaseInstrumentor,
)
from strands import Agent
from strands.telemetry import StrandsTelemetry
from wrapt import wrap_function_wrapper

from fiddler_strandsagents.span_processor import FiddlerSpanProcessor

from .hooks import FiddlerInstrumentationHook

logger = logging.getLogger(__name__)


class StrandsAgentInstrumentor(BaseInstrumentor):
    """
    OpenTelemetry instrumentor for Strands AI agents.

    This instrumentor automatically injects FiddlerInstrumentationHook into all
    Strands Agent instances, enabling automatic observability without manual hook
    configuration. It also registers a FiddlerSpanProcessor for attribute denormalization.

    The instrumentor follows the OpenTelemetry instrumentation pattern and can be
    enabled/disabled dynamically.

    Example:
        .. code-block:: python

            from strands.telemetry import StrandsTelemetry
            from fiddler_strandsagents import StrandsAgentInstrumentor

            telemetry = StrandsTelemetry()
            telemetry.setup_otlp_exporter()

            # Enable instrumentation
            instrumentor = StrandsAgentInstrumentor(telemetry)
            instrumentor.instrument()

            # Create agents - hooks are automatically injected
            agent = Agent(model=model, system_prompt="...")
    """

    def __init__(self, strands_telemetry: StrandsTelemetry):
        """
        Initialize the Strands Agent instrumentor.

        Args:
            strands_telemetry: StrandsTelemetry instance for configuring trace exporters
        """
        self.strands_telemetry = strands_telemetry
        self._original_agent_init = Agent.__init__
        super().__init__()

    def instrumentation_dependencies(self) -> Collection[str]:
        """
        Return the list of packages required for instrumentation.

        Returns:
            Collection of package names with version constraints
        """
        return ['strands-agents']

    def instrument(self, **kwargs):
        """
        Enable automatic instrumentation of Strands agents.

        Activates the instrumentor by registering the FiddlerSpanProcessor with
        the tracer provider and patching Agent.__init__ to automatically inject
        FiddlerInstrumentationHook into all agent instances.

        This method is idempotent - calling it multiple times has the same effect
        as calling it once. After activation, all newly created agents will
        automatically include Fiddler's instrumentation hook.

        Args:
            **kwargs: Additional instrumentation configuration (currently unused)

        Example:
            .. code-block:: python

                from strands import Agent
                from strands.telemetry import StrandsTelemetry
                from fiddler_strandsagents import StrandsAgentInstrumentor

                # Set up telemetry
                telemetry = StrandsTelemetry()
                telemetry.setup_otlp_exporter()

                # Activate instrumentation
                instrumentor = StrandsAgentInstrumentor(telemetry)
                instrumentor.instrument()

                # Agents created after this point are automatically instrumented
                agent = Agent(model=model, system_prompt="...")

                # Check if instrumentation is active
                if instrumentor.is_instrumented_by_opentelemetry:
                    print("Instrumentation is active")
        """
        return super().instrument(**kwargs)

    def uninstrument(self, **kwargs):
        """
        Disable automatic instrumentation and restore original behavior.

        Deactivates the instrumentor by restoring the original Agent.__init__
        method. Agents created after calling this method will no longer have
        FiddlerInstrumentationHook automatically injected.

        Note: This does not affect agents that were already created while
        instrumentation was active - those will retain their hooks.

        Args:
            **kwargs: Additional uninstrumentation configuration (currently unused)

        Example:
            .. code-block:: python

                from fiddler_strandsagents import StrandsAgentInstrumentor

                instrumentor = StrandsAgentInstrumentor(telemetry)
                instrumentor.instrument()

                # Create some agents (automatically instrumented)
                agent1 = Agent(model=model, system_prompt="...")

                # Deactivate instrumentation
                instrumentor.uninstrument()

                # New agents won't be instrumented
                agent2 = Agent(model=model, system_prompt="...")

                # agent1 still has the hook, agent2 does not
        """
        return super().uninstrument(**kwargs)

    @property
    def is_instrumented_by_opentelemetry(self) -> bool:
        """
        Check whether instrumentation is currently active.

        Returns:
            True if the instrumentor has been activated via instrument() and
            not yet deactivated via uninstrument(), False otherwise

        Example:
            .. code-block:: python

                instrumentor = StrandsAgentInstrumentor(telemetry)
                print(instrumentor.is_instrumented_by_opentelemetry)  # False

                instrumentor.instrument()
                print(instrumentor.is_instrumented_by_opentelemetry)  # True

                instrumentor.uninstrument()
                print(instrumentor.is_instrumented_by_opentelemetry)  # False
        """
        return super().is_instrumented_by_opentelemetry

    def _instrument(self, **kwargs):
        """
        Enable instrumentation by patching Agent.__init__.

        Registers FiddlerSpanProcessor with the tracer provider and wraps
        the Agent constructor to automatically inject FiddlerInstrumentationHook.

        Args:
            **kwargs: Additional instrumentation configuration (unused)
        """
        self.strands_telemetry.tracer_provider.add_span_processor(
            FiddlerSpanProcessor()
        )
        _agent_class = Agent

        wrap_function_wrapper(
            _agent_class,
            '__init__',
            self._patched_agent_init,
        )
        logger.info(
            '🎯 Strands Agent instrumentation enabled - LoggingHook will be injected'
        )

    def _uninstrument(self, **kwargs):
        """
        Disable instrumentation by restoring original Agent.__init__.

        Args:
            **kwargs: Additional uninstrumentation configuration (unused)
        """
        Agent.__init__ = self._original_agent_init
        logger.info('⚠️ Uninstrumenting Strands Agent instrumentation')

    def _patched_agent_init(self, wrapped, instance, args, kwargs):
        """
        Patched Agent initialization that injects FiddlerInstrumentationHook.

        This method is called via wrapt whenever an Agent is instantiated.
        It automatically adds FiddlerInstrumentationHook to the hooks list
        if not already present.

        Args:
            wrapped: The original Agent.__init__ method
            instance: The Agent instance (required by wrapt, may appear unused)
            args: Positional arguments to Agent.__init__
            kwargs: Keyword arguments to Agent.__init__

        Returns:
            Result of calling the original Agent.__init__
        """
        existing_hooks = kwargs.get('hooks', [])
        if existing_hooks is None:
            existing_hooks = []

        if not any(isinstance(h, FiddlerInstrumentationHook) for h in existing_hooks):
            existing_hooks.append(FiddlerInstrumentationHook())
            kwargs['hooks'] = existing_hooks

        return wrapped(*args, **kwargs)
