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

# For development
uv add fiddler-strands[dev]

# For running examples
uv add fiddler-strands[examples]
```

### Using pip

```bash
pip install fiddler-strands
```

## Quick Start

### Prerequisites

Before using the SDK, ensure you have:
- **Fiddler credentials** configured as environment variables (see [Configuration](#configuration) section below)
- **OpenAI API key** (if using OpenAI models)

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

**Note:** The OTLP exporter requires Fiddler credentials to be configured. See the [Configuration](#configuration) section in Examples for setup details.

## Examples

The `examples/` directory contains complete working examples:

- **`travel_agent.py`**: Complete travel booking agent with tools
- **`async_travel_agent.py`**: Async version of the travel booking agent

**Note:** The `[examples]` extra includes `strands-agents-tools`, which provides pre-built tools like `calculator` used in the examples.

### Running Examples

```bash
# Clone the repository
git clone https://github.com/fiddler-labs/fiddler-strands-sdk
cd fiddler-strands-sdk

# Copy the example environment file and configure it
cp .env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY (required)
# - FIDDLER_ENDPOINT, FIDDLER_TOKEN, FIDDLER_APPLICATION_UUID (optional - for Fiddler integration)

# Install dependencies (includes openai, strands-agents-tools, and python-dotenv)
uv sync --extra examples

# Run an example
uv run python examples/travel_agent.py
```

#### Configuration

The examples require:

**Required:**
- `OPENAI_API_KEY`: Your OpenAI API key for running the agent

**Optional (for Fiddler telemetry):**
- `FIDDLER_ENDPOINT`: Your Fiddler platform URL (e.g., `https://app.fiddler.ai`)
- `FIDDLER_TOKEN`: API token from your Fiddler dashboard
- `FIDDLER_APPLICATION_UUID`: Application UUID from Fiddler

If Fiddler credentials are not provided, examples will run with console-only telemetry output. To enable full Fiddler integration:

1. Create an application in your Fiddler dashboard
2. Generate an API token
3. Add the credentials to your `.env` file
4. Run the examples - traces will be sent to Fiddler automatically

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

set_conversation_id(travel_agent, 'session_1234567890')
```

#### `set_session_attributes(agent, **kwargs)`

Add custom session-level attributes to track business context:

```python
from fiddler_strandsagents import set_session_attributes

set_session_attributes(travel_agent,
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
set_span_attributes(search_hotel, department='search', version='2.0')
```

#### `set_llm_context(model, context)`

Set additional context for LLM interactions:

```python
from fiddler_strandsagents import set_llm_context

set_llm_context(model, 'Available hotels: Hilton, Marriott, Hyatt...')
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

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/fiddler-labs/fiddler-strands-sdk
cd fiddler-strands-sdk

# Install with development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linting
uv run black fiddler_strandsagents/ examples/
uv run isort fiddler_strandsagents/ examples/
uv run flake8 fiddler_strandsagents/ examples/
```

### Project Structure

```
fiddler-strands-sdk/
├── fiddler_strandsagents/    # Main SDK package
│   ├── __init__.py             # Public API exports
│   ├── instrumentation.py      # OpenTelemetry instrumentor
│   ├── hooks.py                # Hook providers
│   ├── span_processor.py       # Custom span processors
│   ├── attributes.py           # Attribute management utilities
│   ├── constants.py            # SDK constants and configuration
│   └── VERSION                 # Version information
├── examples/                   # Usage examples
│   ├── travel_agent.py         # Synchronous travel agent example
│   └── async_travel_agent.py   # Asynchronous travel agent example
├── tests/                      # Test suite
├── .env.example               # Environment variable template
├── pyproject.toml             # Project configuration
└── README.md                  # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`uv run pytest && uv run black fiddler_strandsagents/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@fiddler.ai
- 📖 Documentation: https://docs.fiddler.ai/api/fiddler-strands-sdk/strands
- 🐛 Issues: https://github.com/fiddler-labs/fiddler-strands-sdk/issues
