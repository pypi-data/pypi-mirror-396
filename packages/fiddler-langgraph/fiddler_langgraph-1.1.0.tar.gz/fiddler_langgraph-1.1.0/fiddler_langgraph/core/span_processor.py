from opentelemetry import context
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import Span

from fiddler_langgraph.core.attributes import (
    _CONVERSATION_ID,
    _CUSTOM_ATTRIBUTES,
    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE,
    FiddlerSpanAttributes,
)


class FiddlerSpanProcessor(SpanProcessor):
    def on_start(self, span: Span, parent_context: context.Context | None = None):
        # inject custom attributes
        try:
            custom_attributes = _CUSTOM_ATTRIBUTES.get().copy()
        except LookupError:
            # LookupError is raised if the contextvar is not set
            custom_attributes = {}
        if custom_attributes:
            for key, value in custom_attributes.items():
                # prefix the key with fiddler.session.
                # fdl_key = f'fiddler.session.{key}'
                fdl_key = FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.format(key=key)
                span.set_attribute(fdl_key, value)

        # inject session id
        session_id = _CONVERSATION_ID.get()
        if session_id:
            span.set_attribute(FiddlerSpanAttributes.CONVERSATION_ID, session_id)
