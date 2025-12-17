"""Callback handler for LangGraph instrumentation."""

import json
import logging
from collections.abc import Sequence
from functools import cached_property
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from opentelemetry import trace
from opentelemetry.context.context import Context

from fiddler_langgraph.core.attributes import (
    _CONVERSATION_ID,
    FIDDLER_METADATA_KEY,
    FIDDLER_USER_SPAN_ATTRIBUTE_TEMPLATE,
    FiddlerSpanAttributes,
    SpanType,
)
from fiddler_langgraph.tracing.util import _LanggraphJSONEncoder

logger = logging.getLogger(__name__)


def _get_agent_name(metadata: dict[str, Any]) -> str:
    """Get the agent name from the kwargs."""
    agent_name = ''
    checkpoint_ns = metadata.get('langgraph_checkpoint_ns', '')
    if checkpoint_ns:
        path = checkpoint_ns.split(':')
        agent_name = path[0]
    return agent_name


def _set_agent_name(span: trace.Span, metadata: dict[str, Any]) -> None:
    """Get the agent name from the kwargs."""
    agent_name = _get_agent_name(metadata)
    span.set_attribute(FiddlerSpanAttributes.AGENT_NAME, agent_name)
    _set_agent_id(span, agent_name)


def _set_agent_id(span: trace.Span, agent_name: str) -> None:
    """Set the agent ID on the span."""
    trace_id = format(span.get_span_context().trace_id, '032x')
    agent_id = str(trace_id) + ':' + agent_name
    span.set_attribute(FiddlerSpanAttributes.AGENT_ID, agent_id)


def _stringify_message_content(message: BaseMessage) -> str:
    """Stringify a message."""
    if isinstance(message.content, str):
        return message.content
    return json.dumps(message.content, cls=_LanggraphJSONEncoder)


def _set_model_attributes(span: trace.Span, metadata: dict[str, Any] | None = None) -> None:
    """Set model-related attributes on a span.

    Extracts model name and provider from metadata.

    Parameters
    ----------
    span : trace.Span
        The OpenTelemetry span to set attributes on
    metadata : dict[str, Any] | None
        The metadata containing model information

    """
    if not metadata:
        return

    # Extract model information
    ls_model_name = metadata.get('ls_model_name')
    ls_provider = metadata.get('ls_provider')

    # Set model name attribute
    if ls_model_name and isinstance(ls_model_name, str) and ls_model_name.strip():
        span.set_attribute(FiddlerSpanAttributes.LLM_REQUEST_MODEL, ls_model_name.strip())

    # Set provider attribute
    if ls_provider and isinstance(ls_provider, str) and ls_provider.strip():
        span.set_attribute(FiddlerSpanAttributes.LLM_SYSTEM, ls_provider.strip())


def _set_token_usage_attributes(span: trace.Span, response: LLMResult) -> None:
    """Set token usage attributes on a span from LLMResult.

    Extracts token usage information from the LLM response

    Parameters
    ----------
    span : trace.Span
        The OpenTelemetry span to set attributes on
    response : LLMResult
        The LLM response containing token usage information

    """
    try:
        if not response.generations or not response.generations[0]:
            return

        generation = response.generations[0][0]

        if not (
            isinstance(generation, ChatGeneration)
            and hasattr(generation.message, 'usage_metadata')
            and generation.message.usage_metadata
        ):
            return

        usage_metadata = generation.message.usage_metadata

        # Set input tokens
        input_tokens = usage_metadata.get('input_tokens')
        if input_tokens is not None and isinstance(input_tokens, int):
            span.set_attribute(FiddlerSpanAttributes.LLM_TOKEN_COUNT_INPUT, input_tokens)

        # Set output tokens
        output_tokens = usage_metadata.get('output_tokens')
        if output_tokens is not None and isinstance(output_tokens, int):
            span.set_attribute(FiddlerSpanAttributes.LLM_TOKEN_COUNT_OUTPUT, output_tokens)

        # Set total tokens
        total_tokens = usage_metadata.get('total_tokens')
        if total_tokens is not None and isinstance(total_tokens, int):
            span.set_attribute(FiddlerSpanAttributes.LLM_TOKEN_COUNT_TOTAL, total_tokens)
        else:
            # Calculate total if not provided
            if input_tokens and output_tokens:
                calculated_total = input_tokens + output_tokens
                span.set_attribute(FiddlerSpanAttributes.LLM_TOKEN_COUNT_TOTAL, calculated_total)

    except Exception as e:
        logger.warning('Failed to extract token usage: %s', e)


def _set_tool_definitions(span: trace.Span, kwargs: dict[str, Any]) -> None:
    """Extract and set tool definitions on the span.

    Retrieves tool definitions from invocation params and stores them as a
    JSON-serialized string attribute on the span.

    Parameters
    ----------
    span : trace.Span
        The OpenTelemetry span to set attributes on
    kwargs : dict[str, Any]
        Callback kwargs containing invocation_params

    """
    try:
        invocation_params = kwargs.get('invocation_params', {})
        tools = invocation_params.get('tools')

        if tools and isinstance(tools, list) and len(tools) > 0:
            # Store tool definitions as-is in OpenAI native format
            tool_definitions_json = json.dumps(tools, cls=_LanggraphJSONEncoder)
            span.set_attribute(FiddlerSpanAttributes.TOOL_DEFINITIONS, tool_definitions_json)
    except Exception as e:
        logger.warning('Failed to extract tool definitions: %s', e)


class _CallbackHandler(BaseCallbackHandler):
    """A LangChain callback handler that creates OpenTelemetry spans for Fiddler.

    This handler listens to events from LangGraph and creates corresponding
    spans to trace the execution of chains, tools, and language models.
    It is responsible for managing the lifecycle of these spans, including
    their creation, activation, and completion.

    Attributes:
        _tracer (trace.Tracer): The OpenTelemetry tracer used to create spans.
        _active_spans (dict[UUID, trace.Span]): A dictionary mapping run IDs
            to active spans.
        _root_span (trace.Span | None): The root span of the current trace.
        session_id (str | None): The ID of the current conversation or session.
    """

    def __init__(self, tracer: trace.Tracer):
        """Initializes the callback handler.

        Args:
            tracer: The OpenTelemetry tracer to use for creating and managing spans.
        """
        self._active_spans: dict[UUID, trace.Span] = {}
        self._tracer = tracer
        self._root_span: trace.Span | None = None
        # our callback handler needs to have its own context
        # so that the spans created by the callback handler are not affected by the global context
        # if the global context is set to a different trace, the spans created by the callback handler
        # will be part of a different trace
        self._context = Context()

    def _start_new_trace(self, trace_name: str) -> trace.Span:
        """Start a new trace with the given name."""
        span = self._tracer.start_span(
            trace_name, kind=trace.SpanKind.CLIENT, context=self._context
        )
        span.set_attribute(FiddlerSpanAttributes.TYPE, SpanType.CHAIN)
        # we don't know the agent name when the graph starts, so we set it to unknown
        # we will update it when the second chain starts
        span.set_attribute(FiddlerSpanAttributes.AGENT_NAME, 'unknown')
        _set_agent_id(span, 'unknown')
        self._set_session_id(span)
        self._root_span = span

        return span

    def _add_span(self, span: trace.Span, run_id: UUID) -> None:
        """Adds a span to the active spans dictionary."""
        self._active_spans[run_id] = span

    def _get_span(self, run_id: UUID | None) -> trace.Span | None:
        """Retrieves a span from the active spans dictionary by its run ID."""
        if run_id is None:
            return None
        return self._active_spans.get(run_id)

    def _remove_span(self, run_id: UUID) -> None:
        """Removes a span from the active spans dictionary."""
        del self._active_spans[run_id]
        if len(self._active_spans) == 0:
            # reset the root span if no active spans are left
            self._root_span = None

    def _set_fiddler_attributes_from_metadata(
        self, span: trace.Span, metadata: dict[str, Any] | None
    ) -> None:
        """Sets Fiddler-specific attributes on a span from metadata."""
        if metadata is not None:
            fiddler_attributes = metadata.get(FIDDLER_METADATA_KEY, {})
            for key, value in fiddler_attributes.items():
                # FiddlerSpanAttributes keys should not be prefixed with fiddler.span.user.
                fdl_key = (
                    key
                    if key in vars(FiddlerSpanAttributes).values()
                    else FIDDLER_USER_SPAN_ATTRIBUTE_TEMPLATE.format(key=key)
                )
                span.set_attribute(fdl_key, value)

    def _update_root_span_agent_name(self, agent_name: str) -> None:
        """Updates the agent name on the root span.

        The root span is created without an agent name, so this method is
        used to update it once the agent name becomes available.

        Args:
            agent_name: The agent name to set on the root span.
        """
        if self._root_span and self._root_span.is_recording():
            self._root_span.set_attribute(FiddlerSpanAttributes.AGENT_NAME, agent_name)
            _set_agent_id(self._root_span, agent_name)

    def _start_trace(self, trace_name: str, run_id: UUID) -> None:
        """Starts a new trace and adds the root span to the active spans."""
        span = self._start_new_trace(trace_name)
        self._add_span(span, run_id)

    @cached_property
    def session_id(self) -> str:
        """Get the session id from the metadata."""
        return _CONVERSATION_ID.get()

    def _set_session_id(self, span: trace.Span) -> None:
        """Sets the session ID as an attribute on the given span."""
        if self.session_id:
            span.set_attribute(FiddlerSpanAttributes.CONVERSATION_ID, self.session_id)

    def _create_child_span(self, parent_span: trace.Span, span_name: str) -> trace.Span:
        """Get a child span."""
        parent_context = trace.set_span_in_context(parent_span, self._context)
        return self._tracer.start_span(span_name, context=parent_context)

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a chain starts.

        This method creates a new span for the chain execution. If this is the
        first event in a trace, it creates a root span. Otherwise, it creates
        a child span of the currently active span.

        Args:
            serialized: The serialized representation of the chain.
            inputs: The inputs to the chain.
            run_id: The unique ID of the chain run.
            parent_run_id: The ID of the parent run, if any.
            tags: A list of tags for the chain.
            metadata: A dictionary of metadata for the chain.
            **kwargs: Additional keyword arguments.
        """
        if not self._root_span:
            trace_name = kwargs.get('name', 'unknown')
            self._start_trace(trace_name, run_id)
            return
        agent_name = _get_agent_name(metadata) if metadata is not None else 'unknown'
        parent_span = self._get_span(parent_run_id)
        if parent_span is None:
            # if for some reason the parent span is not found, we can just return - don't generate faulty child spans
            logger.warning(
                'on_chain_start no parent span for run_id %s , parent_run_id %s',
                run_id,
                parent_run_id,
            )
            return
        child_span = self._create_child_span(parent_span, kwargs.get('name', 'unknown'))

        child_span.set_attribute(FiddlerSpanAttributes.TYPE, SpanType.CHAIN)
        child_span.set_attribute(FiddlerSpanAttributes.AGENT_NAME, agent_name)
        _set_agent_id(child_span, agent_name)
        self._update_root_span_agent_name(agent_name)

        if metadata is not None:
            self._set_fiddler_attributes_from_metadata(child_span, metadata)

        self._set_session_id(child_span)
        self._add_span(child_span, run_id)

    def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a chain ends.

        This method finds the corresponding span for the chain run, sets its
        status to OK, and ends the span.

        Args:
            outputs: The outputs of the chain.
            run_id: The unique ID of the chain run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            span.set_status(trace.Status(trace.StatusCode.OK))
            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_chain_end no active span: %s, %s', run_id, kwargs)

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a chain encounters an error.

        This method finds the corresponding span, records the exception, sets
        the status to ERROR, and ends the span.

        Args:
            error: The exception that occurred.
            run_id: The unique ID of the chain run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            span.record_exception(error)
            # Use repr() for more complete error information, fallback to str() if repr() is empty
            error_message = repr(error) if repr(error) else str(error)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_message))
            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_chain_error no active span: %s, %s', run_id, kwargs)

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool starts.

        This method creates a new span for the tool execution as a child of
        the currently active span.

        Args:
            serialized: The serialized representation of the tool.
            input_str: The input to the tool.
            run_id: The unique ID of the tool run.
            parent_run_id: The ID of the parent run, if any.
            tags: A list of tags for the tool.
            metadata: A dictionary of metadata for the tool.
            inputs: The inputs to the tool.
            **kwargs: Additional keyword arguments.
        """
        parent_span = self._get_span(parent_run_id)
        if parent_span is None:
            # if for some reason the parent span is not found, we can just return - don't generate faulty child spans
            logger.warning(
                'on_tool_start no parent span for run_id %s , parent_run_id %s',
                run_id,
                parent_run_id,
            )
            return
        child_span = self._create_child_span(parent_span, serialized.get('name', 'unknown'))
        span_input = json.dumps(inputs, cls=_LanggraphJSONEncoder) if inputs else input_str
        child_span.set_attribute(FiddlerSpanAttributes.TYPE, SpanType.TOOL)
        child_span.set_attribute(FiddlerSpanAttributes.TOOL_NAME, serialized.get('name', 'unknown'))
        child_span.set_attribute(FiddlerSpanAttributes.TOOL_INPUT, span_input)
        if metadata is not None:
            _set_agent_name(child_span, metadata)
            self._set_fiddler_attributes_from_metadata(child_span, metadata)

        self._set_session_id(child_span)
        self._add_span(child_span, run_id)

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool ends.

        This method finds the corresponding span, sets its status to OK, and
        ends the span.

        Args:
            output: The output of the tool.
            run_id: The unique ID of the tool run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            # limit the output to 100 characters for now - add formal limits later
            span.set_attribute(
                FiddlerSpanAttributes.TOOL_OUTPUT,
                json.dumps(output, cls=_LanggraphJSONEncoder),
            )
            span.set_status(trace.Status(trace.StatusCode.OK))
            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_tool_end no active span: %s, %s', run_id, kwargs)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool encounters an error.

        This method finds the corresponding span, records the exception, sets
        the status to ERROR, and ends the span.

        Args:
            error: The exception that occurred.
            run_id: The unique ID of the tool run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            span.record_exception(error)
            # Use repr() for more complete error information, fallback to str() if repr() is empty
            error_message = repr(error) if repr(error) else str(error)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_message))
            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_tool_error no active span: %s, %s', run_id, kwargs)

    def on_retriever_start(
        self,
        serialized: dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a retriever starts.

        This method creates a new span for the retriever execution.

        Args:
            serialized: The serialized representation of the retriever.
            query: The query sent to the retriever.
            run_id: The unique ID of the retriever run.
            parent_run_id: The ID of the parent run, if any.
            tags: A list of tags for the retriever.
            metadata: A dictionary of metadata for the retriever.
            **kwargs: Additional keyword arguments.
        """
        parent_span = self._get_span(parent_run_id)
        if parent_span is None:
            # if for some reason the parent span is not found, we can just return - don't generate faulty child spans
            logger.warning(
                'on_retriever_start no parent span for run_id %s , parent_run_id %s',
                run_id,
                parent_run_id,
            )
            return
        child_span = self._create_child_span(parent_span, kwargs.get('name', 'unknown'))

        child_span.set_attribute(FiddlerSpanAttributes.TYPE, SpanType.TOOL)
        child_span.set_attribute(FiddlerSpanAttributes.TOOL_INPUT, query)

        if metadata is not None:
            _set_agent_name(child_span, metadata)
            self._set_fiddler_attributes_from_metadata(child_span, metadata)

        # semantic convention attributes
        child_span.set_attribute(
            FiddlerSpanAttributes.TYPE, SpanType.TOOL
        )  # document retrieval is a tool
        child_span.set_attribute(FiddlerSpanAttributes.TOOL_NAME, kwargs.get('name', 'unknown'))
        child_span.set_attribute(FiddlerSpanAttributes.TOOL_INPUT, str(query))
        self._set_session_id(child_span)
        self._add_span(child_span, run_id)

    def on_retriever_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a retriever encounters an error.

        This method finds the corresponding span, records the exception, sets
        the status to ERROR, and ends the span.

        Args:
            error: The exception that occurred.
            run_id: The unique ID of the retriever run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            span.record_exception(error)
            # Use repr() for more complete error information, fallback to str() if repr() is empty
            error_message = repr(error) if repr(error) else str(error)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_message))
            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_retriever_error no active span: %s, %s', run_id, kwargs)

    def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a retriever ends.

        This method finds the corresponding span, records the retrieved
        documents as an event, sets the status to OK, and ends the span.

        Args:
            documents: The documents retrieved by the retriever.
            run_id: The unique ID of the retriever run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            span.set_status(trace.Status(trace.StatusCode.OK))
            span.set_attribute(
                FiddlerSpanAttributes.TOOL_OUTPUT,
                json.dumps(documents, cls=_LanggraphJSONEncoder),
            )

            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_retriever_end no active span: %s, %s', run_id, kwargs)

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a chat model starts.

        This method creates a new span for the chat model execution and records
        the input messages as events.

        Args:
            serialized: The serialized representation of the chat model.
            messages: The messages sent to the chat model.
            run_id: The unique ID of the chat model run.
            parent_run_id: The ID of the parent run, if any.
            tags: A list of tags for the chat model.
            metadata: A dictionary of metadata for the chat model.
            **kwargs: Additional keyword arguments.
        """
        parent_span = self._get_span(parent_run_id)
        if parent_span is None:
            # if for some reason the parent span is not found, we can just return - don't generate faulty child spans
            logger.warning(
                'on_llm_start no parent span for run_id %s , parent_run_id %s',
                run_id,
                parent_run_id,
            )
            return
        parent_context = trace.set_span_in_context(parent_span, self._context)
        child_span = self._tracer.start_span(
            serialized.get('name', 'unknown'), context=parent_context
        )

        # chat models are a special case of LLMs with Structure Inputs (messages)
        # the ordering of messages is preserved over the lifecycle of an agent's invocation
        # we are ignoring AIMessage, ToolMessage, FunctionMessage & ChatMessage
        # see https://python.langchain.com/api_reference/core/messages.html#module-langchain_core.messages
        system_message = []
        user_message = []
        if messages and messages[0]:
            system_message = [m for m in messages[0] if isinstance(m, SystemMessage)]
            user_message = [m for m in messages[0] if isinstance(m, HumanMessage)]

        if metadata is not None:
            _set_agent_name(child_span, metadata)

            self._set_fiddler_attributes_from_metadata(child_span, metadata)

        child_span.set_attribute(FiddlerSpanAttributes.TYPE, SpanType.LLM)

        # Set model attributes
        _set_model_attributes(child_span, metadata)

        # Extract and set tool definitions
        _set_tool_definitions(child_span, kwargs)

        # We are only taking the 1st system message and 1st user message
        # as we are not supporting multiple system messages or multiple user messages
        # To support multiple system messages, we would need to add a new attribute with indexing
        # or use event attributes
        system_content = _stringify_message_content(system_message[-1]) if system_message else ''
        user_content = _stringify_message_content(user_message[-1]) if user_message else ''
        child_span.set_attribute(
            FiddlerSpanAttributes.LLM_INPUT_SYSTEM,
            system_content,
        )
        child_span.set_attribute(
            FiddlerSpanAttributes.LLM_INPUT_USER,
            user_content,
        )
        self._set_session_id(child_span)
        self._add_span(child_span, run_id)

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a language model starts.

        This method creates a new span for the language model execution and
        records the prompts as attributes.

        Args:
            serialized: The serialized representation of the language model.
            prompts: The prompts sent to the language model.
            run_id: The unique ID of the language model run.
            parent_run_id: The ID of the parent run, if any.
            tags: A list of tags for the language model.
            metadata: A dictionary of metadata for the language model.
            **kwargs: Additional keyword arguments.
        """
        parent_span = self._get_span(parent_run_id)
        if parent_span is None:
            # if for some reason the parent span is not found, we can just return - don't generate faulty child spans
            logger.warning(
                'on_llm_start no parent span for run_id %s , parent_run_id %s',
                run_id,
                parent_run_id,
            )
            return
        child_span = self._create_child_span(parent_span, serialized.get('name', 'unknown'))

        child_span.set_attribute(FiddlerSpanAttributes.TYPE, SpanType.LLM)

        if metadata is not None:
            _set_agent_name(child_span, metadata)
            self._set_fiddler_attributes_from_metadata(child_span, metadata)

        # Set model attributes
        _set_model_attributes(child_span, metadata)

        # Extract and set tool definitions
        _set_tool_definitions(child_span, kwargs)

        # LLM model is more generic than a chat model, it only has a list on prompts
        # we are using the first prompt as both the system message and the user message
        # to capture all the prompts, we would need to add a new attribute with indexing
        # or use event attributes
        child_span.set_attribute(FiddlerSpanAttributes.LLM_INPUT_SYSTEM, prompts[0])
        child_span.set_attribute(FiddlerSpanAttributes.LLM_INPUT_USER, prompts[0])
        self._set_session_id(child_span)
        self._add_span(child_span, run_id)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a language model ends.

        This method finds the corresponding span, records the model's
        response, sets the status to OK, and ends the span.

        Args:
            response: The response from the language model.
            run_id: The unique ID of the language model run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            span.set_status(trace.Status(trace.StatusCode.OK))

            # assuming we are going to use the first generation for now
            # we always get only one element in the list - even with batch mode
            # Add safety checks to prevent index errors
            output = ''
            if (
                response.generations
                and len(response.generations) > 0
                and response.generations[0]
                and len(response.generations[0]) > 0
            ):
                generation = response.generations[0][0]
                output = generation.text
                if (
                    output == ''
                    and isinstance(generation, ChatGeneration)
                    and isinstance(generation.message, AIMessage)
                    and hasattr(generation.message, 'tool_calls')
                ):
                    # if llm returns an empty string, it means it used a tool
                    # we are using the tool calls to get the output
                    output = json.dumps(generation.message.tool_calls, cls=_LanggraphJSONEncoder)

            span.set_attribute(FiddlerSpanAttributes.LLM_OUTPUT, output)

            # Extract and set token usage information
            _set_token_usage_attributes(span, response)

            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_llm_end no active span: %s, %s', run_id, kwargs)

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        """Called when a language model encounters an error.

        This method finds the corresponding span, records the exception, sets
        the status to ERROR, and ends the span.

        Args:
            error: The exception that occurred.
            run_id: The unique ID of the language model run.
            parent_run_id: The ID of the parent run, if any.
            **kwargs: Additional keyword arguments.
        """
        span = self._get_span(run_id)
        if span:
            span.record_exception(error)
            # Use repr() for more complete error information, fallback to str() if repr() is empty
            error_message = repr(error) if repr(error) else str(error)
            span.set_status(trace.Status(trace.StatusCode.ERROR, error_message))
            span.set_attribute('error_kwargs', str(kwargs))
            span.end()
            self._remove_span(run_id)
        else:
            logger.warning('on_llm_error no active span: %s, %s', run_id, kwargs)
