"""OpenTelemetry span attributes for Fiddler instrumentation."""

import contextvars
from typing import Any

# Key used for storing Fiddler-specific attributes in metadata dictionary
FIDDLER_METADATA_KEY = '_fiddler_attributes'

# Template strings for OpenTelemetry attribute key formatting
FIDDLER_USER_SPAN_ATTRIBUTE_TEMPLATE = 'fiddler.span.user.{key}'
FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE = 'fiddler.session.user.{key}'


class FiddlerSpanAttributes:  # pylint: disable=too-few-public-methods
    """Constants for Fiddler OpenTelemetry span attributes."""

    # common attributes
    AGENT_NAME = 'gen_ai.agent.name'
    AGENT_ID = 'gen_ai.agent.id'
    CONVERSATION_ID = 'gen_ai.conversation.id'
    TYPE = 'fiddler.span.type'

    # LLM attributes
    LLM_INPUT_SYSTEM = 'gen_ai.llm.input.system'
    LLM_INPUT_USER = 'gen_ai.llm.input.user'
    LLM_OUTPUT = 'gen_ai.llm.output'
    LLM_CONTEXT = 'gen_ai.llm.context'

    # Model attributes - following OpenTelemetry semantic conventions
    LLM_REQUEST_MODEL = 'gen_ai.request.model'
    LLM_SYSTEM = 'gen_ai.system'

    # Token usage attributes
    LLM_TOKEN_COUNT_INPUT = 'gen_ai.usage.input_tokens'
    LLM_TOKEN_COUNT_OUTPUT = 'gen_ai.usage.output_tokens'
    LLM_TOKEN_COUNT_TOTAL = 'gen_ai.usage.total_tokens'

    # tool attributes
    TOOL_INPUT = 'gen_ai.tool.input'
    TOOL_OUTPUT = 'gen_ai.tool.output'
    TOOL_NAME = 'gen_ai.tool.name'
    TOOL_DEFINITIONS = 'gen_ai.tool.definitions'


class FiddlerResourceAttributes:
    """Constants for Fiddler OpenTelemetry resource attributes."""

    APPLICATION_ID = 'application.id'


class SpanType:
    """Constants for Fiddler OpenTelemetry span types."""

    CHAIN = 'chain'
    TOOL = 'tool'
    LLM = 'llm'
    OTHER = 'other'


# context variable for conversation ID - used to store the conversation ID for the current thread/async coroutine
# note that contextvars are shallow copied, dictionaries/lists are not copied deeply and are shared between threads/coroutines
_CONVERSATION_ID: contextvars.ContextVar[str] = contextvars.ContextVar(
    '_CONVERSATION_ID', default=''
)
_CUSTOM_ATTRIBUTES: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    '_CUSTOM_ATTRIBUTES'
)
