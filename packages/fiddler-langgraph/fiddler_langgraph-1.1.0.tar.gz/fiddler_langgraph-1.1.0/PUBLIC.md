# fiddler-langgraph

[![Python Version](https://img.shields.io/pypi/pyversions/fiddler-langgraph.svg)](https://pypi.org/project/fiddler-langgraph/)

[![PyPI Version](https://img.shields.io/pypi/v/fiddler-langgraph.svg)](https://pypi.org/project/fiddler-langgraph/)

[![License](https://img.shields.io/pypi/l/fiddler-langgraph.svg)](https://pypi.org/project/fiddler-langgraph/)

The official Python SDK for instrumenting GenAI Applications with [Fiddler](https://www.fiddler.ai) using OpenTelemetry and LangGraph. Monitor, analyze, and protect your LangGraph workflows, LLMs, and AI Agents in production.

## Platform Features

- 🚀 **Easy Integration** - Simple Python API for LangGraph application instrumentation
- 📊 **OpenTelemetry Tracing** - Full distributed tracing support with configurable span limits
- 🔍 **Automatic Instrumentation** - Zero-config tracing for LangGraph workflows, chains, and tools
- 🎯 **LLM Context Management** - Set additional context for LLM processing with `set_llm_context()`
- 💬 **Conversation Tracking** - Track multi-turn conversations with `set_conversation_id()`
- 📈 **Performance Metrics** - Automatic tracking of timing, token usage, and model information
- 🛡️ **Error Handling** - Comprehensive error tracking with detailed stack traces
- 🔄 **Flexible Configuration** - Custom span limits, sampling strategies, and batch processing
- 📊 **Resource Management** - Conservative defaults to prevent resource exhaustion
- 🎨 **Message Serialization** - Smart handling of complex message content (lists, dicts)
- 🔔 **Attribute Truncation** - Automatic truncation of long attribute values to prevent oversized spans

## Installation

```bash
pip install fiddler-langgraph
```

## Requirements

- Python 3.10, 3.11, 3.12, or 3.13
- LangGraph >= 0.3.28 and <= 1.0.2 or Langchain >= 0.3.28 and <= 1.0.2

### With Example Dependencies

To run the example scripts:

```bash
pip install fiddler-langgraph[examples]
```

## Quick Start

```python
from fiddler_langgraph import FiddlerClient
from fiddler_langgraph.tracing.instrumentation import LangGraphInstrumentor, set_llm_context, set_conversation_id

# Initialize the FiddlerClient
client = FiddlerClient(
    url="https://your-instance.fiddler.ai",
    api_key="your-api-key",
    application_id="your-application-id"  # Must be a valid UUID4
)

# Instrument LangGraph applications
LangGraphInstrumentor(client).instrument()

# Set additional context for LLM processing
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model='gpt-4o-mini')
set_llm_context(model, "Previous conversation context")

# Set conversation ID for multi-turn conversations
from langgraph.graph import StateGraph
workflow = StateGraph(state_schema=State)
app = workflow.compile()
set_conversation_id("conversation_123")
app.invoke({"messages": [{"role": "user", "content": "Write a novel"}]})
```

## Documentation

* 📚 [Complete Documentation](https://docs.fiddler.ai/)
* 🚀 [LangGraph Quick Start Guide](https://docs.fiddler.ai/developers/tutorials/llm-monitoring/langgraph-sdk-quick-start)
* 📖 [API Reference](https://docs.fiddler.ai/api/fiddler-langgraph-sdk/langgraph)

## Example Usage

### Basic Instrumentation

```python
from fiddler_langgraph.tracing.instrumentation import LangGraphInstrumentor

# Initialize and instrument
instrumentor = LangGraphInstrumentor(client)
instrumentor.instrument()
```

### Setting LLM Context

```python
from fiddler_langgraph.tracing.instrumentation import set_llm_context
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model='gpt-4o-mini')
set_llm_context(model, "User prefers concise responses")
```

### Conversation Tracking

```python
from fiddler_langgraph.tracing.instrumentation import set_conversation_id
import uuid

# Set conversation ID for tracking multi-turn conversations
conversation_id = str(uuid.uuid4())
set_conversation_id(conversation_id)
```

### Advanced Configuration

```python
from opentelemetry.sdk.trace import SpanLimits, sampling
from opentelemetry.exporter.otlp.proto.http.trace_exporter import Compression

# Custom span limits for high-volume applications
custom_limits = SpanLimits(
    max_events=64,
    max_links=64,
    max_span_attributes=64,
    max_event_attributes=64,
    max_link_attributes=64,
    max_span_attribute_length=4096,
)

# Sampling strategy for production
sampler = sampling.TraceIdRatioBased(0.1)  # Sample 10% of traces

client = FiddlerClient(
    api_key="your-api-key",
    application_id="your-app-id",
    url="https://your-instance.fiddler.ai",
    span_limits=custom_limits,
    sampler=sampler,
    console_tracer=False,  # Set to True for debugging
    compression=Compression.Gzip,  # Enable gzip compression (default)
)
```

## Example Notebooks

Check out our [GitHub repository](https://github.com/fiddler-labs/fiddler-sdk/tree/main/examples) for example scripts demonstrating:

- Basic LangGraph instrumentation
- LLM context management
- Conversation tracking
- Multi-agent workflows
- Travel agent applications
- Chatbot implementations

## Version History

See our [release notes](https://docs.fiddler.ai/history/python-client-history) for detailed version history.

## Support

- 📧 Email: [support@fiddler.ai](mailto:support@fiddler.ai)
- 💬 Community: [Join our Slack](https://www.fiddler.ai/slack)
- 🐛 Issues: [GitHub Issues](https://github.com/fiddler-labs/fiddler-sdk/issues)

## License

Apache License 2.0 - see LICENSE file for details

---

**Want to see Fiddler in action?** [Request a demo](https://www.fiddler.ai/demo)
