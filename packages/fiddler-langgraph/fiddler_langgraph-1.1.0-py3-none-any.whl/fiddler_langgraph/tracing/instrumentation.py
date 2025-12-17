"""LangGraph instrumentation module for Fiddler."""

from collections.abc import Callable, Collection
from typing import Any, cast

from langchain_core.callbacks import BaseCallbackManager
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableBinding
from langchain_core.tools import BaseTool
from opentelemetry.instrumentation.instrumentor import (  # type: ignore[attr-defined]
    BaseInstrumentor,
)
from pydantic import ConfigDict, validate_call
from wrapt import wrap_function_wrapper

from fiddler_langgraph.core.attributes import (
    _CONVERSATION_ID,
    _CUSTOM_ATTRIBUTES,
    FIDDLER_METADATA_KEY,
    FiddlerSpanAttributes,
)
from fiddler_langgraph.core.client import FiddlerClient
from fiddler_langgraph.tracing.callback import _CallbackHandler
from fiddler_langgraph.tracing.util import _check_langgraph_version, _get_package_version


@validate_call(config=ConfigDict(strict=True))
def set_conversation_id(conversation_id: str) -> None:
    """Enables end-to-end tracing of multi-step workflows and conversations.

    The primary purpose of set_conversation_id is to enable end-to-end tracing
    of a multi-step workflow. Modern agentic applications often involve a complex
    sequence of events to fulfill a single user request. The result in your Fiddler
    dashboard is that you can instantly filter for and view the entire, ordered
    sequence of operations that constituted a single conversation or task. This is
    crucial for debugging complex failures, analyzing latency across an entire
    workflow, and understanding the agent's behavior from start to finish.

    This will remain in use until it is called again with a new conversation ID.

    Args:
        conversation_id (str): Unique identifier for the conversation session. **Required**.

    Returns:
        None

    Examples:
        .. code-block:: python

            from langgraph.prebuilt import create_react_agent
            from fiddler_langgraph.tracing.instrumentation import set_conversation_id
            import uuid

            # Basic usage
            agent = create_react_agent(model, tools=[])
            conversation_id = str(uuid.uuid4())
            set_conversation_id(conversation_id)
            agent.invoke({"messages": [{"role": "user", "content": "Write me a novel"}]})

            # Multi-turn conversation tracking
            def handle_conversation(user_id, session_id):
                # Create a unique conversation ID combining user and session
                conversation_id = f"{user_id}_{session_id}_{uuid.uuid4()}"
                set_conversation_id(conversation_id)
                return conversation_id

            # Different conversation types
            business_conversation_id = f"business_{uuid.uuid4()}"
            support_conversation_id = f"support_{uuid.uuid4()}"
    """
    _CONVERSATION_ID.set(conversation_id)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def add_session_attributes(key: str, value: str) -> None:
    """Adds custom session-level attributes that persist across all spans in the current context.

    Session attributes are key-value pairs that apply to all operations within the current
    execution context (thread or async coroutine). Use this to add metadata that describes
    the session environment, such as user information, deployment environment, or feature flags.

    These attributes are stored in context variables and automatically included in all spans
    created during the session. They persist until the context ends or the attribute is updated
    with a new value.

    Note: Context variables are shallow copied - modifications to mutable values (lists, dicts)
    are shared between contexts.

    Args:
        key (str): The attribute key to add or update. Will be formatted as
            'fiddler.session.user.{key}' in the OpenTelemetry span. **Required**.
        value (str): The attribute value to set. **Required**.

    Returns:
        None

    Examples:
        .. code-block:: python

            from fiddler_langgraph.tracing.instrumentation import add_session_attributes

            # Add user information to all spans in this session
            add_session_attributes("user_id", "user_12345")
            add_session_attributes("tier", "premium")

            # Add deployment environment context
            add_session_attributes("environment", "production")
            add_session_attributes("region", "us-west-2")

            # Update an existing attribute
            add_session_attributes("user_id", "user_67890")  # Overwrites previous value
    """
    try:
        current_attributes = _CUSTOM_ATTRIBUTES.get().copy()
    except LookupError:
        current_attributes = {}
    current_attributes[key] = value
    _CUSTOM_ATTRIBUTES.set(current_attributes)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def _set_default_metadata(
    node: BaseLanguageModel | BaseRetriever | BaseTool,
) -> None:
    """Ensures a node has the default Fiddler metadata dictionary.

    If `node.metadata` does not exist or is not a dictionary, it will be
    initialized. This function modifies the node in place.

    Args:
        node (BaseLanguageModel | BaseRetriever | BaseTool): The node to modify.
    """
    if not hasattr(node, 'metadata'):
        node.metadata = {}
    if not isinstance(node.metadata, dict):
        node.metadata = {}
    metadata = node.metadata
    if FIDDLER_METADATA_KEY not in metadata:
        metadata[FIDDLER_METADATA_KEY] = {}


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def add_span_attributes(
    node: BaseLanguageModel | BaseRetriever | BaseTool,
    **kwargs: Any,
) -> None:
    """Adds custom span-level attributes to a specific runnable component's metadata.

    Span attributes are key-value pairs that apply to a specific component (LLM, tool, or retriever)
    and are included in the OpenTelemetry spans created when that component executes. Use this to
    add metadata that describes the component's configuration, purpose, or operational context.

    Unlike session attributes (which apply to all spans in a context), span attributes are scoped
    to individual components. This is useful for:
    - Identifying which model or tool is being used
    - Tagging components by purpose or category
    - Adding version information or deployment metadata
    - Tracking A/B test variants or experimental configurations

    The attributes are stored in the component's metadata dictionary under the key
    '_fiddler_attributes' and will be automatically included in spans when the component executes.
    Attributes persist for the lifetime of the component instance.

    Supported component types:
    - **BaseLanguageModel**: LLM calls (ChatOpenAI, ChatAnthropic, etc.)
    - **BaseRetriever**: Document retrieval operations
    - **BaseTool**: Tool/function calls in agent workflows

    Args:
        node (BaseLanguageModel | BaseRetriever | BaseTool): The LangChain component to annotate
            with custom attributes. The component's metadata will be modified in place. **Required**.
        **kwargs (Any): Arbitrary keyword arguments representing the attributes to add. Each
            key-value pair will be stored as a span attribute. Keys should be strings, and values
            can be any type (though simple types like str, int, bool are recommended for
            observability). **Required** (at least one attribute).

    Returns:
        None

    Examples:
        Tagging an LLM with model information:

        .. code-block:: python

            from langchain_openai import ChatOpenAI
            from fiddler_langgraph.tracing.instrumentation import add_span_attributes

            llm = ChatOpenAI(model="gpt-4")
            add_span_attributes(
                llm,
                model_name="gpt-4",
                provider="openai",
                purpose="summarization"
            )

        Adding version and environment metadata:

        .. code-block:: python

            add_span_attributes(
                llm,
                version="v2.1.0",
                environment="production",
                region="us-west-2"
            )

        Tagging tools in a multi-tool agent:

        .. code-block:: python

            from langchain.tools import Tool

            search_tool = Tool(
                name="search",
                func=search_function,
                description="Search the web"
            )
            add_span_attributes(
                search_tool,
                tool_category="external_api",
                rate_limit="100/min",
                cost_per_call=0.001
            )

        A/B testing different retrievers:

        .. code-block:: python

            from langchain_community.vectorstores import FAISS

            retriever_a = FAISS.from_documents(docs, embeddings).as_retriever()
            add_span_attributes(
                retriever_a,
                variant="semantic_search",
                experiment_id="exp_2024_q1",
                retrieval_strategy="similarity"
            )

            retriever_b = FAISS.from_documents(docs, embeddings).as_retriever(
                search_type="mmr"
            )
            add_span_attributes(
                retriever_b,
                variant="mmr_search",
                experiment_id="exp_2024_q1",
                retrieval_strategy="maximum_marginal_relevance"
            )

        Combining with session attributes:

        .. code-block:: python

            from fiddler_langgraph.tracing.instrumentation import (
                add_session_attributes,
                add_span_attributes,
                set_conversation_id
            )

            # Session-level: applies to all spans
            set_conversation_id("conv_12345")
            add_session_attributes("user_id", "user_789")

            # Span-level: applies only to this LLM's spans
            llm = ChatOpenAI(model="gpt-4-turbo")
            add_span_attributes(
                llm,
                model_tier="premium",
                use_case="customer_support"
            )

    Note:
        - Attributes are stored in the component's `metadata` dictionary, which persists
          for the lifetime of the component instance
        - If the component doesn't have a `metadata` attribute, one will be created
        - Multiple calls to `add_span_attributes` on the same component will merge attributes
        - Later calls with the same key will overwrite previous values
        - This modifies the component in place - no need to reassign the return value
    """
    _set_default_metadata(node)
    metadata = cast(dict[str, Any], node.metadata)
    fiddler_attrs = cast(dict[str, Any], metadata.get(FIDDLER_METADATA_KEY, {}))
    for key, value in kwargs.items():
        fiddler_attrs[key] = value


@validate_call(config=ConfigDict(strict=True))
def set_llm_context(llm: BaseLanguageModel | RunnableBinding, context: str) -> None:
    """Sets additional context information on a language model instance.

    This context provides environmental or operational information that will be
    attached to all spans created for this model. Use this to add relevant metadata
    such as user preferences, session state, or runtime conditions that influenced
    the LLM's behavior. This is valuable for debugging and understanding why the
    model produced specific outputs.

    Supports both `BaseLanguageModel` instances and `RunnableBinding` objects. When a
    `RunnableBinding` is provided, the context is automatically set on the underlying
    bound object (which must be a `BaseLanguageModel`).

    For more information on RunnableBinding, see:
    https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.base.RunnableBinding.html

    Args:
        llm (BaseLanguageModel | RunnableBinding): The language model instance or binding. **Required**.
        context (str): The context string to add. This will be included in span attributes
            as 'gen_ai.llm.context'. **Required**.

    Raises:
        TypeError: If a RunnableBinding is provided but its bound object is not a BaseLanguageModel.

    Examples:
        Basic usage with ChatOpenAI:

        .. code-block:: python

            from langchain_openai import ChatOpenAI
            from fiddler_langgraph.tracing.instrumentation import set_llm_context

            llm = ChatOpenAI(model="gpt-4")
            set_llm_context(llm, "User prefers concise responses")

        With user preferences:

        .. code-block:: python

            set_llm_context(llm, "User language: Spanish, Expertise: Beginner")

        Using with RunnableBinding:

        .. code-block:: python

            bound_llm = llm.bind(temperature=0.7, max_tokens=100)
            set_llm_context(bound_llm, "Creative writing mode with token limits")

        Adding session context:

        .. code-block:: python

            import uuid
            session_id = uuid.uuid4()
            set_llm_context(llm, f"Session: {session_id}, Environment: Production")
    """
    if isinstance(llm, RunnableBinding):
        if not isinstance(llm.bound, BaseLanguageModel):
            raise TypeError(
                'llm must be a BaseLanguageModel or a RunnableBinding of a BaseLanguageModel'
            )
        # RunnableBinding has config attribute (which can store metadata), however these are not passed
        # to the callback handlers. So we need to use the bound object directly.
        _llm = llm.bound
    else:
        _llm = llm

    _set_default_metadata(_llm)

    if _llm.metadata is None:
        _llm.metadata = {}
    fiddler_attrs = cast(dict[str, Any], _llm.metadata.get(FIDDLER_METADATA_KEY, {}))
    fiddler_attrs[FiddlerSpanAttributes.LLM_CONTEXT] = context


class LangGraphInstrumentor(BaseInstrumentor):
    """An OpenTelemetry instrumentor for LangGraph applications.

    This class provides automatic instrumentation for applications built with
    LangGraph. It captures traces from the execution of LangGraph graphs and
    sends them to the Fiddler platform for monitoring and analysis.

    Instrumentation works by monkey-patching LangChain's callback system to inject
    a custom callback handler that captures trace data. Once instrumented, all
    LangGraph operations will automatically generate telemetry data.

    Note: Instrumentation persists for the lifetime of the application unless
    explicitly removed by calling `uninstrument()`. Calling `instrument()` multiple
    times is safe - it will not create duplicate handlers.

    Thread Safety: The instrumentation applies globally to the process and affects
    all threads. In concurrent environments (multi-threading, async), all contexts
    share the same instrumented callback system.

    To use the instrumentor, you first need to create a `FiddlerClient`
    instance. Then, you can create an instance of `LangGraphInstrumentor` and
    call the `instrument()` method.

    Examples:
        Basic usage:

        .. code-block:: python

            from fiddler_langgraph import FiddlerClient
            from fiddler_langgraph.tracing import LangGraphInstrumentor

            client = FiddlerClient(api_key="...", application_id="...", url="https://your-instance.fiddler.ai")
            instrumentor = LangGraphInstrumentor(client=client)
            instrumentor.instrument()

        Removing instrumentation:

        .. code-block:: python

            # Clean up instrumentation when shutting down
            instrumentor.uninstrument()

        Context manager pattern (advanced):

        .. code-block:: python

            with LangGraphInstrumentor(client).instrument():
                # Instrumented operations here
                agent.invoke({"messages": [...]})
            # Automatically uninstrumented after block

    Attributes:
        _client (FiddlerClient): The FiddlerClient instance used for configuration.
        _tracer (_CallbackHandler | None): The callback handler instance for tracing.
        _langgraph_version: The installed LangGraph version.
        _langchain_version: The installed LangChain Core version.
        _fiddler_langgraph_version: The Fiddler LangGraph SDK version.
    """

    def __init__(self, client: FiddlerClient):
        """Initializes the LangGraphInstrumentor.

        Args:
            client (FiddlerClient): The `FiddlerClient` instance. **Required**.

        Raises:
            ImportError: If LangGraph version is incompatible or not installed.
        """
        super().__init__()
        self._client = client
        self._langgraph_version = _get_package_version('langgraph')
        self._langchain_version = _get_package_version('langchain_core')
        self._fiddler_langgraph_version = _get_package_version('fiddler_langgraph')

        self._client.update_resource(
            {
                'lib.langgraph.version': self._langgraph_version.public,
                'lib.langchain_core.version': self._langchain_version.public,
                'lib.fiddler-langgraph.version': self._fiddler_langgraph_version.public,
            }
        )
        self._tracer: _CallbackHandler | None = None
        self._original_callback_manager_init: Callable[..., None] | None = None

        # Check LangGraph version compatibility - we don't add this to dependencies
        # because we leave it to the user to install the correct version of LangGraph
        # We will check if the user installed version is compatible with the version of fiddler-langgraph
        _check_langgraph_version(self._langgraph_version)

    def instrumentation_dependencies(self) -> Collection[str]:
        """Returns the package dependencies required for this instrumentor.

        Returns:
            Collection[str]: A collection of package dependency strings.
        """
        return ('langchain_core >= 0.1.0',)

    def _instrument(self, **kwargs: Any) -> None:
        """Instruments LangGraph by monkey-patching `BaseCallbackManager`.

        This method injects a custom callback handler into LangGraph's callback
        system to capture trace data. This is done by wrapping the `__init__`
        method of `BaseCallbackManager` to inject a `_CallbackHandler`.

        Raises:
            ValueError: If the tracer is not initialized in the FiddlerClient.
        """
        import langchain_core

        tracer = self._client.get_tracer()
        if tracer is None:
            raise ValueError('Context tracer is not initialized')

        self._tracer = _CallbackHandler(tracer)
        self._original_callback_manager_init = langchain_core.callbacks.BaseCallbackManager.__init__
        wrap_function_wrapper(
            module='langchain_core.callbacks',
            name='BaseCallbackManager.__init__',
            wrapper=_BaseCallbackManagerInit(self._tracer),
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        """Removes the instrumentation from LangGraph.

        This is done by restoring the original `__init__` method on the
        `BaseCallbackManager` class.
        """
        import langchain_core

        if self._original_callback_manager_init is not None:
            setattr(  # noqa: B010
                langchain_core.callbacks.BaseCallbackManager,
                '__init__',
                self._original_callback_manager_init,
            )
        self._original_callback_manager_init = None
        self._tracer = None


class _BaseCallbackManagerInit:
    """A wrapper class for `BaseCallbackManager.__init__` to inject Fiddler's callback handler."""

    __slots__ = ('_callback_handler',)

    def __init__(self, callback_handler: _CallbackHandler):
        """Initializes the wrapper.

        Args:
            callback_handler (_CallbackHandler): The Fiddler callback handler instance
                to be injected into the callback manager.
        """
        self._callback_handler = callback_handler

    def __call__(
        self,
        wrapped: Callable[..., None],
        instance: 'BaseCallbackManager',
        args: Any,
        kwargs: Any,
    ) -> None:
        """Calls the original `__init__` and then adds the Fiddler handler.

        It also ensures that the handler is not added multiple times if it
        already exists in the list of inheritable handlers.
        """
        wrapped(*args, **kwargs)
        for handler in instance.inheritable_handlers:
            # Handlers may be copied when new managers are created, so we
            # don't want to keep adding. E.g. see the following location.
            # https://github.com/langchain-ai/langchain/blob/5c2538b9f7fb64afed2a918b621d9d8681c7ae32/libs/core/langchain_core/callbacks/manager.py#L1876
            if isinstance(handler, type(self._callback_handler)):
                break
        else:
            instance.add_handler(self._callback_handler, True)
