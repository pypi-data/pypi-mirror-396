# Fiddler Strands SDK

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

OpenTelemetry instrumentation SDK for [Strands AI](https://strands.ai) agents, providing automatic observability and monitoring capabilities through Fiddler's platform.

## Features

- 🎯 **Automatic Instrumentation**: Zero-code instrumentation of Strands agents using OpenTelemetry
- 🔍 **Built-in Observability**: Automatic logging hooks for agent interactions
- 📊 **Fiddler Integration**: Custom span processors for enhanced trace analysis
- 🛠️ **Extensible**: Easy to add custom hooks and processors
- 🚀 **Production Ready**: Built on OpenTelemetry standards

## Installation

### Using uv (Recommended)

```bash
# Install the SDK
uv add fiddler-strands
```

### Using pip

```bash
pip install fiddler-strands
```

## Quick Start

### Prerequisites

Before using the SDK, ensure you have:
- **Fiddler platform access** with API credentials
- **OpenAI API key** (if using OpenAI models)
- Configure environment variables:
  - `FIDDLER_ENDPOINT`: Your Fiddler platform URL
  - `FIDDLER_TOKEN`: Your Fiddler API token
  - `FIDDLER_APPLICATION_UUID`: Your application UUID from Fiddler

See the [full documentation](https://docs.fiddler.ai/api/fiddler-strands-sdk/strands) for detailed configuration steps.

### Basic Usage

```python
import os
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.telemetry import StrandsTelemetry
from fiddler_strandsagents import StrandsAgentInstrumentor

strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()
strands_telemetry.setup_console_exporter()
# Enable automatic instrumentation
StrandsAgentInstrumentor(strands_telemetry).instrument()

# Create your agent as usual - LoggingHook will be automatically injected
model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY"))
agent = Agent(model=model, system_prompt="You are a helpful assistant")

# Use your agent - all interactions will be automatically instrumented
response = agent("Hello, how are you?")
```

**Note:** The OTLP exporter requires Fiddler credentials to be configured as environment variables.

## API Reference

### StrandsAgentInstrumentor

The main instrumentor class for automatic agent instrumentation.

```python
from fiddler_strandsagents import StrandsAgentInstrumentor

instrumentor = StrandsAgentInstrumentor()

# Enable instrumentation
instrumentor.instrument()

# Check if instrumentation is active
is_active = instrumentor.is_instrumented_by_opentelemetry

# Disable instrumentation
instrumentor.uninstrument()
```

### Helper Functions

The SDK provides helper functions to add custom metadata to your telemetry spans:

#### `set_conversation_id(agent, conversation_id)`

Set a unique conversation ID for tracking related interactions:

```python
from fiddler_strandsagents import set_conversation_id

set_conversation_id(agent, 'session_1234567890')
```

#### `set_session_attributes(agent, **kwargs)`

Add custom session-level attributes to track business context:

```python
from fiddler_strandsagents import set_session_attributes

set_session_attributes(agent,
    role='customer_support',
    cost_center='travel_desk',
    region='us-west'
)
```

#### `set_span_attributes(obj, **kwargs)`

Add custom attributes to specific components (agents, models, or tools):

```python
from fiddler_strandsagents import set_span_attributes

# Add attributes to a model
set_span_attributes(model, model_id='gpt-4o-mini', temperature=0.7)

# Add attributes to a tool
set_span_attributes(tool, department='search', version='2.0')
```

#### `set_llm_context(model, context)`

Set additional context for LLM interactions:

```python
from fiddler_strandsagents import set_llm_context

set_llm_context(model, 'Available options: Option A, Option B, Option C...')
```

#### Getter Functions

Retrieve previously set metadata:

```python
from fiddler_strandsagents import (
    get_conversation_id,
    get_session_attributes,
    get_span_attributes
)

conversation_id = get_conversation_id(agent)
attributes = get_session_attributes(agent)
span_attrs = get_span_attributes(model)
```

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@fiddler.ai
- 📖 Documentation: https://docs.fiddler.ai/api/fiddler-strands-sdk/strands
- 🐛 Issues: https://github.com/fiddler-labs/fiddler-strands-sdk/issues

## Examples and Development

For example scripts and development information, please visit the [GitHub repository](https://github.com/fiddler-labs/fiddler-strands-sdk).
